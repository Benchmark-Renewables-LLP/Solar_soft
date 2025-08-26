from datetime import datetime, timedelta
from fastapi import HTTPException, status
import jwt
from passlib.context import CryptContext
from backend.config.settings import settings
from backend.models.user import UserCreate, UserLogin, UserOut, Token, OTPVerify
from backend.repository.user_repo import get_user_by_username, get_user_by_email, create_user, verify_user
from backend.utils.auth_utils import verify_password
import redis.asyncio as redis
import logging
import uuid
import random
import string
import json

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
redis_client = redis.from_url(settings.REDIS_URL)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))

async def send_otp_email(email: str, otp: str):
    logger.debug(f"Mock sending OTP {otp} to {email}")

def authenticate_user(login_id: str, password: str, userType: str) -> UserOut | bool:
    logger.debug(f"Authenticating user: login_id={login_id}, userType={userType}")
    user_dict = get_user_by_username(login_id.strip()) or get_user_by_email(login_id.strip())
    if not user_dict:
        logger.warning(f"User not found: login_id={login_id}")
        return False
    if not user_dict.get('verified', False):
        logger.warning(f"User not verified: login_id={login_id}")
        raise HTTPException(status_code=403, detail="Account not verified. Please check your email for the OTP.")
    if 'usertype' not in user_dict:
        logger.error(f"Database schema error: 'usertype' column missing for user {login_id}")
        raise HTTPException(status_code=500, detail="Database schema error: missing usertype column")
    if user_dict['usertype'] != userType:
        logger.warning(f"Incorrect userType: expected {user_dict['usertype']}, got {userType}")
        raise HTTPException(status_code=400, detail=f"Incorrect userType: must be {user_dict['usertype']}")
    if not verify_password(password, user_dict['password_hash']):
        logger.warning(f"Password verification failed for login_id={login_id}")
        return False
    logger.debug(f"User authenticated: {user_dict['username']}")
    user_dict['userType'] = user_dict.pop('usertype')
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
    logger.debug(f"Login attempt: username={user_credentials.username}, userType={user_credentials.userType}")
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
    logger.debug(f"Login successful for {user.username}")
    return Token(token=access_token, user=user)

async def register_user(user_data: UserCreate) -> dict:
    logger.debug(f"Registering user: username={user_data.username}, email={user_data.email}")
    existing_user = get_user_by_username(user_data.username) or get_user_by_email(user_data.email)
    if existing_user:
        logger.warning(f"User already exists: username={user_data.username}, email={user_data.email}")
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    password_hash = hash_password(user_data.password)
    
    profile = {
        "whatsappNumber": user_data.whatsappNumber,
        "address": user_data.address or None,
        "panelBrand": user_data.panelBrand or None,
        "panelCapacity": user_data.panelCapacity,
        "panelType": user_data.panelType or None,
        "inverterBrand": user_data.inverterBrand or None,
        "inverterCapacity": user_data.inverterCapacity
    }
    profile = {k: v for k, v in profile.items() if v is not None}
    
    user_dict = {
        "id": str(uuid.uuid4()),
        "username": user_data.username,
        "name": user_data.name,
        "email": user_data.email,
        "password_hash": password_hash,
        "usertype": user_data.userType,
        "profile": profile,
        "verified": False,
        "created_at": datetime.utcnow().isoformat(),  # Convert to string
        "last_login": None,
        "updated_at": None
    }
    try:
        created_user = await create_user(user_dict)
        logger.debug(f"User created: {created_user['username']}")
        
        otp = generate_otp()
        await redis_client.setex(f"otp:{user_data.email}", 600, otp)
        await redis_client.setex(f"user:{user_data.email}", 600, json.dumps(user_dict))
        await send_otp_email(user_data.email, otp)
        
        return {"email": user_data.email, "message": "OTP sent to email"}
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

async def verify_otp(otp_data: OTPVerify) -> Token:
    logger.debug(f"Verifying OTP for email: {otp_data.email}")
    stored_otp = await redis_client.get(f"otp:{otp_data.email}")
    if not stored_otp:
        logger.warning(f"OTP not found or expired for email: {otp_data.email}")
        raise HTTPException(status_code=400, detail="OTP not found or expired")
    if stored_otp.decode() != otp_data.otp:
        logger.warning(f"Invalid OTP for email: {otp_data.email}")
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    user_dict_str = await redis_client.get(f"user:{otp_data.email}")
    if not user_dict_str:
        logger.error(f"User data not found for email: {otp_data.email}")
        raise HTTPException(status_code=400, detail="User data not found")
    
    user_dict = json.loads(user_dict_str.decode())
    try:
        verified_user = await verify_user(otp_data.email)
        if not verified_user:
            logger.error(f"Failed to verify user: {otp_data.email}")
            raise HTTPException(status_code=500, detail="Failed to verify user")
        
        user_out = UserOut(**verified_user)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_out.username, "userType": user_out.userType}, expires_delta=access_token_expires
        )
        
        await redis_client.delete(f"otp:{otp_data.email}")
        await redis_client.delete(f"user:{otp_data.email}")
        
        return Token(token=access_token, user=user_out)
    except Exception as e:
        logger.error(f"Failed to verify OTP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify OTP: {str(e)}")