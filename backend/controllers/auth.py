from fastapi import APIRouter, Depends, HTTPException, status
from typing import Union
from datetime import timedelta
from backend.services.auth_service import login_user, register_user, verify_otp
from backend.models.user import UserLogin, UserCreate, OTPVerify, Token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    try:
        token = await login_user(login_data)
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/register")
async def register(user_data: UserCreate):
    try:
        result = await register_user(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/verify-otp", response_model=Token)
async def verify_otp_endpoint(otp_data: OTPVerify):
    try:
        token = await verify_otp(otp_data)
        return token
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OTP verification failed: {str(e)}")