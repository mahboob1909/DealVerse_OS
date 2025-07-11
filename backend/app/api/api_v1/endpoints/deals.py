"""
Deal management endpoints
"""
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_deal import crud_deal
from app.db.database import get_db
from app.models.user import User
from app.schemas.deal import Deal, DealCreate, DealUpdate, DealResponse
from app.middleware.cache_middleware import cache_response, invalidate_cache_on_change
from app.services.cache_service import cache_service, cached

router = APIRouter()


@router.get("/", response_model=List[DealResponse])
@cache_response(ttl=180, key_prefix="deals_list")
def read_deals(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    stage: str = Query(None, description="Filter by deal stage"),
    status: str = Query(None, description="Filter by deal status"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve deals for the current user's organization with caching
    """
    # Generate cache key including user context
    cache_key = cache_service._generate_key(
        "deals_list",
        str(current_user.organization_id),
        skip, limit, stage, status
    )

    # Try cache first
    cached_deals = cache_service.get(cache_key)
    if cached_deals is not None:
        return cached_deals

    # Get deals with relations for better performance
    deals = crud_deal.get_by_organization(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        stage=stage,
        status=status,
        include_relations=True
    )

    # Cache the result
    cache_service.set(cache_key, deals, ttl=180)

    return deals


@router.post("/", response_model=DealResponse)
@invalidate_cache_on_change([
    "dealverse:api:*deals*",
    "dealverse:api:*dashboard*",
    "dealverse:deals_list:*"
])
def create_deal(
    *,
    db: Session = Depends(get_db),
    deal_in: DealCreate,
    current_user: User = Depends(deps.check_permission("deals:create")),
) -> Any:
    """
    Create new deal with cache invalidation
    """
    # Add organization and creator info
    deal_data = deal_in.dict()
    deal_data["organization_id"] = current_user.organization_id
    deal_data["created_by_id"] = current_user.id
    
    deal = crud_deal.create(db=db, obj_in=deal_data)
    return deal


@router.get("/{deal_id}", response_model=DealResponse)
def read_deal(
    *,
    db: Session = Depends(get_db),
    deal_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get deal by ID
    """
    deal = crud_deal.get(db=db, id=deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Check if user has access to this deal's organization
    if deal.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return deal


@router.put("/{deal_id}", response_model=DealResponse)
def update_deal(
    *,
    db: Session = Depends(get_db),
    deal_id: UUID,
    deal_in: DealUpdate,
    current_user: User = Depends(deps.check_permission("deals:edit")),
) -> Any:
    """
    Update deal
    """
    deal = crud_deal.get(db=db, id=deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Check if user has access to this deal's organization
    if deal.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    deal = crud_deal.update(db=db, db_obj=deal, obj_in=deal_in)
    return deal


@router.delete("/{deal_id}")
def delete_deal(
    *,
    db: Session = Depends(get_db),
    deal_id: UUID,
    current_user: User = Depends(deps.check_permission("deals:delete")),
) -> Any:
    """
    Delete deal
    """
    deal = crud_deal.get(db=db, id=deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Check if user has access to this deal's organization
    if deal.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    deal = crud_deal.remove(db=db, id=deal_id)
    return {"message": "Deal deleted successfully"}


@router.get("/{deal_id}/team")
def get_deal_team(
    *,
    db: Session = Depends(get_db),
    deal_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get deal team members
    """
    deal = crud_deal.get(db=db, id=deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Check if user has access to this deal's organization
    if deal.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return {"deal_team": deal.deal_team or []}


@router.post("/{deal_id}/team")
def add_team_member(
    *,
    db: Session = Depends(get_db),
    deal_id: UUID,
    user_id: UUID,
    role: str,
    current_user: User = Depends(deps.check_permission("deals:edit")),
) -> Any:
    """
    Add team member to deal
    """
    deal = crud_deal.get(db=db, id=deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Check if user has access to this deal's organization
    if deal.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Add team member
    team = deal.deal_team or []
    team_member = {"user_id": str(user_id), "role": role}
    
    # Check if user is already in team
    if not any(member["user_id"] == str(user_id) for member in team):
        team.append(team_member)
        deal.deal_team = team
        db.add(deal)
        db.commit()
        db.refresh(deal)
    
    return {"message": "Team member added successfully", "deal_team": deal.deal_team}


@router.get("/stats/summary")
def get_deals_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get deals summary statistics
    """
    stats = crud_deal.get_organization_stats(db, organization_id=current_user.organization_id)
    return stats
