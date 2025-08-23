from psycopg2 import connect, OperationalError
from contextlib import contextmanager
from typing import Generator
import logging
from config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

class DBConnection:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

@contextmanager
def get_db_connection() -> Generator[DBConnection, None, None]:
    conn = None
    try:
        conn = connect(DATABASE_URL)
        yield DBConnection(conn)
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        if conn:
            conn.close()
        raise
    finally:
        if conn and not conn.closed:
            conn.close()

def close_db_connection(conn):
    if conn and not conn.closed:
        conn.close()