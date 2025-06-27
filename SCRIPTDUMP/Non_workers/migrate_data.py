import os
import logging
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'solar_data'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'secret'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Establish a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def migrate_data():
    """Migrate data from device_data_current to device_data_historical."""
    conn = get_db_connection()
    threshold = datetime.now() - timedelta(days=7)  # 7-day threshold
    threshold_str = threshold.strftime('%Y-%m-%d %H:%M:%S')

    try:
        with conn.cursor() as cur:
            # Step 1: Select records older than the threshold
            cur.execute("""
                SELECT *
                FROM device_data_current
                WHERE timestamp < %s;
            """, (threshold_str,))
            records_to_move = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            if not records_to_move:
                logger.info("No records to migrate.")
                return

            logger.info(f"Found {len(records_to_move)} records to migrate.")

            # Step 2: Insert records into device_data_historical
            insert_query = f"""
                INSERT INTO device_data_historical ({', '.join(columns)})
                VALUES ({', '.join(['%s'] * len(columns))})
                ON CONFLICT (device_sn, timestamp) DO NOTHING;
            """
            cur.executemany(insert_query, records_to_move)
            logger.info(f"Inserted {cur.rowcount} records into device_data_historical.")

            # Step 3: Delete the moved records from device_data_current
            cur.execute("""
                DELETE FROM device_data_current
                WHERE timestamp < %s;
            """, (threshold_str,))
            logger.info(f"Deleted {cur.rowcount} records from device_data_current.")

        conn.commit()
        logger.info("Data migration completed successfully.")
    except Exception as e:
        logger.error(f"Error during data migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_data()