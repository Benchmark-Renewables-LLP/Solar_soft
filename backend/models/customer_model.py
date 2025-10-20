from sqlalchemy import Column, Integer, String, Boolean, DateTime
from utils.db_utils import Base
from datetime import datetime
from pydantic import BaseModel

# SQLAlchemy Model for DB
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    fullname = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # Hashed
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    is_installer = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime)

# Pydantic Models for Validation (Your Existing)
class UserRegister(BaseModel):
    username: str
    fullname: str
    password: str
    confirmPassword: str
    isInstaller: bool = False
    email: str = None
    whatsappNumber: str = None
    address: str = None

class UserLogin(BaseModel):
    username: str
    password: str
    isInstaller: bool = False