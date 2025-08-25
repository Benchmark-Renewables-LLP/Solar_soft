from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Dict, Any

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2)
    email: EmailStr
    userType: Literal["customer", "installer"]

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)  # Relaxed from 8
    profile: Dict[str, Any] = {}

class UserLogin(BaseModel):
    username: str
    password: str
    userType: Literal["customer", "installer"]
     
class UserOut(UserBase):
    id: str
    profile: Dict[str, Any]
    created_at: str | None
    last_login: str | None

class Token(BaseModel):
    token: str
    user: UserOut