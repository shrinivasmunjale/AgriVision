from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    full_name: Optional[str] = None
    farm_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str
    role: Optional[str] = "farmer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    farm_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
