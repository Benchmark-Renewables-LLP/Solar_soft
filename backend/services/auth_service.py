from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.config.settings import settings
from backend.models.user import UserCreate, UserLogin, UserOut, Token
from backend.repository.user_repo import create_user, get_user_by_username, get_user_by_email
from backend.utils.auth_utils import verify_password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(login_id: str, password: str) -> UserOut | bool:
    user_dict = get_user_by_username(login_id) or get_user_by_email(login_id)
    if not user_dict:
        return False
    if not verify_password(password, user_dict['password_hash']):
        return False
    # Extract UserOut fields
    user = UserOut(id=user_dict['id'], username=user_dict['username'], email=user_dict['email'], role=user_dict['role'])
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def register_user(user: UserCreate) -> UserOut:
    existing_user = get_user_by_username(user.username) or get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    hashed_password = hash_password(user.password)
    created_user = create_user(user.username, user.email, hashed_password, user.role)
    return created_user

async def login_user(user_credentials: UserLogin) -> Token:
    user = authenticate_user(user_credentials.username, user_credentials.password)  # username as login_id
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)