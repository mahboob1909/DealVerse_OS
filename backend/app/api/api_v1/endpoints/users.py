"""
User management endpoints
"""
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_user import crud_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    password: str = None,
    first_name: str = None,
    last_name: str = None,
    phone: str = None,
    title: str = None,
    department: str = None,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user
    """
    current_user_data = {}
    if password is not None:
        current_user_data["password"] = password
    if first_name is not None:
        current_user_data["first_name"] = first_name
    if last_name is not None:
        current_user_data["last_name"] = last_name
    if phone is not None:
        current_user_data["phone"] = phone
    if title is not None:
        current_user_data["title"] = title
    if department is not None:
        current_user_data["department"] = department
    
    user = crud_user.update(db, db_obj=current_user, obj_in=current_user_data)
    return user


@router.get("/", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users from the same organization
    """
    users = crud_user.get_by_organization(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return users


@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.check_permission("users:create")),
) -> Any:
    """
    Create new user
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Ensure user is created in the same organization
    user_in.organization_id = current_user.organization_id
    user = crud_user.create(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
    user_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    # Check if user is in the same organization
    if user.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(deps.check_permission("users:edit")),
) -> Any:
    """
    Update a user
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    # Check if user is in the same organization
    if user.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: User = Depends(deps.check_permission("users:delete")),
) -> Any:
    """
    Delete a user
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    # Check if user is in the same organization
    if user.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself"
        )
    
    user = crud_user.remove(db, id=user_id)
    return {"message": "User deleted successfully"}
