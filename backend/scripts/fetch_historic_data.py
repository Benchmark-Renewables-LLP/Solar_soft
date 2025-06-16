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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config.settings import DATABASE_URL, COMPANY_KEY, BATCH_SIZE
from shinemonitor_api import ShinemonitorAPI
from soliscloud_api import SolisCloudAPI

# Load environment variables
load_dotenv()

# Configure logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('fetch_historic_data.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

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
        return True
    try:
        val = float(value)
        return min_val <= val <= max_val
    except (ValueError, TypeError):
        logger.warning(f"Invalid value for {param_name}: {value}")
        return False

def load_customers_to_db(conn, credentials):
    """Load customers into the customers table based on unique customer_ids from credentials."""
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
        with open(csv_file, 'r') as f:
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
                api_key = credential.get('api_key', '') if api_provider == 'soliscloud' else ''
                api_secret = credential.get('api_secret', '') if api_provider == 'soliscloud' else ''
                cur.execute("""
                    INSERT INTO api_credentials (
                        user_id, customer_id, api_provider, username, password, api_key, api_secret,
                        created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                """, (
                    credential['user_id'], credential['customer_id'], api_provider,
                    credential['username'], credential['password'], api_key, api_secret,
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

def insert_data_to_db(conn, data, device_sn):
    """Insert historical data into the device_data_historical table."""
    try:
        with conn.cursor() as cur:
            for entry in data:
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

                valid = True
                for j in range(1, 13):
                    if not validate_parameter(entry.get(f"pv{j:02d}_voltage"), f"pv{j:02d}_voltage", 0, 1000):
                        valid = False
                    if not validate_parameter(entry.get(f"pv{j:02d}_current"), f"pv{j:02d}_current", 0, 50):
                        valid = False
                for phase in ['r', 's', 't']:
                    if not validate_parameter(entry.get(f"{phase}_voltage"), f"{phase}_voltage", 0, 300):
                        valid = False
                if not validate_parameter(entry.get("total_power"), "total_power", 0, 100000):
                    valid = False
                if not validate_parameter(entry.get("energy_today"), "energy_today", 0, 100):
                    valid = False
                if not validate_parameter(entry.get("pr"), "pr", 0, 100):
                    valid = False

                if not valid:
                    logger.warning(f"Skipping entry for device {device_sn} at {entry_timestamp} due to validation failure")
                    continue

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
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (device_sn, timestamp) DO NOTHING
                """, (
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
                ))

        conn.commit()
        logger.info(f"Inserted {len(data)} records into device_data_historical for device {device_sn}.")
    except Exception as e:
        logger.error(f"Failed to insert data into database for device {device_sn}: {e}")
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
                fetch_plants = api_client.get_all_stations
                fetch_devices = api_client.get_all_inverters
                fetch_data = api_client.get_inverter_historical_data
                plant_id_key = 'station_id'
            elif api_provider == 'solarman':
                continue
            else:
                api_client = ShinemonitorAPI(COMPANY_KEY) if COMPANY_KEY else ShinemonitorAPI()
                fetch_plants = api_client.fetch_plant_list
                fetch_devices = api_client.fetch_plant_devices
                fetch_data = api_client.fetch_historical_data
                plant_id_key = 'plant_id'

            try:
                plants = fetch_plants(user_id, username, password)
                if not plants:
                    logger.warning(f"No plants found for user {user_id}, skipping.")
                    continue
            except Exception as e:
                logger.error(f"Failed to fetch plants for user {user_id}: {e}")
                continue

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for plant in plants:
                    try:
                        cur.execute("""
                            INSERT INTO plants (plant_id, customer_id, plant_name, capacity, install_date, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (plant_id) DO NOTHING
                        """, (
                            plant[plant_id_key], customer_id, plant.get('plant_name', 'Unknown'),
                            plant.get('capacity', 0.0), plant.get('install_date', '1970-01-01'),
                            datetime.now(), datetime.now()
                        ))
                        logger.info(f"Inserted plant with ID {plant[plant_id_key]} for customer {customer_id}")
                    except Exception as e:
                        logger.error(f"Failed to insert plant {plant[plant_id_key]}: {e}")
                        continue

                for plant in plants:
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
                            cur.execute("""
                                INSERT INTO devices (device_sn, plant_id, inverter_model, panel_model, pv_count, string_count, first_install_date, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (device_sn) DO NOTHING
                            """, (
                                device['sn'], plant_id, device.get('inverter_model', 'Unknown'),
                                device.get('panel_model', 'Unknown'), device.get('pv_count', 0),
                                device.get('string_count', 0), device.get('first_install_date', '1970-01-01'),
                                datetime.now(), datetime.now()
                            ))
                            logger.info(f"Inserted device with SN {device['sn']} for plant {plant_id}")
                        except Exception as e:
                            logger.error(f"Failed to insert device {device.get('sn', 'unknown')}: {e}")
                            continue

                        try:
                            end_date = datetime.now().strftime('%Y-%m-%d')
                            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

                            @retry(
                                stop=stop_after_attempt(3),
                                wait=wait_exponential(multiplier=1, min=2, max=10),
                                retry=retry_if_exception_type(requests_exceptions.RequestException)
                            )
                            def fetch_with_retry():
                                return fetch_data(user_id, username, password, device, start_date, end_date)

                            historical_data = fetch_with_retry()
                            if not historical_data:
                                logger.warning(f"No historical data for device {device['sn']}")
                                continue
                            logger.info(f"Received {len(historical_data)} historical data entries for device {device['sn']}")

                            insert_data_to_db(conn, historical_data, device['sn'])
                        except Exception as e:
                            logger.error(f"Failed to fetch or insert data for device {device['sn']}: {e}")
                            continue

        conn.commit()
        logger.info("Completed fetch_historic_data script.")
    except Exception as e:
        logger.error(f"Error in fetch_historic_data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_historic_data()