import sys
import os
import csv
import logging
import re
from datetime import datetime
import psycopg2
from logging.handlers import TimedRotatingFileHandler

# Project imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from shinemonitor_api import fetch_plant_list, fetch_plant_devices, fetch_historical_data
from config.settings import DATABASE_URL

# Set up logging with a dedicated log folder
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'fetch_historic_data.log')

# Configure logging with TimedRotatingFileHandler for daily logs
logger = logging.getLogger('FetchHistoricData')
logger.setLevel(logging.INFO)

# File handler (rotates daily)
file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', interval=1, backupCount=30)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Regex for numeric validation
NUMBER_REGEX = re.compile(r'^(\d*\.\d+|\d+)$')

# Output CSV path
OUTPUT_CSV_PATH = 'backend/data/historical_data_output.csv'

# Define CSV fieldnames based on historical_data structure
CSV_FIELDNAMES = [
    'device_id', 'timestamp',
    'pv01_voltage', 'pv01_current', 'pv02_voltage', 'pv02_current',
    'pv03_voltage', 'pv03_current', 'pv04_voltage', 'pv04_current',
    'pv05_voltage', 'pv05_current', 'pv06_voltage', 'pv06_current',
    'pv07_voltage', 'pv07_current', 'pv08_voltage', 'pv08_current',
    'pv09_voltage', 'pv09_current', 'pv10_voltage', 'pv10_current',
    'pv11_voltage', 'pv11_current', 'pv12_voltage', 'pv12_current',
    'r_voltage', 's_voltage', 't_voltage',
    'r_current', 's_current', 't_current',
    'rs_voltage', 'st_voltage', 'tr_voltage',
    'frequency', 'total_power', 'reactive_power',
    'energy_today', 'cuf', 'pr', 'state'
]

def validate_parameter(value, param_name, min_val, max_val):
    if value is None:
        return True
    str_value = str(value)
    if not NUMBER_REGEX.match(str_value):
        logger.warning(f"Invalid format for {param_name}: {str_value}")
        return False
    num_value = float(str_value)
    if not (min_val <= num_value <= max_val):
        logger.warning(f"Value out of range for {param_name}: {num_value} (expected {min_val} to {max_val})")
        return False
    return True

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("Connected to TimescaleDB")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to TimescaleDB: {e}")
        raise

def fetch_historic_data():
    print("Starting fetch_historic_data script...")
    logger.info("Starting fetch_historic_data script...")
    conn = get_db_connection()

    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)

        # Write CSV header if the file doesn't exist
        if not os.path.exists(OUTPUT_CSV_PATH):
            with open(OUTPUT_CSV_PATH, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
                writer.writeheader()
                logger.info(f"Created output CSV file at {OUTPUT_CSV_PATH} with headers")

        with open('backend/data/users.csv', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            users = list(reader)
            if users:
                print(f"Keys in first user dictionary: {users[0].keys()}")
                logger.info(f"Keys in first user dictionary: {users[0].keys()}")

        for user in users:
            user_id = user['user_id']
            username = user['username']
            password = user['password']
            logger.info(f"Processing user {user_id}: {username}")
            print(f"Processing user {user_id}: {username}")

            plants = fetch_plant_list(user_id, username, password)
            if not plants:
                logger.warning(f"No plants found for user {user_id}")
                continue

            with conn.cursor() as cur:
                for plant in plants:
                    print(f"Processing plant ID {plant['plant_id']}")
                    logger.info(f"Processing plant ID {plant['plant_id']}")
                    cur.execute("""
                        INSERT INTO plants (plant_id, customer_name, capacity, total_energy, install_date)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (plant_id) DO NOTHING
                    """, (
                        plant['plant_id'], plant['customer_name'], plant['capacity'],
                        plant['total_energy'], plant['install_date']
                    ))
                    logger.info(f"Inserted plant with ID {plant['plant_id']}")

                for plant in plants:
                    plant_id = plant['plant_id']
                    devices = fetch_plant_devices(user_id, username, password, plant_id)
                    if not devices:
                        logger.warning(f"No devices found for plant {plant_id}")
                        continue
                    print(f"Found {len(devices)} devices for plant {plant_id}: {[device['sn'] for device in devices]}")
                    logger.info(f"Found {len(devices)} devices for plant {plant_id}: {[device['sn'] for device in devices]}")

                    for device in devices:
                        print(f"Processing device SN {device['sn']} for plant {plant_id}")
                        logger.info(f"Processing device SN {device['sn']} for plant {plant_id}")
                        cur.execute("""
                            INSERT INTO devices (sn, plant_id, first_install_date, inverter_model, panel_model, pv_count, string_count)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (sn) DO NOTHING
                        """, (
                            device['sn'], plant_id, device['first_install_date'], device['inverter_model'],
                            device['panel_model'], device['pv_count'], device['string_count']
                        ))
                        logger.info(f"Inserted device with SN {device['sn']}")

                    for device in devices:
                        start_date = "2025-06-09 12:00:00"
                        end_date = "2025-06-09 13:00:00"
                        logger.info(f"Fetching historical data for device {device['sn']}")
                        print(f"Fetching historical data for device {device['sn']} from {start_date} to {end_date}")

                        historical_data = fetch_historical_data(user_id, username, password, device, start_date, end_date)
                        if not historical_data:
                            logger.warning(f"No historical data for device {device['sn']}")
                            continue
                        print(f"Received {len(historical_data)} historical data entries for device {device['sn']}")
                        logger.info(f"Received {len(historical_data)} historical data entries for device {device['sn']}")

                        # Write historical data to CSV
                        with open(OUTPUT_CSV_PATH, 'a', newline='', encoding='utf-8') as csvfile:
                            writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
                            for entry in historical_data:
                                writer.writerow(entry)
                            logger.info(f"Appended {len(historical_data)} rows to {OUTPUT_CSV_PATH} for device {device['sn']}")

                        for entry in historical_data:
                            # Ensure timestamp is present
                            ts_str = entry.get('timestamp')
                            if not ts_str:
                                logger.warning(f"Missing timestamp for device {device['sn']}: {entry}")
                                continue
                            try:
                                # Parse timestamp to ensure it's in the correct format
                                ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                                entry_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                logger.warning(f"Invalid timestamp format for device {device['sn']}: {ts_str}")
                                continue

                            print(f"Processing historical data entry for device {device['sn']} at {entry_timestamp}")
                            logger.info(f"Processing historical data entry for device {device['sn']} at {entry_timestamp}")

                            # Validate important parameters
                            valid = True
                            for i in range(1, 13):
                                if not validate_parameter(entry.get(f"pv{i:02d}_voltage"), f"pv{i:02d}_voltage", 0, 1000):
                                    valid = False
                                if not validate_parameter(entry.get(f"pv{i:02d}_current"), f"pv{i:02d}_current", 0, 50):
                                    valid = False
                            for phase in ['r', 's', 't']:
                                if not validate_parameter(entry.get(f"{phase}_voltage"), f"{phase}_voltage", 0, 300):
                                    valid = False
                            if not validate_parameter(entry.get("total_power"), "total_power", 0, 5000):
                                valid = False
                            if not validate_parameter(entry.get("energy_today"), "energy_today", 0, 50):
                                valid = False

                            if not valid:
                                logger.warning(f"Skipping entry for device {device['sn']} at {entry_timestamp} due to validation failure")
                                continue

                            print(f"Inserting historical data for device {device['sn']} at {entry_timestamp}")
                            cur.execute("""
                                INSERT INTO device_data_current (
                                    device_id, timestamp, pv01_voltage, pv01_current, pv02_voltage, pv02_current,
                                    pv03_voltage, pv03_current, pv04_voltage, pv04_current, pv05_voltage, pv05_current,
                                    pv06_voltage, pv06_current, pv07_voltage, pv07_current, pv08_voltage, pv08_current,
                                    pv09_voltage, pv09_current, pv10_voltage, pv10_current, pv11_voltage, pv11_current,
                                    pv12_voltage, pv12_current, r_voltage, s_voltage, t_voltage,
                                    r_current, s_current, t_current, rs_voltage, st_voltage, tr_voltage,
                                    frequency, total_power, reactive_power, energy_today, cuf, pr, state
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (device_id, timestamp) DO NOTHING
                            """, (
                                entry['device_id'], entry_timestamp, entry.get('pv01_voltage'), entry.get('pv01_current'),
                                entry.get('pv02_voltage'), entry.get('pv02_current'), entry.get('pv03_voltage'), entry.get('pv03_current'),
                                entry.get('pv04_voltage'), entry.get('pv04_current'), entry.get('pv05_voltage'), entry.get('pv05_current'),
                                entry.get('pv06_voltage'), entry.get('pv06_current'), entry.get('pv07_voltage'), entry.get('pv07_current'),
                                entry.get('pv08_voltage'), entry.get('pv08_current'), entry.get('pv09_voltage'), entry.get('pv09_current'),
                                entry.get('pv10_voltage'), entry.get('pv10_current'), entry.get('pv11_voltage'), entry.get('pv11_current'),
                                entry.get('pv12_voltage'), entry.get('pv12_current'), entry.get('r_voltage'), entry.get('s_voltage'), entry.get('t_voltage'),
                                entry.get('r_current'), entry.get('s_current'), entry.get('t_current'), entry.get('rs_voltage'),
                                entry.get('st_voltage'), entry.get('tr_voltage'), entry.get('frequency'), entry.get('total_power'),
                                entry.get('reactive_power'), entry.get('energy_today'), entry.get('cuf'), entry.get('pr'), entry.get('state')
                            ))
                            logger.info(f"Inserted historical data for device {device['sn']} at {entry_timestamp}")
                            print(f"Successfully inserted historical data for device {device['sn']} at {entry_timestamp}")

        conn.commit()
        logger.info("Completed fetch_historic_data script.")
        print("Done.")
    except Exception as e:
        logger.error(f"Error in fetch_historic_data: {e}")
        print(f"Error in fetch_historic_data: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_historic_data()