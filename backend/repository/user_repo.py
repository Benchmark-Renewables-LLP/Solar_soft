from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings
from backend.models.user import UserOut
import logging

engine = create_engine(settings.POSTGRES_URL)
Session = sessionmaker(bind=engine)
logger = logging.getLogger(__name__)

def get_user_by_username(username: str) -> dict | None:
    with Session() as session:
        result = session.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": username}
        )
        row = result.mappings().fetchone()  # Return as dict
        return dict(row) if row else None

def get_user_by_email(email: str) -> dict | None:
    with Session() as session:
        result = session.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": email}
        )
        row = result.mappings().fetchone()
        return dict(row) if row else None

def create_user(username: str, email: str, hashed_password: str, role: str) -> UserOut:
    with Session() as session:
        try:
            result = session.execute(
                text("""
                    INSERT INTO users (username, email, password_hash, role)
                    VALUES (:username, :email, :hashed_password, :role)
                    RETURNING id, username, email, role
                """),
                {"username": username, "email": email, "hashed_password": hashed_password, "role": role}
            )
            session.commit()
            row = result.fetchone()
            return UserOut(id=row.id, username=row.username, email=row.email, role=row.role)
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            session.rollback()
            raise