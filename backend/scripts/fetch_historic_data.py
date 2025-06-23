# Install required libraries:
# `pip install requests psycopg2-binary tenacity python-dotenv`

import logging
import os
import sys
import time
import re
import csv
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from psycopg2 import connect, OperationalError, errors
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
from solarman_api import SolarmanAPI

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
class RealTimeRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding, delay=delay)
        if self.stream is not None:
            self.stream.close()
            self.stream = None
        self.stream = open(self.baseFilename, self.mode, buffering=1, encoding=self.encoding)

# Configure logging
try:
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'fetch_historic_data.log')

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RealTimeRotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'),
            UnicodeSafeStreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
except Exception as e:
    print(f"Failed to configure logging: {e}", file=sys.stderr)
    raise

# Load environment variables
load_dotenv()

def convert_timestamp_to_date(timestamp, default='1970-01-01'):
    """Convert Unix timestamp to YYYY-MM-DD format."""
    try:
        if isinstance(timestamp, (int, float)):
            if len(str(int(timestamp))) > 10:  # Milliseconds
                timestamp = timestamp / 1000
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        return timestamp
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to convert timestamp {timestamp}: {e}")
        return default

def get_db_connection():
    """Establish database connection."""
    try:
        conn = connect(DATABASE_URL)
        return conn
    except OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def validate_customer_id(customer_id):
    """Validate customer_id for safe table names."""
    if not customer_id or customer_id.isspace():
        return False, "Customer ID cannot be empty or whitespace"
    if not re.match(r'^[a-zA-Z0-9_]+$', customer_id):
        return False, f"Invalid customer_id: {customer_id}. Must be alphanumeric or underscore"
    if len(customer_id) > 63:
        return False, f"Customer ID too long: {customer_id}. Max 63 characters"
    return True, None

def validate_parameter(value, param_name, min_val, max_val):
    """Validate parameter value, return validity and error message."""
    if value is None:
        return True, None  # Allow NULL for absent fields
    try:
        val = float(value)
        if min_val <= val <= max_val:
            return True, None
        return False, f"Value {val} for {param_name} out of range [{min_val}, {max_val}]"
    except (ValueError, TypeError):
        return False, f"Invalid value for {param_name}: {value}"

def log_error_to_db(customer_id, device_sn, api_provider, field_name, field_value, error_message):
    """Log error to error_logs table using a separate connection."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO error_logs (
                    customer_id, device_sn, timestamp, api_provider, field_name, field_value, error_message, created_at
                )
                VALUES (%s, %s, NOW(), %s, %s, %s, %s, NOW())
            """, (customer_id, device_sn, api_provider, field_name, str(field_value), error_message))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to log error to error_logs: {e}")
    finally:
        conn.close()

def load_customers_to_db(conn, credentials):
    """Load customers into customers table with validation."""
    try:
        customer_ids = set(credential.get('customer_id', 'default_customer') for credential in credentials)
        if not customer_ids:
            logger.warning("No customer_ids found, using default customer.")
            customer_ids = {'default_customer'}

        valid_customer_ids = []
        for customer_id in customer_ids:
            is_valid, error = validate_customer_id(customer_id)
            if is_valid:
                valid_customer_ids.append(customer_id)
            else:
                logger.error(f"Invalid customer_id: {customer_id}. Error: {error}")
                log_error_to_db(None, None, None, "customer_id", customer_id, error)

        inserted_count = 0
        with conn.cursor() as cur:
            for customer_id in valid_customer_ids:
                try:
                    cur.execute("""
                        INSERT INTO customers (
                            customer_id, customer_name, email, phone, address, created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (customer_id) DO NOTHING
                    """, (
                        customer_id, customer_id, None, None, None, datetime.now(), datetime.now()
                    ))
                    inserted_count += cur.rowcount
                except Exception as e:
                    logger.error(f"Failed to insert customer {customer_id}: {e}")
                    log_error_to_db(customer_id, None, None, "insert_customer", customer_id, str(e))
                    conn.rollback()
                    continue
            conn.commit()
        logger.info(f"Inserted/updated {inserted_count} customers.")
        return valid_customer_ids
    except Exception as e:
        logger.error(f"Failed to load customers: {e}")
        conn.rollback()
        raise

def load_credentials_to_db(conn, csv_file):
    """Load API credentials from CSV to api_credentials table."""
    credentials = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_number, row in enumerate(reader, start=1):
                try:
                    if not row.get('user_id'):
                        logger.error(f"Missing user_id at row {row_number}: {row}")
                        log_error_to_db(None, None, None, "csv_row", str(row), "Missing user_id")
                        continue
                    credential = {
                        'user_id': row['user_id'],
                        'customer_id': row.get('customer_id', 'default_customer'),
                        'api_provider': row.get('api_provider', 'shinemonitor').lower(),
                        'username': row.get('username', ''),
                        'password': row.get('password', ''),  # For Shinemonitor/Soliscloud
                        'email': row.get('user_id', ''),        # For Solarman
                        'password_sha256': row.get('password', ''),  # For Solarman
                        'api_key': row.get('api_key', ''),
                        'api_secret': row.get('api_secret', '')
                    }
                    credentials.append(credential)
                except Exception as e:
                    logger.error(f"Error parsing CSV row {row_number}: {e}")
                    log_error_to_db(None, None, None, "csv_row", str(row), str(e))
                    continue

        valid_customer_ids = load_customers_to_db(conn, credentials)
        if not valid_customer_ids:
            logger.error("No valid customers to process, exiting.")
            return []

        inserted_count = 0
        with conn.cursor() as cur:
            for credential in credentials:
                if credential['customer_id'] not in valid_customer_ids:
                    logger.warning(f"Skipping credential for invalid customer_id: {credential['customer_id']}")
                    log_error_to_db(None, None, credential['api_provider'], "customer_id", credential['customer_id'], "Customer ID not in customers table")
                    continue
                try:
                    cur.execute("""
                        INSERT INTO api_credentials (
                            user_id, customer_id, api_provider, username, password, api_key, api_secret,
                            created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) DO NOTHING
                    """, (
                        credential['user_id'], credential['customer_id'], credential['api_provider'],
                        credential['username'], credential['password'],
                        credential['api_key'], credential['api_secret'], datetime.now(), datetime.now()
                    ))
                    inserted_count += cur.rowcount
                except Exception as e:
                    logger.error(f"Failed to insert credential for user {credential['user_id']}: {e}")
                    log_error_to_db(credential['customer_id'], None, credential['api_provider'], "insert_credential", credential['user_id'], str(e))
                    conn.rollback()
                    continue
        conn.commit()
        logger.info(f"Inserted {inserted_count} credentials.")
        return credentials
    except Exception as e:
        logger.error(f"Failed to load credentials from CSV: {e}")
        conn.rollback()
        raise

def load_credentials_from_db(conn):
    """Load API credentials from database."""
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
    """Normalize data entry with default NULL values, API-specific mappings."""
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
            'state': entry.get('state'),
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
        data_list = entry.get("dataList", [])
        for item in data_list:
            key = item.get("key", "").lower()
            value = item.get("value")
            if key in ['pv1_voltage', 'pv2_voltage', 'pv3_voltage', 'pv4_voltage', 'pv5_voltage', 'pv6_voltage', 'pv7_voltage', 'pv8_voltage', 'pv9_voltage', 'pv10_voltage', 'pv11_voltage', 'pv12_voltage']:
                normalized[key] = value
            elif key in ['pv1_current', 'pv2_current', 'pv3_current', 'pv4_current', 'pv5_current', 'pv6_current', 'pv7_current', 'pv8_current', 'pv9_current', 'pv10_current', 'pv11_current', 'pv12_current']:
                normalized[key] = value
            elif key in ['r_voltage', 's_voltage', 't_voltage', 'r_current', 's_current', 't_current', 'rs_voltage', 'st_voltage', 'tr_voltage']:
                normalized[key] = value
            elif key == 'frequency':
                normalized['frequency'] = value
            elif key in ['total_power', 'power']:
                normalized['total_power'] = value
            elif key in ['reactive_power']:
                normalized['reactive_power'] = value
            elif key in ['energy_today', 'e_day']:
                normalized['energy_today'] = value
            elif key in ['pr']:
                normalized['pr'] = value
            elif key in ['state', 'status']:
                normalized['state'] = value
        normalized['timestamp'] = entry.get('collectTime') or entry.get('timestamp')
    else:  # Shinemonitor
        normalized.update({
            'timestamp': entry.get('timestamp'),
            'total_power': entry.get('total_power'),
            'energy_today': entry.get('energy_today'),
            'pr': entry.get('pr'),
            'state': entry.get('state'),
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
    """Flatten nested lists into dictionaries, deduplicate by timestamp."""
    flattened = []
    seen_timestamps = set()
    if depth > max_depth:
        logger.error(f"Max recursion depth exceeded: {data}")
        return flattened
    if api_provider == 'solarman':
        param_data_list = data.get("paramDataList", []) if isinstance(data, dict) else data
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
    """Insert data into customer_{customer_id}_device_data (real-time) or device_data_historical (historical)."""
    try:
        table_name = f"customer_{customer_id.lower()}_device_data" if is_real_time else "device_data_historical"
        flattened_data = flatten_data(data, api_provider)
        if not flattened_data:
            logger.warning(f"No valid data to insert for device {device_sn}")
            return

        inserted_count = 0
        errors = []
        with conn.cursor() as cur:
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
                    if isinstance(ts_str, (int, float)):
                        ts = datetime.fromtimestamp(ts_str / 1000 if len(str(int(ts_str))) > 10 else ts_str)
                    else:
                        ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                    entry_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    errors.append(("timestamp", ts_str, "Invalid timestamp format"))
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
                            entry[pv_voltage_key] = None
                    if pv_current_key in entry and entry[pv_current_key] is not None:
                        is_valid, error = validate_parameter(entry[pv_current_key], pv_current_key, 0, 50)
                        if not is_valid:
                            validation_errors.append((pv_current_key, entry[pv_current_key], error))
                            entry[pv_current_key] = None
                for phase in ['r', 's', 't']:
                    voltage_key = f"{phase}_voltage"
                    current_key = f"{phase}_current"
                    if voltage_key in entry and entry[voltage_key] is not None:
                        is_valid, error = validate_parameter(entry[voltage_key], voltage_key, 0, 300)
                        if not is_valid:
                            validation_errors.append((voltage_key, entry[voltage_key], error))
                            entry[voltage_key] = None
                    if current_key in entry and entry[current_key] is not None:
                        is_valid, error = validate_parameter(entry[current_key], current_key, 0, 100)
                        if not is_valid:
                            validation_errors.append((current_key, entry[current_key], error))
                            entry[current_key] = None
                if "total_power" in entry and entry["total_power"] is not None:
                    is_valid, error = validate_parameter(entry["total_power"], "total_power", 0, 100000)
                    if not is_valid:
                        validation_errors.append(("total_power", entry["total_power"], error))
                        entry["total_power"] = None
                if "energy_today" in entry and entry["energy_today"] is not None:
                    is_valid, error = validate_parameter(entry["energy_today"], "energy_today", 0, 1000)
                    if not is_valid:
                        validation_errors.append(("energy_today", entry["energy_today"], error))
                        entry["energy_today"] = None
                if "pr" in entry and entry["pr"] is not None:
                    is_valid, error = validate_parameter(entry["pr"], "pr", 0, 100)
                    if not is_valid:
                        validation_errors.append(("pr", entry["pr"], error))
                        entry["pr"] = None
                if "frequency" in entry and entry["frequency"] is not None:
                    is_valid, error = validate_parameter(entry["frequency"], "frequency", 0, 70)
                    if not is_valid:
                        validation_errors.append(("frequency", entry["frequency"], error))
                        entry["frequency"] = None
                if "reactive_power" in entry and entry["reactive_power"] is not None:
                    is_valid, error = validate_parameter(entry["reactive_power"], "reactive_power", -100000, 100000)
                    if not is_valid:
                        validation_errors.append(("reactive_power", entry["reactive_power"], error))
                        entry["reactive_power"] = None

                if validation_errors:
                    for field_name, field_value, error_message in validation_errors:
                        logger.warning(f"Validation error for device {device_sn} at {entry_timestamp}: {field_name}: {error_message}")
                        log_error_to_db(customer_id, device_sn, api_provider, field_name, field_value, error_message)
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

                try:
                    cur.execute(f"""
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
                    """, data_tuple)
                    inserted_count += cur.rowcount
                except Exception as e:
                    logger.error(f"Failed to insert data entry for device {device_sn} at {entry_timestamp}: {e}")
                    log_error_to_db(customer_id, device_sn, api_provider, "insert_data", str(data_tuple), str(e))
                    continue

            for field_name, field_value, error_message in errors:
                log_error_to_db(customer_id, device_sn, api_provider, field_name, field_value, error_message)

        conn.commit()
        logger.info(f"Inserted {inserted_count} records into {table_name} for device {device_sn}.")
    except Exception as e:
        logger.error(f"Failed to insert data for device {device_sn}: {e}")
        log_error_to_db(customer_id, device_sn, api_provider, "insert_data_batch", str(device_sn), str(e))
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
        log_error_to_db(None, None, None, "refresh_customer_metrics", None, str(e))
        conn.rollback()
        raise

def fetch_historic_data():
    logger.info("Starting fetch_historic_data script...")
    conn = get_db_connection()
    try:
        csv_file = "backend/data/users.csv"
        credentials = load_credentials_to_db(conn, csv_file)

        if not credentials:
            logger.error("No credentials found, exiting.")
            return

        for credential in credentials:
            user_id = credential['user_id']
            customer_id = credential['customer_id']
            username = credential['username']
            password = credential['password']
            email = user_id
            password_sha256 = password
            api_key = credential.get('api_key')
            api_secret = credential.get('api_secret')
            api_provider = credential.get('api_provider', 'shinemonitor').lower()

            if api_provider == 'soliscloud':
                if not api_key or not api_secret:
                    logger.warning(f"No API key/secret for SolisCloud user {user_id}, skipping.")
                    log_error_to_db(customer_id, None, api_provider, "api_credentials", user_id, "Missing API key/secret")
                    continue
                api_client = SolisCloudAPI(api_key, api_secret)
                fetch_plants = api_client.get_all_stations
                fetch_devices = api_client.get_all_inverters
                fetch_historical = api_client.get_inverter_historical_data
                fetch_real_time = api_client.get_inverter_real_time_data
                plant_id_key = 'station_id'
            elif api_provider == 'solarman':
                if not email or not password_sha256 or not api_key or not api_secret:
                    logger.warning(f"Missing email/password_sha256/API key/secret for Solarman user {user_id}, skipping.")
                    log_error_to_db(customer_id, None, api_provider, "api_credentials", user_id, "Missing credentials")
                    continue
                api_client = SolarmanAPI(email, password_sha256, api_key, api_secret)
                fetch_plants = api_client.get_plant_list
                fetch_devices = api_client.get_all_devices
                fetch_historical = api_client.get_historical_data
                fetch_real_time = api_client.get_current_data
                plant_id_key = 'id'
            else:
                api_client = ShinemonitorAPI(COMPANY_KEY if COMPANY_KEY else None)
                fetch_plants = api_client.fetch_plant_list
                fetch_devices = api_client.fetch_plant_devices
                fetch_historical = api_client.fetch_historical_data
                fetch_real_time = api_client.fetch_current_data
                plant_id_key = 'plant_id'

            try:
                plants = fetch_plants(user_id, username, password)
                if not plants:
                    logger.warning(f"No plants found for user {user_id}, skipping.")
                    log_error_to_db(customer_id, None, api_provider, "fetch_plants", user_id, "No plants found")
                    continue
            except Exception as e:
                logger.error(f"Failed to fetch plants for user {user_id}: {e}")
                log_error_to_db(customer_id, None, api_provider, "fetch_plants", user_id, str(e))
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
                    log_error_to_db(customer_id, None, api_provider, "insert_plant", plant.get(plant_id_key), str(e))
                    conn.rollback()
                    continue

                plant_id = plant[plant_id_key]
                try:
                    devices = fetch_devices(user_id, username, password, plant_id)
                    if not devices:
                        logger.warning(f"No devices found for plant {plant_id}")
                        log_error_to_db(customer_id, None, api_provider, "fetch_devices", plant_id, "No devices found")
                        continue
                    logger.info(f"Found {len(devices)} devices for plant {plant_id}")
                except Exception as e:
                    logger.error(f"Failed to fetch devices for plant {plant_id}: {e}")
                    log_error_to_db(customer_id, None, api_provider, "fetch_devices", plant_id, str(e))
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
                        log_error_to_db(customer_id, device_sn, api_provider, "insert_device", device.get('sn', device.get('deviceSn')), str(e))
                        conn.rollback()
                        continue

                    try:
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
                        if real_time_response:
                            logger.info(f"Received real-time data entries for device {device_sn}")
                            insert_data_to_db(conn, real_time_response, device_sn, customer_id, api_provider, is_real_time=True)
                        else:
                            logger.warning(f"No real-time data for device {device_sn}")
                            log_error_to_db(customer_id, device_sn, api_provider, "fetch_real_time", device_sn, "No real-time data")

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
                        if not historical_data:
                            logger.warning(f"No historical data for device {device_sn}")
                            log_error_to_db(customer_id, device_sn, api_provider, "fetch_historical", device_sn, "No historical data")
                            continue
                        flattened_historical_data = flatten_data(historical_data, api_provider)
                        logger.info(f"Received {len(flattened_historical_data)} historical data entries for device {device_sn}")
                        insert_data_to_db(conn, flattened_historical_data, device_sn, customer_id, api_provider, is_real_time=False)
                    except Exception as e:
                        logger.error(f"Failed to fetch or insert data for device {device_sn}: {e}")
                        log_error_to_db(customer_id, device_sn, api_provider, "fetch_data", device_sn, str(e))
                        conn.rollback()
                        continue

        refresh_customer_metrics(conn)
        logger.info("Completed fetch_historic_data script.")
    except Exception as e:
        logger.error(f"Error in fetch_historic_data: {e}")
        log_error_to_db(None, None, None, "fetch_historic_data", None, str(e))
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_historic_data()