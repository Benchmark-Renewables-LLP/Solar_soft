from sqlalchemy.orm import Session
from backend.models.user import UserOut

def get_user_by_username(db: Session, username: str) -> UserOut | None:
    """Get user by username."""
    result = db.execute(
        "SELECT * FROM users WHERE username = :username",
        {"username": username}
    ).first()
    if result:
        return UserOut(**result)
    return None

def get_user_by_email(db: Session, email: str) -> UserOut | None:
    """Get user by email."""
    result = db.execute(
        "SELECT * FROM users WHERE email = :email",
        {"email": email}
    ).first()
    if result:
        return UserOut(**result)
    return None

def get_user_by_id(db: Session, user_id: str) -> UserOut | None:
    """Get user by ID."""
    result = db.execute(
        "SELECT * FROM users WHERE id = :user_id",
        {"user_id": user_id}
    ).first()
    if result:
        return UserOut(**result)
    return None

def get_users(db: Session) -> list[UserOut]:
    """Get all users."""
    result = db.execute("SELECT * FROM users").all()
    return [UserOut(**row) for row in result]

def create_user(db: Session, user_data: dict) -> UserOut:
    """Create a new user."""
    db.execute(
        """
        INSERT INTO users (
            id, username, name, email, password_hash, usertype,
            profile, verified, created_at, updated_at
        )
        VALUES (:id, :username, :name, :email, :password_hash, :usertype,
                :profile, :verified, :created_at, :updated_at)
        """,
        user_data
    )
    db.commit()
    return get_user_by_username(db, user_data['username'])

def verify_user(db: Session, email: str) -> UserOut | None:
    """Verify a user by email."""
    db.execute(
        "UPDATE users SET verified = true, updated_at = NOW() WHERE email = :email",
        {"email": email}
    )
    db.commit()
    return get_user_by_email(db, email)

def update_user(db: Session, user_id: str, user_update: dict) -> UserOut | None:
    """Update a user."""
    db.execute(
        """
        UPDATE users SET
            name = :name,
            email = :email,
            profile = :profile,
            updated_at = NOW()
        WHERE id = :user_id
        """,
        {**user_update, "user_id": user_id}
    )
    db.commit()
    return get_user_by_id(db, user_id)