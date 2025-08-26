from fastapi import APIRouter, Request, HTTPException, status
from backend.models.user import UserCreate, UserLogin, Token, OTPVerify
from backend.services.auth_service import login_user, register_user, verify_otp
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(request: Request, user_credentials: UserLogin):
    logger.debug(f"Raw request body: {await request.body()}")
    logger.debug(f"Parsed login payload: {user_credentials}")
    return await login_user(user_credentials)

@router.post("/register")
async def register(request: Request, user_data: UserCreate):
    logger.debug(f"Raw register body: {await request.body()}")
    logger.debug(f"Parsed register payload: {user_data}")
    try:
        return await register_user(user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/verify-otp", response_model=Token)
async def verify(request: Request, otp_data: OTPVerify):
    logger.debug(f"Raw OTP verification body: {await request.body()}")
    logger.debug(f"Parsed OTP verification payload: {otp_data}")
    try:
        return await verify_otp(otp_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"OTP verification failed: {e}")
        raise HTTPException(status_code=500, detail="OTP verification failed")

@router.post("/logout")
async def logout(request: Request):
    logger.debug(f"Logout request received")
    return {"message": "Logged out successfully"}