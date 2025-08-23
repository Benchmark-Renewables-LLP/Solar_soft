from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: Literal["viewer", "installer"]  # As per project: user (viewer) and admin (installer)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)  # Plaintext input; hashed in service

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(UserBase):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"