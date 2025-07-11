"""
User schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    role: str = "analyst"
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    organization_id: UUID


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None


class UserInDBBase(UserBase):
    """Base user schema with database fields"""
    id: UUID
    organization_id: UUID
    is_superuser: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    login_count: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class User(UserInDBBase):
    """User schema for API responses"""
    pass


class UserResponse(UserInDBBase):
    """User response schema (without sensitive data)"""
    full_name: str
    initials: str
    
    class Config:
        orm_mode = True


class UserInDB(UserInDBBase):
    """User schema with hashed password"""
    hashed_password: str
