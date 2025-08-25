from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings
from backend.models.user import UserOut
import logging
from datetime import datetime

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
logger = logging.getLogger(__name__)

def get_user_by_username(username: str) -> dict | None:
    with Session() as session:
        result = session.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": username}
        )
        row = result.mappings().fetchone()
        return dict(row) if row else None

def get_user_by_email(email: str) -> dict | None:
    with Session() as session:
        result = session.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": email}
        )
        row = result.mappings().fetchone()
        return dict(row) if row else None

def create_user(user_data: dict) -> UserOut:
    with Session() as session:
        try:
            result = session.execute(
                text("""
                    INSERT INTO users (id, username, name, email, password_hash, userType, profile)
                    VALUES (:id, :username, :name, :email, :password_hash, :userType, :profile)
                    RETURNING id, username, name, email, userType, profile, created_at, last_login
                """),
                {
                    "id": user_data["id"],
                    "username": user_data["username"],
                    "name": user_data["name"],
                    "email": user_data["email"],
                    "password_hash": user_data["password_hash"],
                    "userType": user_data["userType"],
                    "profile": user_data["profile"]
                }
            )
            session.commit()
            row = result.mappings().fetchone()
            return UserOut(**row)
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            session.rollback()
            raise

def update_user_profile(user_id: str, name: str | None, profile: dict | None) -> UserOut:
    with Session() as session:
        try:
            updates = {}
            if name:
                updates["name"] = name
            if profile:
                updates["profile"] = profile
            updates["last_login"] = datetime.utcnow().isoformat()
            result = session.execute(
                text("""
                    UPDATE users 
                    SET name = COALESCE(:name, name), 
                        profile = COALESCE(:profile, profile),
                        last_login = :last_login
                    WHERE id = :id
                    RETURNING id, username, name, email, userType, profile, created_at, last_login
                """),
                {"id": user_id, "name": name, "profile": profile, "last_login": updates["last_login"]}
            )
            session.commit()
            row = result.mappings().fetchone()
            return UserOut(**row)
        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            session.rollback()
            raise