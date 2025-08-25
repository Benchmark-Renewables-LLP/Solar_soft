from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from backend.models.user import UserLogin, Token
from backend.services.auth_service import login_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_credentials = UserLogin(
        username=form_data.username.strip(),
        password=form_data.password.strip(),
        userType=form_data.scope.strip() or "customer"
    )
    return await login_user(user_credentials)