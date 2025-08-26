from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    userType: Literal["customer", "installer"]

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    userType: Literal["customer", "installer"]
    whatsappNumber: str = Field(..., pattern=r"^\+?[1-9]\d{9,14}$")
    address: str | None = None
    panelBrand: str | None = None
    panelCapacity: float | None = None
    panelType: str | None = None
    inverterBrand: str | None = None
    inverterCapacity: float | None = None
    profile: Dict[str, Any] = {}

    model_config = {"extra": "forbid"}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_installer_fields
        yield cls.validate_password

    @classmethod
    def validate_installer_fields(cls, values):
        if values.get("userType") == "installer":
            required_fields = ["address", "panelBrand", "panelCapacity", "panelType", "inverterBrand", "inverterCapacity"]
            for field in required_fields:
                if values.get(field) is None:
                    raise ValueError(f"{field} is required for installers")
        return values

    @classmethod
    def validate_password(cls, values):
        password = values.get("password")
        if password:
            if not (any(c.islower() for c in password) and
                    any(c.isupper() for c in password) and
                    any(c.isdigit() for c in password) and
                    any(c in "@$!%*?&" for c in password)):
                raise ValueError("Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character (@$!%*?&)")
        return values

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=6)  # Relaxed to 6 characters
    userType: Literal["customer", "installer"]

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

class UserOut(BaseModel):
    id: str
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    userType: Literal["customer", "installer"]
    profile: Dict[str, Any]
    verified: bool
    created_at: datetime | None
    last_login: datetime | None

class Token(BaseModel):
    token: str
    user: UserOut