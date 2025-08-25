from fastapi import APIRouter, Request
from backend.models.user import UserLogin, Token
from backend.services.auth_service import login_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(request: Request, user_credentials: UserLogin):
    raw_body = await request.body()
    logger.debug(f"Raw request body: {raw_body.decode('utf-8')}")
    logger.debug(f"Parsed login payload: {user_credentials}")
    return await login_user(user_credentials)