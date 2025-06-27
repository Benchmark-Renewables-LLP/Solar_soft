import os
import sys
# Add backend to Python path (three levels up from data_fetchers to backend)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import logging
import time
from datetime import datetime, timedelta
from psycopg2 import connect, OperationalError
from psycopg2.extras import RealDictCursor
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests import exceptions as requests_exceptions
from config.settings import DATABASE_URL,COMPANY_KEY
from pytz import timezone
import logging.handlers
sys.path.append((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api_clients.solarman_api import SolarmanAPI  # Explicit class import
from api_clients.soliscloud_api import SolisCloudAPI  # Explicit class import
from api_clients.shinemonitor_api import ShinemonitorAPI  # Explicit class import
# Add backend to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


logger = logging.getLogger(__name__)

# Logging setup
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'current')
os.makedirs(log_dir, exist_ok=True)
log_date = datetime.now(timezone('Asia/Kolkata')).strftime('%Y%m%d')
log_file = os.path.join(log_dir, f'fetch_current_data_{log_date}.log')

try:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Log file initialized at {datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S IST')}\n")
    logging.getLogger('').handlers = []
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info(f"Logging initialized. Log file: {log_file}")
except Exception as e:
    print(f"Failed to configure logging: {str(e)}", file=sys.stderr)
    raise

def get_db_connection():
    try:
        conn = connect(DATABASE_URL)
        return conn
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def load_credentials_from_db(conn):
    credentials = []
    try:
        if conn.closed:
            raise Exception("Database connection is closed.")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT user_id, customer_id, api_provider, username, password, api_key, api_secret
                FROM api_credentials;
            """)
            credentials = cur.fetchall()
            logger.info(f"Loaded {len(credentials)} credentials.")
        return credentials
    except Exception as e:
        logger.error(f"Failed to load credentials from database: {e}")
        raise

def insert_data_to_db(conn, data, device_sn, customer_id, api_provider, is_real_time=True):
    try:
        table_name = f"customer_{customer_id.lower()}_device_data"
        logger.info(f"Inserting data into {table_name} for device {device_sn}, is_real_time={is_real_time}")
        flattened_data = data
        if not flattened_data:
            logger.warning(f"No valid data to insert for device {device_sn}")
            return

        inserted_count = 0
        with conn.cursor() as cur:
            batch_size = 200
            data_tuples = []
            for entry in flattened_data:
                if not isinstance(entry, dict):
                    continue
                ts_str = entry.get('timestamp')
                if not ts_str:
                    continue
                ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone('UTC'))
                entry_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')

                logger.debug(f"Raw API data for device {device_sn} at {entry_timestamp}: {entry}")
                entry = normalize_data_entry(entry, api_provider)
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
                data_tuples.append(data_tuple)

                if len(data_tuples) >= batch_size:
                    cur.executemany(f"""
                        INSERT INTO {table_name} (
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
                    """, data_tuples)
                    inserted_count += cur.rowcount
                    data_tuples = []

            if data_tuples:
                cur.executemany(f"""
                    INSERT INTO {table_name} (
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
                """, data_tuples)
                inserted_count += cur.rowcount

        conn.commit()
        logger.info(f"Inserted {inserted_count} records into {table_name} for device {device_sn}.")
    except Exception as e:
        logger.error(f"Failed to insert data for device {device_sn}: {e}")
        conn.rollback()
        raise

def normalize_data_entry(entry, api_provider):
    default_entry = {
        'pv01_voltage': None, 'pv01_current': None, 'pv02_voltage': None, 'pv02_current': None,
        'pv03_voltage': None, 'pv03_current': None, 'pv04_voltage': None, 'pv04_current': None,
        'pv05_voltage': None, 'pv05_current': None, 'pv06_voltage': None, 'pv06_current': None,
        'pv07_voltage': None, 'pv07_current': None, 'pv08_voltage': None, 'pv08_current': None,
        'pv09_voltage': None, 'pv09_current': None, 'pv10_voltage': None, 'pv10_current': None,
        'pv11_voltage': None, 'pv11_current': None, 'pv12_voltage': None, 'pv12_current': None,
        'r_voltage': None, 's_voltage': None, 't_voltage': None,
        'r_current': None, 's_current': None, 't_current': None,
        'rs_voltage': None, 'st_voltage': None, 'tr_voltage': None,
        'frequency': None, 'total_power': None, 'reactive_power': None,
        'energy_today': None, 'cuf': None, 'pr': None, 'state': 'unknown'
    }
    normalized = default_entry.copy()

    if api_provider == 'soliscloud':
        normalized.update({
            'timestamp': entry.get('timestamp'),
            'total_power': entry.get('total_power'),
            'energy_today': entry.get('energy_today'),
            'pr': entry.get('pr'),
            'state': entry.get('state', 'unknown'),
            'r_voltage': entry.get('r_voltage'),
            's_voltage': entry.get('s_voltage'),
            't_voltage': entry.get('t_voltage'),
            'r_current': entry.get('r_current'),
            's_current': entry.get('s_current'),
            't_current': entry.get('t_current'),
        })
        for i in range(1, 13):
            normalized[f'pv{i:02d}_voltage'] = entry.get(f'pv{i:02d}_voltage')
            normalized[f'pv{i:02d}_current'] = entry.get(f'pv{i:02d}_current')
    elif api_provider == 'solarman':
        normalized.update({
            'timestamp': entry.get('timestamp') or entry.get('collectTime'),
        })
        for i in range(1, 13):
            normalized[f'pv{i:02d}_voltage'] = entry.get(f'pv{i:02d}_voltage')
            normalized[f'pv{i:02d}_current'] = entry.get(f'pv{i:02d}_current')
        normalized.update({
            'r_voltage': entry.get('r_voltage'),
            's_voltage': entry.get('s_voltage'),
            't_voltage': entry.get('t_voltage'),
            'r_current': entry.get('r_current'),
            's_current': entry.get('s_current'),
            't_current': entry.get('t_current'),
            'rs_voltage': entry.get('rs_voltage'),
            'st_voltage': entry.get('st_voltage'),
            'tr_voltage': entry.get('tr_voltage'),
            'frequency': entry.get('frequency'),
            'total_power': entry.get('total_power'),
            'reactive_power': entry.get('reactive_power'),
            'energy_today': entry.get('energy_today'),
            'pr': entry.get('pr'),
            'state': entry.get('state', 'unknown'),
        })
    else:  # Shinemonitor
        normalized.update({
            'timestamp': entry.get('timestamp'),
            'total_power': entry.get('total_power'),
            'energy_today': entry.get('energy_today'),
            'pr': entry.get('pr'),
            'state': entry.get('state', 'unknown'),
            'r_voltage': entry.get('r_voltage'),
            's_voltage': entry.get('s_voltage'),
            't_voltage': entry.get('t_voltage'),
            'r_current': entry.get('r_current'),
            's_current': entry.get('s_current'),
            't_current': entry.get('t_current'),
            'frequency': entry.get('frequency'),
            'reactive_power': entry.get('reactive_power'),
            'cuf': entry.get('cuf'),
        })
        for i in range(1, 13):
            normalized[f'pv{i:02d}_voltage'] = entry.get(f'pv{i:02d}_voltage')
            normalized[f'pv{i:02d}_current'] = entry.get(f'pv{i:02d}_current')

    return normalized

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((OperationalError, requests_exceptions.RequestException))
)
def fetch_current_data():
    logger.info("Starting fetch_current_data script...")
    conn = get_db_connection()
    start_time = time.time()
    try:
        credentials = load_credentials_from_db(conn)

        if not credentials:
            logger.error("No credentials found, exiting.")
            return

        for credential in credentials:
            user_id = credential['user_id']
            customer_id = credential['customer_id']
            username = credential['username']
            password = credential['password']
            email = credential.get('username')
            password_sha256 = credential.get('password')
            api_key = credential.get('api_key')
            api_secret = credential.get('api_secret')
            api_provider = credential.get('api_provider', 'shinemonitor').lower()

            if api_provider == 'soliscloud':
                if not api_key or not api_secret:
                    logger.warning(f"No API key/secret for SolisCloud user {user_id}, skipping.")
                    continue
                api_client = SolisCloudAPI(api_key, api_secret)
                fetch_plants = api_client.get_all_stations  # Updated to match SolisCloud method
            elif api_provider == 'solarman':
                if not email or not password_sha256 or not api_key or not api_secret:
                    logger.warning(f"Missing email/password_sha256/API key/secret for Solarman user {user_id}, skipping.")
                    continue
                api_client = SolarmanAPI(email, password_sha256, api_key, api_secret)
                fetch_plants = api_client.get_plant_list  # Updated to match Solarman method
            else:
                api_client = ShinemonitorAPI(COMPANY_KEY if COMPANY_KEY else None)
                fetch_plants = api_client.fetch_plant_list  # Matches Shinemonitor method

            try:
                plants_start = time.time()
                plants = fetch_plants(user_id, username, password)
                logger.info(f"Fetched plants for {user_id} in {time.time() - plants_start:.2f}s")
                if not plants:
                    logger.warning(f"No plants found for user {user_id}, skipping.")
                    continue
            except Exception as e:
                logger.error(f"Failed to fetch plants for user {user_id}: {e}")
                continue

            for plant in plants:
                plant_id = plant.get('plant_id') or plant.get('station_id') or plant.get('id')
                try:
                    devices_start = time.time()
                    if api_provider == 'soliscloud':
                        fetch_devices = api_client.get_all_inverters  # Updated to match SolisCloud method
                    elif api_provider == 'solarman':
                        fetch_devices = api_client.get_all_devices  # Updated to match Solarman method
                    else:
                        fetch_devices = api_client.fetch_plant_devices  # Matches Shinemonitor method
                    devices = fetch_devices(user_id, username, password, plant_id)
                    logger.info(f"Fetched devices for plant {plant_id} in {time.time() - devices_start:.2f}s")
                    if not devices:
                        logger.warning(f"No devices found for plant {plant_id}")
                        continue
                    logger.info(f"Found {len(devices)} devices for plant {plant_id}")
                except Exception as e:
                    logger.error(f"Failed to fetch devices for plant {plant_id}: {e}")
                    continue

                for device in devices:
                    device_sn = device.get('sn') or device.get('deviceSn')
                    try:
                        device_start = time.time()
                        if api_provider == 'soliscloud':
                            fetch_real_time = api_client.get_inverter_current_data  # Updated to match SolisCloud method
                        elif api_provider == 'solarman':
                            fetch_real_time = api_client.get_current_day_data  # Updated to match Solarman method
                        else:
                            fetch_real_time = api_client.fetch_current_data  # Matches Shinemonitor method
                        @retry(
                            stop=stop_after_attempt(3),
                            wait=wait_exponential(multiplier=1, min=2, max=10),
                            retry=retry_if_exception_type(requests_exceptions.RequestException)
                        )
                        def fetch_real_time_with_retry():
                            response = fetch_real_time(user_id, username, password, device)
                            logger.debug(f"Real-time API response for device {device_sn}: {response}")
                            return response

                        real_time_response = fetch_real_time_with_retry()
                        logger.info(f"Fetched real-time data for {device_sn} in {time.time() - device_start:.2f}s")
                        if real_time_response:
                            logger.info(f"Received real-time data entries for device {device_sn}")
                            insert_data_to_db(conn, real_time_response, device_sn, customer_id, api_provider, is_real_time=True)
                        else:
                            logger.warning(f"No real-time data for device {device_sn}")

                    except Exception as e:
                        logger.error(f"Failed to fetch or insert data for device {device_sn}: {e}")
                        conn.rollback()
                        continue

        logger.info(f"Completed fetch_current_data script in {time.time() - start_time:.2f}s")
    except Exception as e:
        logger.error(f"Error in fetch_current_data: {e}", exc_info=True)
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_current_data()