import sys
import os
import psycopg2
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config import TIMESCALEDB_URL 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()]
)

def create_schema():
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(TIMESCALEDB_URL)
        cursor = conn.cursor()

        # ─── Create plants table ─── #
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            capacity FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ─── Create devices table ─── #
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            plant_id TEXT REFERENCES plants(id),
            name TEXT NOT NULL,
            type TEXT,
            is_new_device BOOLEAN DEFAULT FALSE,
            pv_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_plant_id ON devices(plant_id);")

        conn.commit()
        logging.info("Plants and devices tables created successfully.")

    except Exception as e:
        logging.error(f"Schema creation failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_schema()
