from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..utils.db_utils import get_db  # Assuming DB dependency in db_utils.py
from ..repositories.plant_repository import get_all_plants  # From your repositories
from ..repositories.device_repository import get_all_devices

router = APIRouter(prefix="/api", tags=["data"])

@router.get("/plants")
async def get_plants(db: Session = Depends(get_db)):
    try:
        plants = get_all_plants(db)  # Assume this function exists in plant_repository.py
        return plants
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/devices")
async def get_devices(db: Session = Depends(get_db)):
    try:
        devices = get_all_devices(db)  # Assume this function exists in device_repository.py
        return devices
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))