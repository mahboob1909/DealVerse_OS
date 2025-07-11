"""
Authentication endpoints with enhanced security
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import structlog

from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserRegister, TokenRefresh
from app.schemas.user import UserCreate, UserResponse
from app.db.database import get_db

logger = structlog.get_logger()

router = APIRouter()


@router.post("/login", response_model=Token)
def login_for_access_token(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login with enhanced security
    """
    # Get client information
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Check for account lockout
    if security.security_monitor.is_account_locked(form_data.username):
        logger.warning(
            "Login attempt on locked account",
            email=form_data.username,
            client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to multiple failed attempts"
        )

    # Authenticate user
    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )

    if not user:
        # Track failed attempt
        security.security_monitor.track_failed_attempt(form_data.username)

        logger.warning(
            "Failed login attempt",
            email=form_data.username,
            client_ip=client_ip,
            user_agent=user_agent
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(
            "Login attempt by inactive user",
            user_id=str(user.id),
            email=user.email,
            client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Clear failed attempts on successful login
    security.security_monitor.clear_failed_attempts(form_data.username)

    # Create secure session
    session_id = security.create_secure_session(
        str(user.id),
        user_agent=user_agent,
        ip_address=client_ip
    )

    # Create tokens with session ID
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id,
        expires_delta=access_token_expires,
        session_id=session_id,
        additional_claims={
            "role": user.role,
            "org_id": str(user.organization_id)
        }
    )
    refresh_token = security.create_refresh_token(user.id, session_id=session_id)

    logger.info(
        "Successful login",
        user_id=str(user.id),
        email=user.email,
        client_ip=client_ip,
        session_id=session_id[:16]
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/json", response_model=Token)
def login_json(
    request: Request,
    user_in: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    JSON login endpoint with enhanced security
    """
    # Get client information
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Check for account lockout
    if security.security_monitor.is_account_locked(user_in.email):
        logger.warning(
            "JSON login attempt on locked account",
            email=user_in.email,
            client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to multiple failed attempts"
        )

    # Authenticate user
    user = crud_user.authenticate(
        db, email=user_in.email, password=user_in.password
    )

    if not user:
        # Track failed attempt
        security.security_monitor.track_failed_attempt(user_in.email)

        logger.warning(
            "Failed JSON login attempt",
            email=user_in.email,
            client_ip=client_ip
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        logger.warning(
            "JSON login attempt by inactive user",
            user_id=str(user.id),
            email=user.email,
            client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Clear failed attempts on successful login
    security.security_monitor.clear_failed_attempts(user_in.email)

    # Create secure session
    session_id = security.create_secure_session(
        str(user.id),
        user_agent=user_agent,
        ip_address=client_ip
    )

    # Create tokens with session ID
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id,
        expires_delta=access_token_expires,
        session_id=session_id,
        additional_claims={
            "role": user.role,
            "org_id": str(user.organization_id)
        }
    )
    refresh_token = security.create_refresh_token(user.id, session_id=session_id)

    logger.info(
        "Successful JSON login",
        user_id=str(user.id),
        email=user.email,
        client_ip=client_ip,
        session_id=session_id[:16]
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserResponse)
def register(
    user_in: UserRegister,
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new user account
    """
    # Check if user already exists
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system"
        )
    
    # Create user
    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        organization_id=user_in.organization_id
    )
    user = crud_user.create(db, obj_in=user_create)
    
    return user


@router.post("/refresh", response_model=Token)
def refresh_token(
    request: Request,
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token with enhanced security
    """
    # Get client information
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    # Verify refresh token
    payload = security.verify_token(token_data.refresh_token, "refresh")
    if not payload:
        logger.warning(
            "Invalid refresh token used",
            client_ip=client_ip,
            user_agent=user_agent
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    session_id = payload.get("sid")

    # Get user from database
    user = crud_user.get(db, id=user_id)
    if not user or not user.is_active:
        logger.warning(
            "Refresh token used for invalid/inactive user",
            user_id=user_id,
            client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Invalidate old refresh token
    security.invalidate_token(token_data.refresh_token)

    # Create new tokens with same session ID
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id,
        expires_delta=access_token_expires,
        session_id=session_id,
        additional_claims={
            "role": user.role,
            "org_id": str(user.organization_id)
        }
    )
    new_refresh_token = security.create_refresh_token(user.id, session_id=session_id)

    logger.info(
        "Token refreshed successfully",
        user_id=str(user.id),
        session_id=session_id[:16] if session_id else "unknown",
        client_ip=client_ip
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Logout current user and invalidate tokens
    """
    # Get client information
    client_ip = request.client.host if request.client else "unknown"

    # Get token from request
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Invalidate the current access token
        security.invalidate_token(token)

    # Get session ID from token payload if available
    if hasattr(current_user, '_token_payload'):
        session_id = current_user._token_payload.get("sid")
        if session_id:
            security.token_manager.invalidate_session(str(current_user.id), session_id)

    logger.info(
        "User logged out",
        user_id=str(current_user.id),
        email=current_user.email,
        client_ip=client_ip
    )

    return {"message": "Successfully logged out"}


@router.post("/logout-all")
def logout_all_sessions(
    request: Request,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Logout from all sessions and invalidate all tokens for the user
    """
    # Get client information
    client_ip = request.client.host if request.client else "unknown"

    # Invalidate all user sessions and tokens
    security.invalidate_all_user_tokens(str(current_user.id))

    logger.info(
        "All sessions logged out",
        user_id=str(current_user.id),
        email=current_user.email,
        client_ip=client_ip
    )

    return {"message": "Successfully logged out from all sessions"}


@router.post("/change-password")
def change_password(
    request: Request,
    old_password: str,
    new_password: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change user password with enhanced security validation
    """
    # Get client information
    client_ip = request.client.host if request.client else "unknown"

    # Verify old password
    if not security.verify_password(old_password, current_user.hashed_password):
        logger.warning(
            "Failed password change attempt - incorrect old password",
            user_id=str(current_user.id),
            client_ip=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Validate new password strength
    password_validation = security.validate_password_strength(new_password)
    if not password_validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Password does not meet security requirements",
                "feedback": password_validation["feedback"],
                "score": password_validation["score"]
            }
        )

    # Update password
    hashed_password = security.get_password_hash(new_password)
    crud_user.update(db, db_obj=current_user, obj_in={"hashed_password": hashed_password})

    # Invalidate all existing sessions to force re-login
    security.invalidate_all_user_tokens(str(current_user.id))

    logger.info(
        "Password changed successfully",
        user_id=str(current_user.id),
        client_ip=client_ip,
        password_score=password_validation["score"]
    )

    return {"message": "Password changed successfully. Please log in again."}
