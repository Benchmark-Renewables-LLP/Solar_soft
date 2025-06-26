import psycopg2
import logging
from datetime import datetime
from config.settings import DATABASE_URL

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logging.info("Connected to TimescaleDB")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to TimescaleDB: {e}")
        raise

def generate_alerts():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Get the latest data for each device
            cur.execute("""
                SELECT device_id, timestamp, state, total_power
                FROM device_data_current
                WHERE timestamp > NOW() - INTERVAL '10 minutes'
                ORDER BY timestamp DESC
            """)
            rows = cur.fetchall()

            # Track the last state to detect changes
            last_states = {}
            for row in rows:
                device_id, timestamp, state, total_power = row
                last_state = last_states.get(device_id, None)

                # Check for duplicate alerts
                cur.execute("""
                    SELECT alert_type 
                    FROM alerts 
                    WHERE device_id = %s AND timestamp > NOW() - INTERVAL '1 hour' AND acknowledged = FALSE 
                    ORDER BY timestamp DESC LIMIT 1
                """, (device_id,))
                last_alert = cur.fetchone()

                # Check for fault state
                if state == "Fault" and (not last_alert or last_alert[0] != 'fault'):
                    cur.execute("""
                        INSERT INTO alerts (plant_id, device_id, timestamp, alert_type, message, severity)
                        SELECT plant_id, %s, %s, 'fault', %s, 'critical'
                        FROM devices WHERE sn = %s
                    """, (device_id, timestamp, f"Device {device_id} reported a fault", device_id))
                    logging.info(f"Generated fault alert for device {device_id}")

                # Check for performance drop
                if last_state and total_power and last_state['total_power']:
                    drop_percentage = ((last_state['total_power'] - total_power) / last_state['total_power']) * 100
                    if drop_percentage > 50 and (not last_alert or last_alert[0] != 'performance_drop'):
                        cur.execute("""
                            INSERT INTO alerts (plant_id, device_id, timestamp, alert_type, message, severity)
                            SELECT plant_id, %s, %s, 'performance_drop', %s, 'warning'
                            FROM devices WHERE sn = %s
                        """, (device_id, timestamp, f"Device {device_id} power dropped by {drop_percentage:.2f}%", device_id))
                        logging.info(f"Generated performance drop alert for device {device_id}")

                last_states[device_id] = {'state': state, 'total_power': total_power}

        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    generate_alerts()