from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings
from backend.models.user import UserOut
import logging
import json  # Added import

logger = logging.getLogger(__name__)

try:
    engine = create_engine(settings.DATABASE_URL)
    logger.debug("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

Session = sessionmaker(bind=engine)

def get_user_by_username(username: str) -> dict | None:
    try:
        with Session() as session:
            result = session.execute(
                text("SELECT * FROM users WHERE username = :username"),
                {"username": username}
            )
            row = result.mappings().fetchone()
            logger.debug(f"User query by username {username}: {row}")
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error querying user by username {username}: {e}")
        raise

def get_user_by_email(email: str) -> dict | None:
    try:
        with Session() as session:
            result = session.execute(
                text("SELECT * FROM users WHERE email = :email"),
                {"email": email}
            )
            row = result.mappings().fetchone()
            logger.debug(f"User query by email {email}: {row}")
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error querying user by email {email}: {e}")
        raise

async def create_user(user_data: dict) -> dict:
    try:
        with Session() as session:
            user_data_serialized = user_data.copy()
            if 'profile' in user_data_serialized:
                user_data_serialized['profile'] = json.dumps(user_data_serialized['profile'])
            query = text("""
                INSERT INTO users (id, username, name, email, password_hash, usertype, profile, verified, created_at, last_login, updated_at)
                VALUES (:id, :username, :name, :email, :password_hash, :usertype, :profile, :verified, :created_at, :last_login, :updated_at)
                RETURNING id, username, name, email, password_hash, usertype, profile::text, verified, created_at, last_login, updated_at
            """)
            result = session.execute(query, user_data_serialized)
            session.commit()
            row = result.mappings().fetchone()
            logger.debug(f"Created user: {row}")
            if row:
                row = dict(row)
                row['profile'] = json.loads(row['profile']) if row['profile'] else {}
                row['userType'] = row.pop('usertype')
            return row if row else None
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        session.rollback()
        raise

async def verify_user(email: str) -> dict:
    try:
        with Session() as session:
            query = text("""
                UPDATE users SET verified = TRUE WHERE email = :email
                RETURNING id, username, name, email, password_hash, usertype, profile::text, verified, created_at, last_login, updated_at
            """)
            result = session.execute(query, {"email": email})
            session.commit()
            row = result.mappings().fetchone()
            logger.debug(f"Verified user: {row}")
            if row:
                row = dict(row)
                row['profile'] = json.loads(row['profile']) if row['profile'] else {}
                row['userType'] = row.pop('usertype')
            return row if row else None
    except Exception as e:
        logger.error(f"Error verifying user with email {email}: {str(e)}")
        session.rollback()
        raise