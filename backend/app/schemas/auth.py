"""
Authentication schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: Optional[str] = None
    type: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    organization_id: UUID

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "first_name": "John",
                "last_name": "Doe",
                "organization_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class TokenRefresh(BaseModel):
    """Token refresh schema"""
    refresh_token: str


class PasswordChange(BaseModel):
    """Password change schema"""
    old_password: str
    new_password: str


class PasswordValidation(BaseModel):
    """Password validation response schema"""
    is_valid: bool
    score: int
    feedback: list[str]
    requirements_met: dict[str, bool]
