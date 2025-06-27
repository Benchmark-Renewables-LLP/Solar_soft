import psycopg2
import logging
from datetime import datetime, timedelta
from config.settings import DATABASE_URL

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

def aggregate_and_transfer_data(conn):
    """Aggregate current day's data and transfer to device_daily_historical."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    with conn.cursor() as cur:
        # Get all device_ids for today's data
        cur.execute("SELECT DISTINCT device_id FROM device_data_current WHERE DATE(timestamp) = %s", (today,))
        device_ids = [row[0] for row in cur.fetchall()]
        
        for device_id in device_ids:
            # Aggregate data
            cur.execute("""
                SELECT 
                    AVG(pv01_voltage), AVG(pv01_current), AVG(pv02_voltage), AVG(pv02_current),
                    AVG(pv03_voltage), AVG(pv03_current), AVG(pv04_voltage), AVG(pv04_current),
                    AVG(pv05_voltage), AVG(pv05_current), AVG(pv06_voltage), AVG(pv06_current),
                    AVG(pv07_voltage), AVG(pv07_current), AVG(pv08_voltage), AVG(pv08_current),
                    AVG(pv09_voltage), AVG(pv09_current), AVG(pv10_voltage), AVG(pv10_current),
                    AVG(pv11_voltage), AVG(pv11_current), AVG(pv12_voltage), AVG(pv12_current),
                    AVG(r_voltage), AVG(s_voltage), AVG(t_voltage), AVG(r_current), AVG(s_current),
                    AVG(t_current), AVG(rs_voltage), AVG(st_voltage), AVG(tr_voltage), AVG(frequency),
                    AVG(total_power), AVG(reactive_power), AVG(energy_today), AVG(cuf), AVG(pr),
                    (SELECT state FROM device_data_current WHERE device_id = %s AND DATE(timestamp) = %s ORDER BY timestamp DESC LIMIT 1)
                FROM device_data_current
                WHERE device_id = %s AND DATE(timestamp) = %s
            """, (device_id, today, device_id, today))
            result = cur.fetchone()
            
            if result:
                # Insert aggregated data into device_daily_historical
                cur.execute("""
                    INSERT INTO device_daily_historical (
                        device_id, date, avg_pv01_voltage, avg_pv01_current, avg_pv02_voltage, avg_pv02_current,
                        avg_pv03_voltage, avg_pv03_current, avg_pv04_voltage, avg_pv04_current, avg_pv05_voltage, avg_pv05_current,
                        avg_pv06_voltage, avg_pv06_current, avg_pv07_voltage, avg_pv07_current, avg_pv08_voltage, avg_pv08_current,
                        avg_pv09_voltage, avg_pv09_current, avg_pv10_voltage, avg_pv10_current, avg_pv11_voltage, avg_pv11_current,
                        avg_pv12_voltage, avg_pv12_current, avg_r_voltage, avg_s_voltage, avg_t_voltage, avg_r_current, avg_s_current,
                        avg_t_current, avg_rs_voltage, avg_st_voltage, avg_tr_voltage, avg_frequency, avg_total_power,
                        avg_reactive_power, avg_energy_today, avg_cuf, avg_pr, state
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (device_id, date) DO NOTHING
                """, (
                    device_id, today, result[0], result[1], result[2], result[3], result[4], result[5],
                    result[6], result[7], result[8], result[9], result[10], result[11], result[12], result[13],
                    result[14], result[15], result[16], result[17], result[18], result[19], result[20], result[21],
                    result[22], result[23], result[24], result[25], result[26], result[27], result[28], result[29],
                    result[30], result[31], result[32], result[33], result[34], result[35], result[36], result[37],
                    result[38]
                ))
                logging.info(f"Aggregated and transferred data for device {device_id} on {today}")
        
        # Clear today's data from device_data_current
        cur.execute("DELETE FROM device_data_current WHERE DATE(timestamp) = %s", (today,))
        conn.commit()
        logging.info(f"Cleared current data for {today}")

def end_of_day():
    """Perform end-of-day aggregation and cleanup."""
    conn = get_db_connection()
    try:
        aggregate_and_transfer_data(conn)
    except Exception as e:
        logging.error(f"Error during end-of-day processing: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    end_of_day()