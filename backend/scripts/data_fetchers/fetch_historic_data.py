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
logger = logging.getLogger(__name__)

# Custom StreamHandler for Unicode characters
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

# Custom RotatingFileHandler with line buffering
class RealTimeRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay)
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        self.stream = open(self.baseFilename, self.mode, buffering=1, encoding=self.encoding)

# Logging setup
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'historic')
os.makedirs(log_dir, exist_ok=True)
log_date = datetime.now(timezone('Asia/Kolkata')).strftime('%Y%m%d')
log_file = os.path.join(log_dir, f'fetch_historic_data_{log_date}.log')

try:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Log file initialized at {datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S IST')}\n")
    logging.getLogger('').handlers = []
    file_handler = RealTimeRotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    stream_handler = UnicodeSafeStreamHandler()
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

def convert_timestamp_to_date(timestamp, default='1970-01-01'):
    try:
        if isinstance(timestamp, (int, float)):
            if len(str(int(timestamp))) > 10:
                timestamp = timestamp / 1000
            return datetime.fromtimestamp(timestamp, tz=timezone('UTC')).strftime('%Y-%m-%d')
        return timestamp
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to convert timestamp {timestamp}: {e}")
        return default

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

def flatten_data(data, api_provider, depth=0, max_depth=10):
    flattened = []
    seen_timestamps = set()
    if depth > max_depth:
        logger.error(f"Max recursion depth exceeded: {data}")
        return flattened
    if api_provider == 'solarman':
        param_data_list = data if isinstance(data, list) else data.get("paramDataList", [])
        for item in param_data_list:
            if isinstance(item, dict):
                timestamp = item.get('collectTime') or item.get('timestamp')
                if timestamp and timestamp not in seen_timestamps:
                    seen_timestamps.add(timestamp)
                    flattened.append(item)
                else:
                    logger.debug(f"Skipping duplicate Solarman entry with timestamp: {timestamp}")
    else:
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, list):
                flattened.extend(flatten_data(item, api_provider, depth + 1, max_depth))
            elif isinstance(item, dict):
                timestamp = item.get('timestamp') or item.get('collectTime')
                if timestamp and timestamp not in seen_timestamps:
                    seen_timestamps.add(timestamp)
                    flattened.append(item)
                else:
                    logger.debug(f"Skipping duplicate entry with timestamp: {timestamp}")
            else:
                logger.warning(f"Unexpected item type: {type(item)}, item: {item}")
    return flattened

def insert_data_to_db(conn, data, device_sn, customer_id, api_provider, is_real_time=True):
    try:
        table_name = f"customer_{customer_id.lower()}_device_data" if is_real_time else "device_data_historical"
        logger.info(f"Inserting data into {table_name} for device {device_sn}, is_real_time={is_real_time}")
        flattened_data = flatten_data(data, api_provider)
        if not flattened_data:
            logger.warning(f"No valid data to insert for device {device_sn}")
            return

        inserted_count = 0
        errors = []
        with conn.cursor() as cur:
            batch_size = 200
            data_tuples = []
            for entry in flattened_data:
                if not isinstance(entry, dict):
                    errors.append(("entry_type", str(entry), f"Invalid entry type: {type(entry)}"))
                    continue
                ts_str = entry.get('timestamp') or entry.get('collectTime')
                if not ts_str:
                    errors.append(("timestamp", None, "Missing timestamp"))
                    continue
                ts_str = ts_str.strip()
                try:
                    if isinstance(ts_str, (int, float)) or (isinstance(ts_str, str) and ts_str.replace('.', '', 1).isdigit()):
                        ts_float = float(ts_str)
                        if ts_float > 10**12:
                            ts_float = ts_float / 1000
                        ts = datetime.fromtimestamp(ts_float, tz=timezone('UTC'))
                    else:
                        ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone('UTC'))
                    entry_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError) as e:
                    errors.append(("timestamp", ts_str, f"Invalid timestamp format: {str(e)}"))
                    logger.error(f"Invalid timestamp for device {device_sn}: {ts_str}, error: {str(e)}")
                    continue

                logger.debug(f"Raw API data for device {device_sn} at {entry_timestamp}: {entry}")
                entry = normalize_data_entry(entry, api_provider)
                validation_errors = []
                for j in range(1, 13):
                    pv_voltage_key = f"pv{j:02d}_voltage"
                    pv_current_key = f"pv{j:02d}_current"
                    if pv_voltage_key in entry and entry[pv_voltage_key] is not None:
                        is_valid, error = validate_parameter(entry[pv_voltage_key], pv_voltage_key, 0, 1000)
                        if not is_valid:
                            validation_errors.append((pv_voltage_key, entry[pv_voltage_key], error))
                            logger.warning(f"Validation failed for device {device_sn} at {entry_timestamp}: {pv_voltage_key}={entry[pv_voltage_key]}, error: {error}, skipped")
                            entry[pv_voltage_key] = None
                    if pv_current_key in entry and entry[pv_current_key] is not None:
                        is_valid, error = validate_parameter(entry[pv_current_key], pv_current_key, 0, 50)
                        if not is_valid:
                            validation_errors.append((pv_current_key, entry[pv_current_key], error))
                            logger.warning(f"Validation failed for device {device_sn} at {entry_timestamp}: {pv_current_key}={entry[pv_current_key]}, error: {error}, skipped")
                            entry[pv_current_key] = None
                for phase in ['r', 's', 't']:
                    voltage_key = f"{phase}_voltage"
                    current_key = f"{phase}_current"
                    if voltage_key in entry and entry[voltage_key] is not None:
                        is_valid, error = validate_parameter(entry[voltage_key], voltage_key, 0, 300)
                        if not is_valid:
                            validation_errors.append((voltage_key, entry[voltage_key], error))
                            logger.warning(f"Validation failed for device {device_sn} at {entry_timestamp}: {voltage_key}={entry[voltage_key]}, error: {error}, skipped")
                            entry[voltage_key] = None
                    if current_key in entry and entry[current_key] is not None:
                        is_valid, error = validate_parameter(entry[current_key], current_key, 0, 100)
                        if not is_valid:
                            validation_errors.append((current_key, entry[current_key], error))
                            logger.warning(f"Validation failed for device {device_sn} at {entry_timestamp}: {current_key}={entry[current_key]}, error: {error}, skipped")
                            entry[current_key] = None
                if "total_power" in entry and entry["total_power"] is not None:
                    is_valid, error = validate_parameter(entry["total_power"], "total_power", 0, 100000)
                    if not is_valid:
                        validation_errors.append(("total_power", entry["total_power"], error))
                        logger.warning(f"Validation failed for device {device_sn} at {entry_timestamp}: total_power={entry['total_power']}, error: {error}, skipped")
                        entry["total_power"] = None
                if "energy_today" in entry and entry["energy_today"] is not None:
                    is_valid, error = validate_parameter(entry["energy_today"], "energy_today", 0, 1000)
                    if not is_valid:
                        validation_errors.append(("energy_today", entry["energy_today"], error))
                        logger.warning(f"Validation failed for device {device_sn} at {entry_timestamp}: energy_today={entry['energy_today']}, error: {error}, skipped")
                        entry["energy_today"] = None
                if "pr" in entry and entry["pr"] is not None:
                    is_valid, error = validate_parameter(entry["pr"], "pr", 0, 100)
                    if not is_valid:
                        validation_errors.append(("pr", entry["pr"], error))
                        logger.warning(f"Validation failed for device {device_sn} at {entry_timestamp}: pr={entry['pr']}, error: {error}, skipped")
                        entry["pr"] = None
                if "frequency" in entry and entry["frequency"] is not None:
                    is_valid, error = validate_parameter(entry["frequency"], "frequency", 0, 70)
                    if not is_valid:
                        validation_errors.append(("frequency", entry["frequency"], error))
                        logger.warning(f"Validation failed for device {device_sn} at {entry_timestamp}: frequency={entry['frequency']}, error: {error}, skipped")
                        entry["frequency"] = None
                if "reactive_power" in entry and entry["reactive_power"] is not None:
                    is_valid, error = validate_parameter(entry["reactive_power"], "reactive_power", -100000, 100000)
                    if not is_valid:
                        validation_errors.append(("reactive_power", entry["reactive_power"], error))
                        logger.warning(f"Validation failed for device {device_sn} at {entry_timestamp}: reactive_power={entry['reactive_power']}, error: {error}, skipped")
                        entry["reactive_power"] = None

                if validation_errors:
                    for field_name, field_value, error_message in validation_errors:
                        log_error_to_db(customer_id, device_sn, api_provider, field_name, field_value, error_message)
                if len(entry) <= 1:
                    logger.warning(f"Skipping invalid data entry for device {device_sn} at {entry_timestamp} after validation")
                    continue

                logger.debug(f"Processed entry for device {device_sn} at {entry_timestamp}: {entry}")

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
                    try:
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
                    except Exception as e:
                        logger.error(f"Failed to insert batch for device {device_sn}: {e}")
                        data_tuples = []

            if data_tuples:
                try:
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
                except Exception as e:
                    logger.error(f"Failed to insert final batch for device {device_sn}: {e}")

            for field_name, field_value, error_message in errors:
                log_error_to_db(customer_id, device_sn, api_provider, field_name, field_value, error_message)

        conn.commit()
        logger.info(f"Inserted {inserted_count} records into {table_name} for device {device_sn}.")
    except Exception as e:
        logger.error(f"Failed to insert data for device {device_sn}: {e}")
        conn.rollback()
        raise

def aggregate_daily_data(conn, device_sn, customer_id, api_provider):
    try:
        logger.info(f"Aggregating daily data for device {device_sn}")
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO device_data_daily (device_sn, date, total_energy, avg_power, max_voltage, min_voltage, active_hours)
                SELECT 
                    device_sn,
                    DATE(timestamp) AS date,
                    SUM(energy_today) AS total_energy,
                    AVG(total_power) AS avg_power,
                    MAX(GREATEST(r_voltage, s_voltage, t_voltage)) AS max_voltage,
                    LEAST(r_voltage, s_voltage, t_voltage) AS min_voltage,
                    SUM(CASE WHEN total_power > 0 THEN EXTRACT(EPOCH FROM (LEAD(timestamp) OVER (PARTITION BY device_sn ORDER BY timestamp) - timestamp)) / 3600 ELSE 0 END) AS active_hours
                FROM device_data_historical
                WHERE device_sn = %s AND timestamp >= CURRENT_DATE - INTERVAL '1 day'
                GROUP BY device_sn, DATE(timestamp)
                ON CONFLICT (device_sn, date) DO UPDATE
                SET total_energy = EXCLUDED.total_energy,
                    avg_power = EXCLUDED.avg_power,
                    max_voltage = EXCLUDED.max_voltage,
                    min_voltage = EXCLUDED.min_voltage,
                    active_hours = EXCLUDED.active_hours,
                    created_at = NOW();
            """, (device_sn,))
        conn.commit()
        logger.info(f"Aggregated daily data for device {device_sn}")
    except Exception as e:
        logger.error(f"Failed to aggregate daily data for device {device_sn}: {e}")
        conn.rollback()
        raise

def refresh_customer_metrics(conn):
    """Refresh customer_metrics materialized view."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT customer_id FROM customers")
            customer_ids = [row[0] for row in cur.fetchall()]
            if not customer_ids:
                logger.info("No customers found, skipping customer_metrics refresh.")
                return
            union_queries = [
                f"""
                SELECT
                    '{cid}' AS customer_id,
                    COALESCE(SUM(ddc.energy_today), 0.0) AS total_energy_today,
                    COALESCE(AVG(ddc.pr), 0.0) AS avg_pr,
                    COUNT(DISTINCT ddc.device_sn) AS active_devices
                FROM customer_{cid.lower()}_device_data ddc
                WHERE ddc.timestamp > NOW() - INTERVAL '1 day'
                """
                for cid in customer_ids
            ]
            cur.execute(f"""
                DROP MATERIALIZED VIEW IF EXISTS customer_metrics;
                CREATE MATERIALIZED VIEW customer_metrics AS
                {' UNION ALL '.join(union_queries)}
                WITH DATA;
            """)
        conn.commit()
        logger.info("Refreshed customer_metrics materialized view.")
    except Exception as e:
        logger.error(f"Failed to refresh customer_metrics: {e}")
        conn.rollback()
        raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((OperationalError, requests_exceptions.RequestException))
)
def fetch_historic_data():
    logger.info("Starting fetch_historic_data script...")
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
                fetch_plants = api_client.get_all_stations
                fetch_devices = api_client.get_all_inverters
                fetch_historical = api_client.get_inverter_historical_data
                plant_id_key = 'station_id'
            elif api_provider == 'solarman':
                if not email or not password_sha256 or not api_key or not api_secret:
                    logger.warning(f"Missing email/password_sha256/API key/secret for Solarman user {user_id}, skipping.")
                    continue
                api_client = SolarmanAPI(email, password_sha256, api_key, api_secret)
                fetch_plants = api_client.get_plant_list
                fetch_devices = api_client.get_all_devices
                fetch_historical = api_client.get_historical_data
                plant_id_key = 'id'
            else:
                api_client = ShinemonitorAPI(COMPANY_KEY if COMPANY_KEY else None)
                fetch_plants = api_client.fetch_plant_list
                fetch_devices = api_client.fetch_plant_devices
                fetch_historical = api_client.fetch_historical_data
                plant_id_key = 'plant_id'

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
                            logger.info(f"Inserted plant {plant[plant_id_key]} for customer {customer_id}")
                    conn.commit()
                except Exception as e:
                    logger.error(f"Failed to insert plant {plant.get(plant_id_key, 'unknown')}: {e}")
                    conn.rollback()
                    continue

                plant_id = plant[plant_id_key]
                try:
                    devices_start = time.time()
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
                    try:
                        first_install_date = convert_timestamp_to_date(device.get('first_install_date', '1970-01-01'))
                        device['first_install_date'] = first_install_date
                        device_sn = device.get('sn') or device.get('deviceSn')

                        with conn.cursor(cursor_factory=RealDictCursor) as cur:
                            cur.execute("""
                                INSERT INTO devices (device_sn, plant_id, inverter_model, panel_model, pv_count, string_count, first_install_date, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (device_sn) DO NOTHING
                                RETURNING device_sn
                            """, (
                                device_sn, plant_id, device.get('inverter_model', 'Unknown'),
                                device.get('panel_model', 'Unknown'), int(device.get('pv_count', 0)),
                                int(device.get('string_count', 0)), first_install_date,
                                datetime.now(), datetime.now()
                            ))
                            result = cur.fetchone()
                            if result:
                                logger.info(f"Inserted device {device_sn} for plant {plant_id}")
                        conn.commit()
                    except Exception as e:
                        logger.error(f"Failed to insert device {device.get('sn', device.get('deviceSn', 'unknown'))}: {e}")
                        conn.rollback()
                        continue

                    try:
                        historical_start = time.time()
                        end_date = datetime.now().strftime('%Y-%m-%d')
                        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')

                        @retry(
                            stop=stop_after_attempt(3),
                            wait=wait_exponential(multiplier=1, min=2, max=10),
                            retry=retry_if_exception_type(requests_exceptions.RequestException)
                        )
                        def fetch_historical_with_retry():
                            response = fetch_historical(user_id, username, password, device, start_date, end_date)
                            logger.debug(f"Historical API response for device {device_sn}: {response}")
                            return response

                        historical_data = fetch_historical_with_retry()
                        logger.info(f"Fetched historical data for {device_sn} in {time.time() - historical_start:.2f}s")
                        if not historical_data:
                            logger.warning(f"No historical data for device {device_sn}")
                            continue
                        flattened_historical_data = flatten_data(historical_data, api_provider)
                        logger.info(f"Received {len(flattened_historical_data)} historical data entries for device {device_sn}")
                        insert_data_to_db(conn, flattened_historical_data, device_sn, customer_id, api_provider, is_real_time=False)

                        aggregate_daily_data(conn, device_sn, customer_id, api_provider)

                    except Exception as e:
                        logger.error(f"Failed to fetch or insert data for device {device_sn}: {e}")
                        conn.rollback()
                        continue

        refresh_customer_metrics(conn)
        logger.info(f"Completed fetch_historic_data script in {time.time() - start_time:.2f}s")
    except Exception as e:
        logger.error(f"Error in fetch_historic_data: {e}", exc_info=True)
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_historic_data()