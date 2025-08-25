from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Dict, Any
from datetime import datetime  # Add this import

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1)
    email: EmailStr
    userType: Literal["customer", "installer"]

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    userType: Literal["customer", "installer"]
    profile: Dict[str, Any] = {}

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    userType: Literal["customer", "installer"]

class UserOut(UserBase):
    id: str
    profile: Dict[str, Any]
    created_at: datetime | None  # Changed from str to datetime
    last_login: datetime | None  # Changed from str to datetime

class Token(BaseModel):
    token: str
    user: UserOut