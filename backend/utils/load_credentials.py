import sys
import os
import logging
import csv
import re
from datetime import datetime
from psycopg2 import connect, OperationalError
from pytz import timezone
from logging import handlers

# Add the project root (/app) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

# Logging setup
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'current')
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
...(truncated 4231 characters)...tomers to process, exiting.")
            return []

        inserted_count = 0
        with conn.cursor() as cur:
            for credential in credentials:
                if credential['customer_id'] not in valid_customer_ids:
                    logger.warning(f"Skipping credential for invalid customer_id: {credential['customer_id']}")
                    log_error_to_db(None, None, credential['api_provider'], "customer_id", credential['customer_id'], "Customer ID not in customers table")
                    continue
                try:
                    cur.execute(
                        """
                        INSERT INTO api_credentials (
                            user_id, customer_id, api_provider, username, password, api_key, api_secret,
                            created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (user_id) DO NOTHING
                        """,
                        (
                            credential['user_id'], credential['customer_id'], credential['api_provider'],
                            credential['username'], credential['password'],
                            credential['api_key'], credential['api_secret'],
                            datetime.now(timezone('Asia/Kolkata')), datetime.now(timezone('Asia/Kolkata'))
                        )
                    )
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