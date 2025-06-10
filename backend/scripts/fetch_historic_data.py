import sys
import os
import csv
import logging
import re
from datetime import datetime
import psycopg2

# Project imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from shinemonitor_api import fetch_plant_list, fetch_plant_devices, fetch_historical_data
from config.settings import DATABASE_URL

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Regex for numeric validation
NUMBER_REGEX = re.compile(r'^(\d*\.\d+|\d+)$')

def validate_parameter(value, param_name, min_val, max_val):
    if value is None:
        return True
    str_value = str(value)
    if not NUMBER_REGEX.match(str_value):
        logging.warning(f"Invalid format for {param_name}: {str_value}")
        return False
    num_value = float(str_value)
    if not (min_val <= num_value <= max_val):
        
        logging.warning(f"Value out of range for {param_name}: {num_value} (expected {min_val} to {max_val})")
        return False
    return True

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logging.info("Connected to TimescaleDB")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to TimescaleDB: {e}")
        raise

def fetch_historic_data():
    print("Starting fetch_historic_data script...")
    conn = get_db_connection()

    try:
        with open('backend/data/userx.csv', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            users = list(reader)
            if users:
                print(f"Keys in first user dictionary: {users[0].keys()}")

        for user in users:
            user_id = user['user_id']
            username = user['username']
            password = user['password']
            logging.info(f"Processing user {user_id}: {username}")
            print(f"Processing user {user_id}: {username}")

            plants = fetch_plant_list(user_id, username, password)
            if not plants:
                logging.warning(f"No plants found for user {user_id}")
                continue

            with conn.cursor() as cur:
                for plant in plants:
                    print(f"Processing plant ID {plant['plant_id']}")
                    cur.execute("""
                        INSERT INTO plants (plant_id, customer_name, capacity, total_energy, install_date)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (plant_id) DO NOTHING
                    """, (
                        plant['plant_id'], plant['customer_name'], plant['capacity'],
                        plant['total_energy'], plant['install_date']
                    ))
                    logging.info(f"Inserted plant with ID {plant['plant_id']}")

                for plant in plants:
                    plant_id = plant['plant_id']
                    devices = fetch_plant_devices(user_id, username, password, plant_id)
                    if not devices:
                        logging.warning(f"No devices found for plant {plant_id}")
                        continue
                    print(f"Found {len(devices)} devices for plant {plant_id}: {[device['sn'] for device in devices]}")

                    for device in devices:
                        print(f"Processing device SN {device['sn']} for plant {plant_id}")
                        cur.execute("""
                            INSERT INTO devices (sn, plant_id, first_install_date, inverter_model, panel_model, pv_count, string_count)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (sn) DO NOTHING
                        """, (
                            device['sn'], plant_id, device['first_install_date'], device['inverter_model'],
                            device['panel_model'], device['pv_count'], device['string_count']
                        ))
                        logging.info(f"Inserted device with SN {device['sn']}")

                    for device in devices:
                        start_date = "2025-06-08"
                        end_date = "2025-06-09"
                        logging.info(f"Fetching historical data for device {device['sn']}")
                        print(f"Fetching historical data for device {device['sn']} on {start_date}")

                        historical_data = fetch_historical_data(user_id, username, password, device, start_date, end_date)
                        if not historical_data:
                            logging.warning(f"No historical data for device {device['sn']}")
                            continue
                        print(f"Received {len(historical_data)} historical data entries for device {device['sn']}")

                        for entry in historical_data:
                            # Ensure timestamp is present
                            ts_str = entry.get('timestamp')
                            if not ts_str:
                                logging.warning(f"Missing timestamp for device {device['sn']}: {entry}")
                                continue
                            try:
                                # Parse timestamp to ensure it's in the correct format
                                ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                                entry_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                logging.warning(f"Invalid timestamp format for device {device['sn']}: {ts_str}")
                                continue

                            print(f"Processing historical data entry for device {device['sn']} at {entry_timestamp}")

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
                            if not validate_parameter(entry.get("total_power"), "total_power", 0, 100000):
                                valid = False
                            if not validate_parameter(entry.get("energy_today"), "energy_today", 0, 100):
                                valid = False

                            if not valid:
                                logging.warning(f"Skipping entry for device {device['sn']} at {entry_timestamp} due to validation failure")
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
                            logging.info(f"Inserted historical data for device {device['sn']} at {entry_timestamp}")
                            print(f"Successfully inserted historical data for device {device['sn']} at {entry_timestamp}")

        conn.commit()
        logging.info("Completed fetch_historic_data script.")
        print("Done.")
    except Exception as e:
        logging.error(f"Error in fetch_historic_data: {e}")
        print(f"Error in fetch_historic_data: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_historic_data()