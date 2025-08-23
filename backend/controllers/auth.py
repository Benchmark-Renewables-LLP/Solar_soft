from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from backend.models.user import UserCreate, UserLogin, Token
from backend.services.auth_service import register_user, login_user

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    created_user = await register_user(user)
    # Generate token after registration (optional; or return user and let client login)
    token = await login_user(UserLogin(username=user.username, password=user.password))
    return token

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_user(UserLogin(username=form_data.username, password=form_data.password))