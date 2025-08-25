from fastapi import APIRouter, Depends, HTTPException
from backend.models.user import UserOut, UserProfileUpdate
from backend.services.auth_service import get_current_user, update_user_profile
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.get("/profile", response_model=UserOut)
async def get_profile(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserOut)
async def update_profile(update_data: UserProfileUpdate, current_user: UserOut = Depends(get_current_user)):
    return await update_user_profile(current_user.id, update_data.name, update_data.profile)