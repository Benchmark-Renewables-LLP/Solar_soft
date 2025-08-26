from fastapi import APIRouter, Request, HTTPException, status
from backend.models.user import UserCreate, UserLogin, Token
from backend.services.auth_service import login_user, register_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(request: Request, user_credentials: UserLogin):
    logger.debug(f"Raw request body: {await request.body()}")
    logger.debug(f"Parsed login payload: {user_credentials}")
    return await login_user(user_credentials)

@router.post("/register", response_model=Token)
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