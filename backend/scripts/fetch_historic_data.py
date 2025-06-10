import os
import logging
from logging.handlers import RotatingFileHandler
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import time
import sys
from dotenv import load_dotenv
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

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'solar_data'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'secret'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

BATCH_SIZE = int(os.getenv('BATCH_SIZE', 1000))

def get_db_connection():
    """Establish a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
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
    """Load users from CSV and insert into database."""
    users = []
    try:
        with open(csv_file, 'r') as f:
            # Skip header
            header = f.readline().strip().split(',')
            for line in f:
                values = line.strip().split(',')
                user = dict(zip(header, values))
                users.append(user)
        with conn.cursor() as cur:
            for user in users:
                cur.execute("""
                    INSERT INTO customers (customer_id, username, email, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (customer_id) DO NOTHING
                """, (
                    user['user_id'], user['username'], f"{user['username']}@example.com",
                    datetime.now(), datetime.now()
                ))
        conn.commit()
        return users
    except Exception as e:
        logger.error(f"Failed to load users from CSV: {e}")
        raise

def fetch_historic_data():
    """Main function to fetch and process historical data."""
    logger.info("Starting fetch_historic_data script...")
    conn = get_db_connection()

    try:
        # Load users and insert into database
        users = load_users_to_db(conn, 'backend/data/userx.csv')
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
            else:  # Default to Shinemonitor
                api_client = ShinemonitorAPI()
                fetch_plants = api_client.fetch_plant_list
                fetch_devices = api_client.fetch_plant_devices
                fetch_data = api_client.fetch_historical_data
                plant_id_key = 'plant_id'

            logger.info(f"Processing user {user_id}: {username} with {api_provider} API")

            plants = fetch_plants(user_id, username, password)
            if not plants:
                logger.warning(f"No plants found for user {user_id}")
                continue

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Insert plants
                for plant in plants:
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

                # Fetch and insert devices
                for plant in plants:
                    plant_id = plant[plant_id_key]
                    devices = fetch_devices(user_id, username, password, plant_id)
                    if not devices:
                        logger.warning(f"No devices found for plant {plant_id}")
                        continue
                    logger.info(f"Found {len(devices)} devices for plant {plant_id}")

                    for device in devices:
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

                    # Fetch and process historical data in batches
                    for device in devices:
                        start_date = "2025-06-08"
                        end_date = "2025-06-09"
                        logger.info(f"Fetching historical data for device {device['sn']}")

                        historical_data = fetch_data(user_id, username, password, device, start_date, end_date)
                        if not historical_data:
                            logger.warning(f"No historical data for device {device['sn']}")
                            continue
                        logger.info(f"Received {len(historical_data)} historical data entries for device {device['sn']}")

                        # Process data in batches
                        for i in range(0, len(historical_data), BATCH_SIZE):
                            batch = historical_data[i:i + BATCH_SIZE]
                            logger.info(f"Processing batch {i//BATCH_SIZE + 1} for device {device['sn']}")

                            for entry in batch:
                                # Clean and parse timestamp
                                ts_str = entry.get('timestamp')
                                if not ts_str:
                                    logger.warning(f"Missing timestamp for device {device['sn']}: {entry}")
                                    continue
                                ts_str = ts_str.strip()
                                try:
                                    ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                                    entry_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    logger.warning(f"Invalid timestamp format for device {device['sn']}: {ts_str}")
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
                                    logger.warning(f"Skipping entry for device {device['sn']} at {entry_timestamp} due to validation failure")
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
                                    device['sn'], entry_timestamp, entry.get('pv01_voltage'), entry.get('pv01_current'),
                                    entry.get('pv02_voltage'), entry.get('pv02_current'), entry.get('pv03_voltage'), entry.get('pv03_current'),
                                    entry.get('pv04_voltage'), entry.get('pv04_current'), entry.get('pv05_voltage'), entry.get('pv05_current'),
                                    entry.get('pv06_voltage'), entry.get('pv06_current'), entry.get('pv07_voltage'), entry.get('pv07_current'),
                                    entry.get('pv08_voltage'), entry.get('pv08_current'), entry.get('pv09_voltage'), entry.get('pv09_current'),
                                    entry.get('pv10_voltage'), entry.get('pv10_current'), entry.get('pv11_voltage'), entry.get('pv11_current'),
                                    entry.get('pv12_voltage'), entry.get('pv12_current'), entry.get('r_voltage'), entry.get('s_voltage'), entry.get('t_voltage'),
                                    entry.get('r_current'), entry.get('s_current'), entry.get('t_current'), entry.get('total_power'),
                                    entry.get('energy_today'), entry.get('pr'), entry.get('state')
                                ))
                                logger.info(f"Inserted data for device {device['sn']} at {entry_timestamp}")

                                # Insert audit log
                                cur.execute("""
                                    INSERT INTO audit_logs (table_name, operation, record_id, changed_by, changed_at, new_value)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (
                                    'device_data', 'INSERT', f"{device['sn']}_{entry_timestamp}", 'system',
                                    datetime.now(), {'device_sn': device['sn'], 'timestamp': entry_timestamp}
                                ))

                            conn.commit()
                            logger.info(f"Committed batch {i//BATCH_SIZE + 1} for device {device['sn']}")

        logger.info("Completed fetch_historic_data script.")
    except Exception as e:
        logger.error(f"Error in fetch_historic_data: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_historic_data()