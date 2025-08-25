from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from backend.config.settings import settings
from backend.models.user import UserCreate, UserLogin, UserOut, Token
from backend.repository.user_repo import create_user, get_user_by_username, get_user_by_email
from backend.utils.auth_utils import verify_password
import uuid
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(login_id: str, password: str, userType: str) -> UserOut | bool:
    logger.debug(f"Authenticating user: login_id={login_id}, userType={userType}")
    user_dict = get_user_by_username(login_id) or get_user_by_email(login_id)
    if not user_dict:
        logger.error(f"User not found: {login_id}")
        return False
    if user_dict['userType'] != userType:
        logger.error(f"Incorrect userType: expected {user_dict['userType']}, got {userType}")
        raise HTTPException(status_code=400, detail=f"Incorrect userType: must be {user_dict['userType']} for {login_id}")
    if not verify_password(password, user_dict['password_hash']):
        logger.error(f"Password verification failed for {login_id}")
        return False
    return UserOut(**user_dict)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def login_user(user_credentials: UserLogin) -> Token:
    logger.debug(f"Login attempt: {user_credentials}")
    user = authenticate_user(user_credentials.username, user_credentials.password, user_credentials.userType)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "userType": user.userType}, expires_delta=access_token_expires
    )
    return Token(token=access_token, user=user)