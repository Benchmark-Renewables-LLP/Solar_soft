import sys
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from services.auth_service import AuthService
from utils.db_utils import get_db
from utils.jwt_utils import create_token  # If you have custom JWT, else use service's

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

router = APIRouter()

auth_service = AuthService()

# Dependency for DB
db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/register")
async def register(user: UserRegister, db: db_dependency):
    logger.debug(f"Received register request: {user.dict()}")
    try:
        token = await auth_service.register(user.dict(), db)
        logger.info(f"User {user.username} registered successfully")
        return {"token": token}
    except ValueError as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in register: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/login")
async def login(user: UserLogin, db: db_dependency):
    logger.debug(f"Received login request: {user.dict()}")
    try:
        token = await auth_service.login(user.username, user.password, user.isInstaller, db)
        logger.info(f"User {user.username} logged in successfully")
        return {"token": token}
    except ValueError as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")