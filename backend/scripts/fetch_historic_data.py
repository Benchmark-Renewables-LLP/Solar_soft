import logging
import os
import sys
import time
 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from requests import exceptions as requests_exceptions
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

from config.settings import DATABASE_URL, COMPANY_KEY, ENCRYPTION_KEY, BATCH_SIZE
from shinemonitor_api import ShinemonitorAPI
from soliscloud_api import SolisCloudAPI

# Load environment variables (if needed for other settings)
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

def load_users_to_db(conn, csv_file):
    """Load users from CSV and insert into the users table."""
    users = []
    try:
        with open(csv_file, 'r') as f:
            # Skip header
            header = f.readline().strip().split(',')
            for line in f:
                values = line.strip().split(',')
                user = dict(zip(header, values))
                users.append(user)

        # Verify ENCRYPTION_KEY is set
        if not ENCRYPTION_KEY:
            logger.error("ENCRYPTION_KEY is not set.")
            raise ValueError("ENCRYPTION_KEY is not set.")

        with conn.cursor() as cur:
            for user in users:
                # Default api_provider to 'shinemonitor' if not specified
                api_provider = user.get('api_provider', 'shinemonitor')
                password = user.get('password', '')
                api_key = user.get('api_key', '') if api_provider == 'soliscloud' else ''
                api_secret = user.get('api_secret', '') if api_provider == 'soliscloud' else ''

                cur.execute("""
                    INSERT INTO users (
                        user_id, username, password_encrypted, api_provider,
                        api_key_encrypted, api_secret_encrypted, created_at, updated_at
                    )
                    VALUES (%s, %s, pgp_sym_encrypt(%s, %s), %s, 
                            pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                """, (
                    user['user_id'], user['username'], password, ENCRYPTION_KEY, api_provider,
                    api_key, ENCRYPTION_KEY, api_secret, ENCRYPTION_KEY,
                    datetime.now(), datetime.now()
                ))
        conn.commit()
        logger.info(f"Inserted {len(users)} users into the users table.")
        return users
    except Exception as e:
        logger.error(f"Failed to load users from CSV: {e}")
        raise

def load_users_from_db(conn):
    """Load users from the database."""
    users = []
    try:
        # Verify the connection is active
        if conn.closed:
            logger.error("Database connection is closed.")
            raise Exception("Database connection is closed.")

        # Verify ENCRYPTION_KEY is set
        if not ENCRYPTION_KEY:
            logger.error("ENCRYPTION_KEY is not set.")
            raise ValueError("ENCRYPTION_KEY is not set.")

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            logger.debug("Executing query to fetch users...")
            cur.execute("""
                SELECT user_id, username, 
                       pgp_sym_decrypt(password_encrypted, %s) as password,
                       api_provider,
                       pgp_sym_decrypt(api_key_encrypted, %s) as api_key,
                       pgp_sym_decrypt(api_secret_encrypted, %s) as api_secret
                FROM users;
            """, (ENCRYPTION_KEY, ENCRYPTION_KEY, ENCRYPTION_KEY))
            users = cur.fetchall()
            logger.info(f"Loaded {len(users)} users from the database.")
            for user in users:
                logger.debug(f"User: {user['user_id']}, Provider: {user['api_provider']}")
        return users
    except Exception as e:
        logger.error(f"Failed to load users from database: {e}")
        if isinstance(e, Exception) and "decryption" in str(e).lower():
            logger.error("Decryption failure: Check ENCRYPTION_KEY or encrypted data in the users table.")
        raise

def insert_data_to_db(conn, data):
    """Insert data into the device_data table."""
    try:
        with conn.cursor() as cur:
            for entry in data:
                # Clean and parse timestamp
                ts_str = entry.get('timestamp')
                if not ts_str:
                    logger.warning(f"Missing timestamp for device {entry.get('device_id', 'unknown')}: {entry}")
                    continue
                ts_str = ts_str.strip()
                try:
                    ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                    entry_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    logger.warning(f"Invalid timestamp format for device {entry.get('device_id', 'unknown')}: {ts_str}")
                    continue

                # Validate parameters
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
                    logger.warning(f"Skipping entry for device {entry.get('device_id', 'unknown')} at {entry_timestamp} due to validation failure")
                    continue

                # Insert into device_data
                cur.execute("""
                    INSERT INTO device_data (
                        device_sn, timestamp, pv01_voltage, pv01_current, pv02_voltage, pv02_current,
                        pv03_voltage, pv03_current, pv04_voltage, pv04_current, pv05_voltage, pv05_current,
                        pv06_voltage, pv06_current, pv07_voltage, pv07_current, pv08_voltage, pv08_current,
                        pv09_voltage, pv09_current, pv10_voltage, pv10_current, pv11_voltage, pv11_current,
                        pv12_voltage, pv12_current, r_voltage, s_voltage, t_voltage,
                        r_current, s_current, t_current, total_power, energy_today, pr, state
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (device_sn, timestamp) DO NOTHING
                """, (
                    entry.get('device_id'), entry_timestamp, entry.get('pv01_voltage'), entry.get('pv01_current'),
                    entry.get('pv02_voltage'), entry.get('pv02_current'), entry.get('pv03_voltage'), entry.get('pv03_current'),
                    entry.get('pv04_voltage'), entry.get('pv04_current'), entry.get('pv05_voltage'), entry.get('pv05_current'),
                    entry.get('pv06_voltage'), entry.get('pv06_current'), entry.get('pv07_voltage'), entry.get('pv07_current'),
                    entry.get('pv08_voltage'), entry.get('pv08_current'), entry.get('pv09_voltage'), entry.get('pv09_current'),
                    entry.get('pv10_voltage'), entry.get('pv10_current'), entry.get('pv11_voltage'), entry.get('pv11_current'),
                    entry.get('pv12_voltage'), entry.get('pv12_current'), entry.get('r_voltage'), entry.get('s_voltage'), entry.get('t_voltage'),
                    entry.get('r_current'), entry.get('s_current'), entry.get('t_current'), entry.get('total_power'),
                    entry.get('energy_today'), entry.get('pr'), entry.get('state')
                ))

                # Insert audit log
                cur.execute("""
                    INSERT INTO audit_logs (table_name, operation, record_id, changed_by, changed_at, new_value)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    'device_data', 'INSERT', f"{entry.get('device_id')}_{entry_timestamp}", 'system',
                    datetime.now(), {'device_sn': entry.get('device_id'), 'timestamp': entry_timestamp}
                ))

        conn.commit()
        logger.info(f"Inserted {len(data)} records into device_data.")
    except Exception as e:
        logger.error(f"Failed to insert data into database: {e}")
        conn.rollback()
        raise

def fetch_historic_data():
    logger.info("Starting fetch_historic_data script...")
    conn = get_db_connection()
    try:
        # Load users from CSV into the database
        csv_file = "backend/data/users.csv"  # Adjust the path as needed
        load_users_to_db(conn, csv_file)

        # Load users from database
        users = load_users_from_db(conn)
        if not users:
            logger.error("No users found, exiting.")
            return

        logger.info(f"Processing {len(users)} users")
        for user in users:
            user_id = user['user_id']
            username = user['username']
            password = user['password']
            api_provider = user.get('api_provider', 'shinemonitor')
            api_key = user.get('api_key')
            api_secret = user.get('api_secret')

            # Instantiate the appropriate API client
            if api_provider == 'soliscloud':
                if not api_key or not api_secret:
                    logger.warning(f"No API key/secret for SolisCloud user {user_id}, skipping.")
                    continue
                api_client = SolisCloudAPI(api_key, api_secret)
                fetch_plants = api_client.fetch_station_list
                fetch_devices = api_client.fetch_station_inverters
                fetch_data = api_client.fetch_historical_data
                plant_id_key = 'id'
            elif api_provider == 'solarman':
                # ... (Solarman logic, to be updated later)
                continue
            else:  # Shinemonitor
                api_client = ShinemonitorAPI(COMPANY_KEY) if COMPANY_KEY else ShinemonitorAPI()
                fetch_plants = api_client.fetch_plant_list
                fetch_devices = api_client.fetch_plant_devices
                fetch_data = api_client.fetch_historical_data
                plant_id_key = 'plant_id'

            # Fetch plants (stations)
            try:
                plants = fetch_plants(user_id, username, password)
                if not plants:
                    logger.warning(f"No plants found for user {user_id}, skipping.")
                    continue
            except Exception as e:
                logger.error(f"Failed to fetch plants for user {user_id}: {e}")
                continue

            # Process each plant and its devices
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Insert plants
                for plant in plants:
                    try:
                        cur.execute("""
                            INSERT INTO plants (plant_id, customer_id, plant_name, capacity, install_date, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (plant_id) DO NOTHING
                        """, (
                            plant[plant_id_key], user_id, plant.get('plant_name', 'Unknown'),
                            plant.get('capacity', 0.0), plant.get('install_date', '1970-01-01'),
                            datetime.now(), datetime.now()
                        ))
                        logger.info(f"Inserted plant with ID {plant[plant_id_key]}")
                    except Exception as e:
                        logger.error(f"Failed to insert plant {plant[plant_id_key]}: {e}")
                        continue

                # Fetch and insert devices
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
                            logger.info(f"Inserted device with SN {device['sn']}")
                        except Exception as e:
                            logger.error(f"Failed to insert device {device.get('sn', 'unknown')}: {e}")
                            continue

                        # Fetch and process historical data with retry logic
                        try:
                            # Dynamic date range: last 7 days
                            end_date = datetime.now().strftime('%Y-%m-%d')  # Today: 2025-06-11
                            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')  # 2025-06-04

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

                            # Insert data using the separate function
                            insert_data_to_db(conn, historical_data)
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