"""
Organization management endpoints
"""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_organization import crud_organization
from app.db.database import get_db
from app.models.user import User
from app.schemas.organization import Organization, OrganizationUpdate, OrganizationResponse

router = APIRouter()


@router.get("/me", response_model=OrganizationResponse)
def read_organization_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's organization
    """
    organization = crud_organization.get(db, id=current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.put("/me", response_model=OrganizationResponse)
def update_organization_me(
    *,
    db: Session = Depends(get_db),
    organization_in: OrganizationUpdate,
    current_user: User = Depends(deps.check_permission("organizations:edit")),
) -> Any:
    """
    Update current user's organization
    """
    organization = crud_organization.get(db, id=current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    organization = crud_organization.update(db, db_obj=organization, obj_in=organization_in)
    return organization


@router.get("/{organization_id}", response_model=OrganizationResponse)
def read_organization(
    *,
    db: Session = Depends(get_db),
    organization_id: UUID,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get organization by ID (superuser only)
    """
    organization = crud_organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.get("/me/stats")
def get_organization_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization statistics
    """
    stats = crud_organization.get_organization_stats(db, organization_id=current_user.organization_id)
    return stats


@router.get("/me/settings")
def get_organization_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization settings
    """
    organization = crud_organization.get(db, id=current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return {
        "settings": organization.settings or {},
        "subscription_tier": organization.subscription_tier,
        "subscription_status": organization.subscription_status
    }


@router.put("/me/settings")
def update_organization_settings(
    *,
    db: Session = Depends(get_db),
    settings: dict,
    current_user: User = Depends(deps.check_permission("organizations:edit")),
) -> Any:
    """
    Update organization settings
    """
    organization = crud_organization.get(db, id=current_user.organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    organization.settings = settings
    db.add(organization)
    db.commit()
    db.refresh(organization)
    
    return {"message": "Settings updated successfully", "settings": organization.settings}
