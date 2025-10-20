from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, description="Username")
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=6, description="Password")
    userType: str = Field(..., description="User type: 'customer' or 'installer'")
    whatsappNumber: str = Field(..., description="WhatsApp number")
    address: Optional[str] = Field(None, description="Address")
    panelBrand: Optional[str] = Field(None, description="Panel brand")
    panelCapacity: Optional[float] = Field(None, description="Panel capacity in kW")
    panelType: Optional[str] = Field(None, description="Panel type")
    inverterBrand: Optional[str] = Field(None, description="Inverter brand")
    inverterCapacity: Optional[float] = Field(None, description="Inverter capacity in kW")

class UserLogin(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    userType: str = Field(..., description="User type: 'customer' or 'installer'")

class OTPVerify(BaseModel):
    email: EmailStr = Field(..., description="Email")
    otp: str = Field(..., description="6-digit OTP")

class Token(BaseModel):
    token: str = Field(..., description="Access token")
    user: Optional[dict] = Field(None, description="User details")

class UserOut(BaseModel):
    id: str
    username: str
    name: str
    email: str
    userType: str
    verified: bool
    profile: dict
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email")
    profile: Optional[dict] = Field(None, description="Profile updates")