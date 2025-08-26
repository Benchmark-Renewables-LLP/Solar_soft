from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Dict, Any
from datetime import datetime

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
    whatsappNumber: str = Field(..., pattern=r"^\+?[1-9]\d{9,14}$")
    address: str | None = None
    panelBrand: str | None = None
    panelCapacity: float | None = None
    panelType: str | None = None
    inverterBrand: str | None = None
    inverterCapacity: float | None = None
    profile: Dict[str, Any] = {}

    # Custom validation for installer fields
    model_config = {"extra": "forbid"}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_installer_fields

    @classmethod
    def validate_installer_fields(cls, values):
        if values.get("userType") == "installer":
            required_fields = ["address", "panelBrand", "panelCapacity", "panelType", "inverterBrand", "inverterCapacity"]
            for field in required_fields:
                if values.get(field) is None:
                    raise ValueError(f"{field} is required for installers")
        return values

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    userType: Literal["customer", "installer"]

class UserOut(UserBase):
    id: str
    profile: Dict[str, Any]
    created_at: datetime | None
    last_login: datetime | None

class Token(BaseModel):
    token: str
    user: UserOut