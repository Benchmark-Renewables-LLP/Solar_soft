import psycopg2
import csv
import logging
from config.settings import DATABASE_URL
from scripts.shinemonitor_api import fetch_plant_list

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """
    Establish a connection to TimescaleDB.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logging.info("Successfully connected to TimescaleDB")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to TimescaleDB: {e}")
        raise

def insert_user(conn, username, password, role, customer_id, is_paying):
    """
    Insert a user into the users table.
    """
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (username, password, role, customer_id, is_paying)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            RETURNING user_id
        """, (username, password, role, customer_id, is_paying))
        result = cur.fetchone()
        conn.commit()
        return result[0] if result else cur.execute("SELECT user_id FROM users WHERE username = %s", (username,)), cur.fetchone()[0]

def test_setup():
    """
    Test the database connection and API integration.
    """
    # Connect to the database
    conn = get_db_connection()
    
    try:
        # Read users from CSV and insert into the database
        with open("backend/data/users.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                usr, pwd, role = row["usr"], row["pwd"], row["role"]
                customer_id = int(row["customer_id"]) if row["customer_id"] else None
                is_paying = row["is_paying"].lower() == "true"
                user_id = insert_user(conn, usr, pwd, role, customer_id, is_paying)
                logging.info(f"Inserted user {user_id}: {usr}")

                # Test API call (expecting failure due to mock credentials)
                plants = fetch_plant_list(user_id, usr, pwd)
                if plants:
                    logging.info(f"Successfully fetched plants for user {user_id}: {plants}")
                else:
                    logging.warning(f"No plants fetched for user {user_id} (expected with mock credentials)")

    except Exception as e:
        logging.error(f"Error during test: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_setup()