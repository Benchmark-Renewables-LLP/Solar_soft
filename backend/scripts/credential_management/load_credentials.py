import logging
import os
import csv
from datetime import datetime
from psycopg2 import connect, OperationalError
from config.settings import DATABASE_URL
from pytz import timezone

logger = logging.getLogger(__name__)

# Logging setup
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_date = datetime.now(timezone('Asia/Kolkata')).strftime('%Y%m%d')
log_file = os.path.join(log_dir, f'load_credentials_{log_date}.log')

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

def validate_customer_id(customer_id):
    if not customer_id or customer_id.isspace():
        return False, "Customer ID cannot be empty or whitespace"
    if not re.match(r'^[a-zA-Z0-9_]+$', customer_id):
        return False, f"Invalid customer_id: {customer_id}. Must be alphanumeric or underscore"
    if len(customer_id) > 63:
        return False, f"Customer ID too long: {customer_id}. Max 63 characters"
    return True, None

def log_error_to_db(customer_id, device_sn, api_provider, field_name, field_value, error_message):
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

def load_credentials_to_db(conn, csv_file):
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
                        'password': row.get('password', ''),
                        'email': row.get('username', ''),
                        'password_sha256': row.get('password', ''),
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
    except Exception as e:
        logger.error(f"Failed to load credentials from CSV: {e}")
        conn.rollback()
        raise

if __name__ == "__main__":
    conn = get_db_connection()
    try:
        load_credentials_to_db(conn, "backend/data/users.csv")
    except Exception as e:
        logger.error(f"Error in load_credentials: {e}")
    finally:
        conn.close()