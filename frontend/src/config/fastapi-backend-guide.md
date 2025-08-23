
# FastAPI Backend Implementation Guide for Solar PV Dashboard

## Prerequisites

### Required Python Packages
```bash
pip install fastapi uvicorn python-multipart
pip install sqlalchemy psycopg2-binary asyncpg
pip install python-jose[cryptography] passlib[bcrypt]
pip install google-auth google-auth-oauthlib
pip install pydantic[email] python-dotenv
pip install celery redis  # For background tasks
pip install alembic  # For database migrations
```

### Environment Variables (.env)
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/solar_timeseries
TIMESCALE_DB_URL=postgresql://username:password@localhost:5432/solar_timeseries

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# FastAPI Configuration
DEBUG=True
CORS_ORIGINS=http://localhost:5173,https://your-frontend-domain.com
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── plant.py
│   │   ├── device.py
│   │   └── timeseries.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── plant.py
│   │   ├── device.py
│   │   └── timeseries.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   ├── google_auth.py
│   │   └── jwt_handler.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── plants.py
│   │   ├── devices.py
│   │   └── timeseries.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_collector.py
│   │   └── aggregator.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── alembic/
├── requirements.txt
└── .env
```

## Core Configuration (app/config.py)

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # FastAPI
    app_name: str = "Solar PV Dashboard API"
    debug: bool = True
    
    # Database
    database_url: str
    timescale_db_url: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    
    # Google OAuth
    google_client_id: str
    google_client_secret: str
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Database Setup (app/database.py)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Async database engine
engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Dependency for getting database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

## Pydantic Schemas (app/schemas/auth.py)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    token: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

## SQLAlchemy Models (app/models/user.py)

```python
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # NULL for Google OAuth
    google_id = Column(String(255), unique=True, nullable=True)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## JWT Authentication (app/auth/jwt_handler.py)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None
```

## Authentication Dependencies (app/auth/dependencies.py)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.auth.jwt_handler import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user
```

## Google OAuth (app/auth/google_auth.py)

```python
from google.auth.transport import requests
from google.oauth2 import id_token
from app.config import settings
from typing import Optional, Dict

async def verify_google_token(token: str) -> Optional[Dict]:
    try:
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.google_client_id
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return None
            
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo['name'],
            'picture': idinfo.get('picture')
        }
    except ValueError:
        return None
```

## Authentication Routes (app/api/auth.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, GoogleLoginRequest
from app.auth.jwt_handler import verify_password, get_password_hash, create_access_token
from app.auth.google_auth import verify_google_token
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return {
        "access_token": access_token,
        "user": new_user
    }

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "user": user
    }

@router.post("/google", response_model=TokenResponse)
async def google_login(google_data: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    user_info = await verify_google_token(google_data.token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_info['email']))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user from Google OAuth
        user = User(
            name=user_info['name'],
            email=user_info['email'],
            google_id=user_info['google_id'],
            password_hash=None
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "user": user
    }
```

## Main Application (app/main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api import auth, plants, devices, timeseries

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await init_db()
    yield

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(plants.router)
app.include_router(devices.router)
app.include_router(timeseries.router)

@app.get("/")
async def root():
    return {"message": "Solar PV Dashboard API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

## Background Data Collection (app/services/data_collector.py)

```python
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import asyncio
from app.database import AsyncSessionLocal
from app.models.device import Device
from app.models.timeseries import DeviceMetrics

# Celery configuration
celery_app = Celery(
    "solar_dashboard",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def collect_all_device_data():
    asyncio.run(_collect_all_device_data())

async def _collect_all_device_data():
    async with AsyncSessionLocal() as db:
        # Get all active devices
        result = await db.execute(select(Device).where(Device.status == 'online'))
        devices = result.scalars().all()
        
        for device in devices:
            await collect_device_data(device.id, db)

async def collect_device_data(device_id: str, db: AsyncSession):
    # Simulate data collection from actual solar equipment
    data = generate_demo_data()
    
    # Store metrics
    for metric_type, values in data.items():
        if isinstance(values, list):
            for i, value in enumerate(values):
                metric = DeviceMetrics(
                    time=datetime.utcnow(),
                    device_id=device_id,
                    metric_type=metric_type,
                    metric_name=f"PV{i+1}",
                    value=value,
                    unit="V" if "voltage" in metric_type else "A"
                )
                db.add(metric)
        else:
            metric = DeviceMetrics(
                time=datetime.utcnow(),
                device_id=device_id,
                metric_type=metric_type,
                metric_name="total",
                value=values,
                unit="W"
            )
            db.add(metric)
    
    await db.commit()

# Schedule task to run every 5 minutes
celery_app.conf.beat_schedule = {
    'collect-data-every-5-minutes': {
        'task': 'app.services.data_collector.collect_all_device_data',
        'schedule': 300.0,  # 5 minutes
    },
}
```

## Run Scripts

### Development Server (run_dev.py)
```python
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### Celery Worker (run_celery.py)
```python
from app.services.data_collector import celery_app

if __name__ == "__main__":
    celery_app.start()
```

## API Endpoints Summary

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/google` - Google OAuth login

### Plants & Devices
- `GET /api/plants` - Get user's plants
- `GET /api/plants/{plant_id}` - Get plant details
- `GET /api/devices` - Get user's devices
- `GET /api/devices/{device_id}` - Get device details
- `GET /api/devices/{device_id}/timeseries` - Get time-series data

## Database Migration

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Running the Application

```bash
# Start FastAPI server
python run_dev.py

# Start Celery worker (in another terminal)
celery -A app.services.data_collector worker --loglevel=info

# Start Celery beat scheduler (in another terminal)
celery -A app.services.data_collector beat --loglevel=info
```

## Key Differences from Flask

1. **Async/Await**: FastAPI uses async programming for better performance
2. **Type Hints**: Pydantic schemas provide automatic validation and documentation
3. **Dependency Injection**: FastAPI's dependency system is more powerful
4. **Auto Documentation**: Swagger UI available at `/docs`
5. **Performance**: Generally faster than Flask due to async nature

## Advantages of FastAPI

- **High Performance**: Comparable to NodeJS and Go
- **Type Safety**: Built-in validation with Pydantic
- **Auto Documentation**: Interactive API docs
- **Modern Python**: Uses latest Python features
- **Easy Testing**: Built-in testing client
