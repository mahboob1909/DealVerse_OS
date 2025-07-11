"""
API dependencies
"""
from typing import Generator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.db.database import get_db
from app.models.user import User

# Security scheme
security_scheme = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> User:
    """Get current authenticated user with enhanced security"""
    # Verify token and get full payload
    payload = security.verify_access_token(credentials)
    user_id = payload.get("sub")

    # Get user from database
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Add token payload to user object for additional context
    user._token_payload = payload

    return user


def check_permission(required_permission: str):
    """Dependency to check user permissions"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not security.check_permission(current_user.role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {required_permission}"
            )
        return current_user
    return permission_checker


def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current active superuser"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not crud_user.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active superuser"""
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges"
        )
    return current_user


def check_user_organization(
    organization_id: UUID,
    current_user: User = Depends(get_current_user)
) -> User:
    """Check if user belongs to the specified organization"""
    if current_user.organization_id != organization_id and not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this organization"
        )
    return current_user


def check_user_role(allowed_roles: list):
    """Check if user has one of the allowed roles"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles and not crud_user.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


def check_permission(required_permission: str):
    """Check if user has required permission"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not security.check_permission(current_user.role, required_permission) and not crud_user.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission}"
            )
        return current_user
    return permission_checker
