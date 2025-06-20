# Install required libraries:
# `pip install requests psycopg2-binary tenacity python-dotenv`

import logging
import os
import sys
import time
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from requests import exceptions as requests_exceptions
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv
import hashlib
import requests

# Ensure console encoding is UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception as e:
        print(f"Failed to reconfigure stdout encoding: {e}", file=sys.stderr)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.settings import DATABASE_URL, COMPANY_KEY, BATCH_SIZE
from shinemonitor_api import ShinemonitorAPI
from soliscloud_api import SolisCloudAPI
from solarman_api import SolarmanAPI, json_to_csv

# Custom StreamHandler to handle Unicode characters in console output
class UnicodeSafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            msg = self.format(record).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            stream.write(msg + self.terminator)
            self.flush()

# Custom RotatingFileHandler with line buffering for real-time logging
class RealTimeRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay)
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        self.stream = open(self.baseFilename, self.mode, buffering=1, encoding=self.encoding)

# Configure logging with rotation and UTF-8 encoding
try:
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'fetch_historic_data.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RealTimeRotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'),
            UnicodeSafeStreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized with real-time writes. Log file: {log_file}")
except Exception as e:
    print(f"Failed to configure logging: {e}", file=sys.stderr)
    raise

# Load environment variables
load_dotenv()
SAVE_CSV = os.getenv('SAVE_CSV', 'False').lower() == 'true'

def convert_timestamp_to_date(timestamp, default='1970-01-01'):
    """Convert a Unix timestamp (in milliseconds or seconds) to YYYY-MM-DD format."""
    try:
        if isinstance(timestamp, (int, float)):
            if len(str(int(timestamp))) > 10:  # Milliseconds
                timestamp = timestamp / 1000
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        return timestamp
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to convert timestamp {timestamp}: {e}. Using default: {default}")
        return default

def get_db_connection():
    """Establish a database connection."""
    try:
        conn = connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def validate_parameter(value, param_name, min_val, max_val):
    """Validate a parameter value."""
    if value is None:
        logger.warning(f"Missing value for {param_name}")
        return False
    try:
        val = float(value)
        return min_val <= val <= max_val
    except (ValueError, TypeError):
        logger.warning(f"Invalid value for {param_name}: {value}")
        return False

def load_customers_to_db(conn, credentials):
    """Load customers into the customers table."""
    try:
        customer_ids = set(credential.get('customer_id', 'default_customer') for credential in credentials)
        if not customer_ids:
            logger.warning("No customer_ids found, using default customer.")
            customer_ids = {'default_customer'}

        with conn.cursor() as cur:
            for customer_id in customer_ids:
                cur.execute("""
                    INSERT INTO customers (
                        customer_id, customer_name, email, phone, address, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (customer_id) DO NOTHING
                """, (
                    customer_id, customer_id, None, None, None, datetime.now(), datetime.now()
                ))
        conn.commit()
        logger.info(f"Inserted {len(customer_ids)} customers into the customers table.")
    except Exception as e:
        logger.error(f"Failed to load customers into database: {e}")
        conn.rollback()
        raise

def load_credentials_to_db(conn, csv_file):
    """Load API credentials from CSV and insert into the api_credentials table."""
    credentials = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            header = f.readline().strip().split(',')
            for line in f:
                values = line.strip().split(',')
                credential = dict(zip(header, values))
                if 'customer_id' not in credential:
                    credential['customer_id'] = 'default_customer'
                credentials.append(credential)

        load_customers_to_db(conn, credentials)

        with conn.cursor() as cur:
            for credential in credentials:
                api_provider = credential.get('api_provider', 'shinemonitor')
                api_key = credential.get('api_key', '') if api_provider in ('soliscloud', 'solarman') else ''
                api_secret = credential.get('api_secret', '') if api_provider in ('soliscloud', 'solarman') else ''
                cur.execute("""
                    INSERT INTO api_credentials (
                        user_id, customer_id, api_provider, username, password, api_key, api_secret,
                        created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                """, (
                    credential['user_id'], credential['customer_id'], api_provider,
                    credential.get('username', ''), credential.get('password', ''),
                    api_key, api_secret,
                    datetime.now(), datetime.now()
                ))
        conn.commit()
        logger.info(f"Inserted {len(credentials)} credentials into the api_credentials table.")
        return credentials
    except Exception as e:
        logger.error(f"Failed to load credentials from CSV: {e}")
        raise

def load_credentials_from_db(conn):
    """Load API credentials from the database."""
    credentials = []
    try:
        if conn.closed:
            logger.error("Database connection is closed.")
            raise Exception("Database connection is closed.")

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            logger.debug("Executing query to fetch credentials...")
            cur.execute("""
                SELECT user_id, customer_id, api_provider, username, password, api_key, api_secret
                FROM api_credentials;
            """)
            credentials = cur.fetchall()
            logger.info(f"Loaded {len(credentials)} credentials from the database.")
            for credential in credentials:
                logger.debug(f"Credential: {credential['user_id']}, Provider: {credential['api_provider']}, Customer: {credential['customer_id']}")
        return credentials
    except Exception as e:
        logger.error(f"Failed to load credentials from database: {e}")
        raise

def normalize_data_entry(entry):
    """Normalize data entry to ensure all required fields are present."""
    default_entry = {
        'pv01_voltage': 0, 'pv01_current': 0, 'pv02_voltage': 0, 'pv02_current': 0,
        'pv03_voltage': 0, 'pv03_current': 0, 'pv04_voltage': 0, 'pv04_current': 0,
        'pv05_voltage': 0, 'pv05_current': 0, 'pv06_voltage': 0, 'pv06_current': 0,
        'pv07_voltage': 0, 'pv07_current': 0, 'pv08_voltage': 0, 'pv08_current': 0,
        'pv09_voltage': 0, 'pv09_current': 0, 'pv10_voltage': 0, 'pv10_current': 0,
        'pv11_voltage': 0, 'pv11_current': 0, 'pv12_voltage': 0, 'pv12_current': 0,
        'r_voltage': 0, 's_voltage': 0, 't_voltage': 0,
        'r_current': 0, 's_current': 0, 't_current': 0,
        'rs_voltage': 0, 'st_voltage': 0, 'tr_voltage': 0,
        'frequency': 0, 'total_power': 0, 'reactive_power': 0,
        'energy_today': 0, 'cuf': 0, 'pr': 0, 'state': 'unknown'
    }
    default_entry.update(entry)
    return default_entry

def flatten_data(data, depth=0, max_depth=10):
    """Recursively flatten nested lists into a single list of dictionaries."""
    flattened = []
    if depth > max_depth:
        logger.error(f"Maximum recursion depth exceeded in flatten_data: {data}")
        return flattened
    for item in data:
        if isinstance(item, list):
            logger.debug(f"Flattening nested list at depth {depth}: {item}")
            flattened.extend(flatten_data(item, depth + 1, max_depth))
        elif isinstance(item, dict):
            flattened.append(item)
        else:
            logger.warning(f"Unexpected item type in data for device: {type(item)}, item: {item}")
    return flattened

def insert_data_to_db(conn, data, device_sn):
    """Insert historical data into the device_data_historical table."""
    try:
        with conn.cursor() as cur:
            flattened_data = flatten_data(data)
            logger.debug(f"Flattened data for device {device_sn} ({len(flattened_data)} entries): {flattened_data}")

            if not flattened_data:
                logger.warning(f"No valid data to insert for device {device_sn}")
                return

            inserted_count = 0
            for entry in flattened_data:
                if not isinstance(entry, dict):
                    logger.error(f"Invalid entry type for device {device_sn}: {type(entry)}, entry: {entry}")
                    continue
                ts_str = entry.get('timestamp')
                if not ts_str:
                    logger.warning(f"Missing timestamp for device {device_sn}: {entry}")
                    continue
                ts_str = ts_str.strip()
                try:
                    ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                    entry_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    logger.warning(f"Invalid timestamp format for device {device_sn}: {ts_str}")
                    continue

                entry = normalize_data_entry(entry)
                logger.debug(f"Inserting data for device {device_sn} at {entry_timestamp}: {entry}")

                valid = True
                for j in range(1, 13):
                    if not validate_parameter(entry.get(f"pv{j:02d}_voltage"), f"pv{j:02d}_voltage", 0, 1000):
                        valid = False
                    if not validate_parameter(entry.get(f"pv{j:02d}_current"), f"pv{j:02d}_current", 0, 50):
                        valid = False
                for phase in ['r', 's', 't']:
                    if not validate_parameter(entry.get(f"{phase}_voltage"), f"{phase}_voltage", 0, 300):
                        valid = False
                    if not validate_parameter(entry.get(f"{phase}_current"), f"{phase}_current", 0, 100):
                        valid = False
                if not validate_parameter(entry.get("total_power"), "total_power", 0, 100000):
                    valid = False
                if not validate_parameter(entry.get("energy_today"), "energy_today", 0, 1000):
                    valid = False
                if not validate_parameter(entry.get("pr"), "pr", 0, 100):
                    valid = False

                if not valid:
                    logger.warning(f"Skipping entry for device {device_sn} at {entry_timestamp} due to validation failure")
                    continue

                data_tuple = (
                    device_sn, entry_timestamp,
                    entry.get('pv01_voltage'), entry.get('pv01_current'),
                    entry.get('pv02_voltage'), entry.get('pv02_current'),
                    entry.get('pv03_voltage'), entry.get('pv03_current'),
                    entry.get('pv04_voltage'), entry.get('pv04_current'),
                    entry.get('pv05_voltage'), entry.get('pv05_current'),
                    entry.get('pv06_voltage'), entry.get('pv06_current'),
                    entry.get('pv07_voltage'), entry.get('pv07_current'),
                    entry.get('pv08_voltage'), entry.get('pv08_current'),
                    entry.get('pv09_voltage'), entry.get('pv09_current'),
                    entry.get('pv10_voltage'), entry.get('pv10_current'),
                    entry.get('pv11_voltage'), entry.get('pv11_current'),
                    entry.get('pv12_voltage'), entry.get('pv12_current'),
                    entry.get('r_voltage'), entry.get('s_voltage'), entry.get('t_voltage'),
                    entry.get('r_current'), entry.get('s_current'), entry.get('t_current'),
                    entry.get('rs_voltage'), entry.get('st_voltage'), entry.get('tr_voltage'),
                    entry.get('frequency'), entry.get('total_power'), entry.get('reactive_power'),
                    entry.get('energy_today'), entry.get('cuf'), entry.get('pr'), entry.get('state'),
                    datetime.now(), datetime.now()
                )
                logger.debug(f"Data tuple for device {device_sn}: {data_tuple}")

                cur.execute("""
                    INSERT INTO device_data_historical (
                        device_sn, timestamp, pv01_voltage, pv01_current, pv02_voltage, pv02_current,
                        pv03_voltage, pv03_current, pv04_voltage, pv04_current, pv05_voltage, pv05_current,
                        pv06_voltage, pv06_current, pv07_voltage, pv07_current, pv08_voltage, pv08_current,
                        pv09_voltage, pv09_current, pv10_voltage, pv10_current, pv11_voltage, pv11_current,
                        pv12_voltage, pv12_current, r_voltage, s_voltage, t_voltage,
                        r_current, s_current, t_current, rs_voltage, st_voltage, tr_voltage,
                        frequency, total_power, reactive_power, energy_today, cuf, pr, state,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (device_sn, timestamp) DO NOTHING
                """, data_tuple)
                inserted_count += 1

            conn.commit()
            logger.info(f"Inserted {inserted_count} records into device_data_historical for device {device_sn}.")
    except Exception as e:
        logger.error(f"Failed to insert data into database for device {device_sn}: {e}")
        logger.error(f"SQL Query: {cur.query.decode() if 'cur' in locals() and cur.query else 'N/A'}")
        logger.error(f"Data tuple: {data_tuple if 'data_tuple' in locals() else 'N/A'}")
        conn.rollback()
        raise

def fetch_historic_data():
    logger.info("Starting fetch_historic_data script...")
    conn = get_db_connection()
    try:
        csv_file = "backend/data/users.csv"
        load_credentials_to_db(conn, csv_file)

        credentials = load_credentials_from_db(conn)
        if not credentials:
            logger.error("No credentials found, exiting.")
            return

        logger.info(f"Processing {len(credentials)} credentials")
        for credential in credentials:
            user_id = credential['user_id']
            customer_id = credential['customer_id']
            username = credential['username']
            password = credential['password']
            api_provider = credential.get('api_provider', 'shinemonitor')
            api_key = credential.get('api_key')
            api_secret = credential.get('api_secret')

            if api_provider == 'soliscloud':
                if not api_key or not api_secret:
                    logger.warning(f"No API key/secret for SolisCloud user {user_id}, skipping.")
                    continue
                api_client = SolisCloudAPI(api_key, api_secret)
                logger.debug(f"Using SolisCloud API for user {user_id}")
                fetch_plants = api_client.get_all_stations
                fetch_devices = api_client.get_all_inverters
                fetch_historical = api_client.get_inverter_historical_data
                fetch_real_time = api_client.get_inverter_real_time_data
                plant_id_key = 'station_id'
            elif api_provider == 'solarman':
                if not api_key or not api_secret:
                    logger.warning(f"No API key/secret for Solarman user {user_id}, skipping.")
                    continue
                api_client = SolarmanAPI(username, password, api_key, api_secret, base_url=os.getenv('SOLARMAN_BASE_URL', 'https://globalapi.solarmanpv.com'))
                logger.debug(f"Using Solarman API for user {user_id}")
                fetch_plants = api_client.get_plant_list
                fetch_devices = lambda u, un, pw, pid: api_client.get_all_devices(pid, device_type="INVERTER")
                fetch_historical = api_client.get_historical_data
                fetch_real_time = api_client.get_current_data
                plant_id_key = 'plant_id'
            else:  # Default to Shinemonitor
                api_client = ShinemonitorAPI(COMPANY_KEY) if COMPANY_KEY else ShinemonitorAPI()
                fetch_plants = api_client.fetch_plant_list
                fetch_devices = api_client.fetch_plant_devices
                fetch_historical = api_client.fetch_historical_data
                fetch_real_time = lambda u, un, pw, d: api_client.fetch_historical_data(
                    u, un, pw, d, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')
                )
                plant_id_key = 'plant_id'

            try:
                plants = fetch_plants(user_id, username, password)
                if not plants:
                    logger.warning(f"No plants found for user {user_id}, skipping.")
                    continue
            except Exception as e:
                logger.error(f"Failed to fetch plants for user {user_id}: {e}")
                continue

            for plant in plants:
                try:
                    install_date = convert_timestamp_to_date(plant.get('install_date', '1970-01-01'))
                    plant['install_date'] = install_date

                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("""
                            INSERT INTO plants (plant_id, customer_id, plant_name, capacity, install_date, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (plant_id) DO NOTHING
                            RETURNING plant_id
                        """, (
                            plant[plant_id_key], customer_id, plant.get('plant_name', 'Unknown'),
                            float(plant.get('capacity', 0.0)), install_date,
                            datetime.now(), datetime.now()
                        ))
                        result = cur.fetchone()
                        if result:
                            logger.info(f"Inserted plant with ID {plant[plant_id_key]} for customer {customer_id}")
                        else:
                            logger.debug(f"Plant {plant[plant_id_key]} already exists, skipping insertion.")
                    conn.commit()
                except Exception as e:
                    logger.error(f"Failed to insert plant {plant.get(plant_id_key, 'unknown')}: {e}")
                    conn.rollback()
                    continue

                plant_id = plant[plant_id_key]
                try:
                    devices = fetch_devices(user_id, username, password, plant_id)
                    if not devices:
                        logger.warning(f"No devices found for plant {plant_id}")
                        continue
                    logger.info(f"Found {len(devices)} devices for plant {plant_id}")
                except Exception as e:
                    logger.error(f"Failed to fetch devices for plant {plant_id}: {e}")
                    continue

                for device in devices:
                    try:
                        first_install_date = convert_timestamp_to_date(device.get('first_install_date', '1970-01-01'))
                        device['first_install_date'] = first_install_date

                        with conn.cursor(cursor_factory=RealDictCursor) as cur:
                            cur.execute("""
                                INSERT INTO devices (device_sn, plant_id, inverter_model, panel_model, pv_count, string_count, first_install_date, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (device_sn) DO NOTHING
                                RETURNING device_sn
                            """, (
                                device['sn'], plant_id, device.get('inverter_model', 'Unknown'),
                                device.get('panel_model', 'Unknown'), int(device.get('pv_count', 0)),
                                int(device.get('string_count', 0)), first_install_date,
                                datetime.now(), datetime.now()
                            ))
                            result = cur.fetchone()
                            if result:
                                logger.info(f"Inserted device with SN {device['sn']} for plant {plant_id}")
                            else:
                                logger.debug(f"Device {device['sn']} already exists, skipping insertion.")
                        conn.commit()
                    except Exception as e:
                        logger.error(f"Failed to insert device {device.get('sn', 'unknown')}: {e}")
                        conn.rollback()
                        continue

                    try:
                        @retry(
                            stop=stop_after_attempt(3),
                            wait=wait_exponential(multiplier=1, min=2, max=10),
                            retry=retry_if_exception_type(requests_exceptions.RequestException)
                        )
                        def fetch_real_time_with_retry():
                            return fetch_real_time(user_id, username, password, device)

                        real_time_response = fetch_real_time_with_retry()
                        logger.debug(f"Raw real-time response for device {device['sn']}: {real_time_response}")
                        if real_time_response:
                            logger.info(f"Received {len(real_time_response)} real-time data entries for device {device['sn']}")
                            insert_data_to_db(conn, real_time_response, device['sn'])
                            if SAVE_CSV:
                                csv_data = json_to_csv({"deviceSn": device['sn'], "deviceType": "INVERTER", "dataList": real_time_response})
                                csv_filename = f"current_data_{device['sn']}.csv"
                                with open(os.path.join(log_dir, csv_filename), 'w', newline='', encoding='utf-8') as f:
                                    f.write(csv_data)
                                logger.info(f"Saved current data to {csv_filename}")
                        else:
                            logger.warning(f"No real-time data for device {device['sn']}")

                        end_date = datetime.now().strftime('%Y-%m-%d')
                        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')

                        @retry(
                            stop=stop_after_attempt(3),
                            wait=wait_exponential(multiplier=1, min=2, max=10),
                            retry=retry_if_exception_type(requests_exceptions.RequestException)
                        )
                        def fetch_historical_with_retry():
                            return fetch_historical(user_id, username, password, device, start_date, end_date)

                        historical_data = fetch_historical_with_retry()
                        logger.debug(f"Raw historical data for device {device['sn']} ({len(historical_data)} entries): {historical_data}")
                        if not historical_data:
                            logger.warning(f"No historical data for device {device['sn']}")
                            continue
                        flattened_historical_data = flatten_data(historical_data)
                        logger.debug(f"Flattened historical data for device {device['sn']} ({len(flattened_historical_data)} entries): {flattened_historical_data}")
                        logger.info(f"Received {len(flattened_historical_data)} historical data entries for device {device['sn']}")
                        insert_data_to_db(conn, flattened_historical_data, device['sn'])
                        if SAVE_CSV:
                            csv_data = json_to_csv({"deviceSn": device['sn'], "deviceType": "INVERTER", "paramDataList": [{"collectTime": d['timestamp'], "dataList": [{"key": k, "value": v} for k, v in d.items() if k in ['total_power', 'pv01_voltage', 'pv01_current', 'state', 'energy_today']]} for d in flattened_historical_data]})
                            csv_filename = f"historical_data_{device['sn']}.csv"
                            with open(os.path.join(log_dir, csv_filename), 'w', newline='', encoding='utf-8') as f:
                                f.write(csv_data)
                            logger.info(f"Saved historical data to {csv_filename}")
                    except Exception as e:
                        logger.error(f"Failed to fetch or insert data for device {device['sn']}: {e}")
                        conn.rollback()
                        continue

        logger.info("Completed fetch_historic_data script.")
    except Exception as e:
        logger.error(f"Error in fetch_historic_data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_historic_data()