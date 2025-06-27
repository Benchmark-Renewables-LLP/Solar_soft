import psycopg2
import csv
import logging
from datetime import datetime
from config.settings import DATABASE_URL
from scripts.shinemonitor_api import fetch_plant_list, fetch_plant_devices, fetch_current_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """Establish a connection to TimescaleDB."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logging.info("Successfully connected to TimescaleDB")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to TimescaleDB: {e}")
        raise

def get_last_fetch_timestamp(conn, device_id):
    """Get the last fetch timestamp for a device."""
    with conn.cursor() as cur:
        cur.execute("SELECT MAX(timestamp) FROM device_data_current WHERE device_id = %s", (device_id,))
        result = cur.fetchone()
        return result[0].strftime("%Y-%m-%dT%H:%M:%SZ") if result[0] else None

def insert_current_data(conn, data):
    """Insert current data into the device_data_current table."""
    with conn.cursor() as cur:
        for entry in data:
            cur.execute("""
                INSERT INTO device_data_current (
                    device_id, timestamp, pv01_voltage, pv01_current, pv02_voltage, pv02_current,
                    pv03_voltage, pv03_current, pv04_voltage, pv04_current, pv05_voltage, pv05_current,
                    pv06_voltage, pv06_current, pv07_voltage, pv07_current, pv08_voltage, pv08_current,
                    pv09_voltage, pv09_current, pv10_voltage, pv10_current, pv11_voltage, pv11_current,
                    pv12_voltage, pv12_current, r_voltage, s_voltage, t_voltage, r_current, s_current,
                    t_current, rs_voltage, st_voltage, tr_voltage, frequency, total_power,
                    reactive_power, energy_today, cuf, pr, state
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                entry["device_id"], entry["timestamp"], entry.get("pv01_voltage"), entry.get("pv01_current"),
                entry.get("pv02_voltage"), entry.get("pv02_current"), entry.get("pv03_voltage"), entry.get("pv03_current"),
                entry.get("pv04_voltage"), entry.get("pv04_current"), entry.get("pv05_voltage"), entry.get("pv05_current"),
                entry.get("pv06_voltage"), entry.get("pv06_current"), entry.get("pv07_voltage"), entry.get("pv07_current"),
                entry.get("pv08_voltage"), entry.get("pv08_current"), entry.get("pv09_voltage"), entry.get("pv09_current"),
                entry.get("pv10_voltage"), entry.get("pv10_current"), entry.get("pv11_voltage"), entry.get("pv11_current"),
                entry.get("pv12_voltage"), entry.get("pv12_current"), entry.get("r_voltage"), entry.get("s_voltage"),
                entry.get("t_voltage"), entry.get("r_current"), entry.get("s_current"), entry.get("t_current"),
                entry.get("rs_voltage"), entry.get("st_voltage"), entry.get("tr_voltage"), entry.get("frequency"),
                entry.get("total_power"), entry.get("reactive_power"), entry.get("energy_today"), entry.get("cuf"),
                entry.get("pr"), entry.get("state")
            ))
        conn.commit()
        logging.info(f"Inserted {len(data)} current records")

def ingest_data():
    """Fetch current data for all devices and store in the database."""
    conn = get_db_connection()
    try:
        with open("backend/data/users.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                usr, pwd = row["usr"], row["pwd"]
                user_id = row.get("user_id", usr)
                
                plants = fetch_plant_list(user_id, usr, pwd)
                if not plants:
                    logging.warning(f"No plants found for user {user_id}")
                    continue
                
                for plant in plants:
                    plant_id = plant["plant_id"]
                    devices = fetch_plant_devices(user_id, usr, pwd, plant_id)
                    if not devices:
                        logging.warning(f"No devices found for plant {plant_id}")
                        continue
                    
                    for device in devices:
                        since = get_last_fetch_timestamp(conn, device["sn"])
                        current_data = fetch_current_data(user_id, usr, pwd, device, since)
                        if current_data:
                            insert_current_data(conn, current_data)
                            logging.info(f"Fetched and stored current data for device {device['sn']}")
                        else:
                            logging.warning(f"No current data fetched for device {device['sn']}")
    except Exception as e:
        logging.error(f"Error during data ingestion: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    ingest_data()