"""
Client management endpoints
"""
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_client import crud_client
from app.db.database import get_db
from app.models.user import User
from app.schemas.client import Client, ClientCreate, ClientUpdate, ClientResponse

router = APIRouter()


@router.get("/", response_model=List[ClientResponse])
def read_clients(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    client_type: str = Query(None, description="Filter by client type"),
    industry: str = Query(None, description="Filter by industry"),
    search: str = Query(None, description="Search by name or company"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve clients for the current user's organization
    """
    if search:
        clients = crud_client.search_clients(
            db,
            organization_id=current_user.organization_id,
            query=search,
            skip=skip,
            limit=limit
        )
    else:
        clients = crud_client.get_by_organization(
            db,
            organization_id=current_user.organization_id,
            skip=skip,
            limit=limit,
            client_type=client_type,
            industry=industry
        )
    return clients


@router.post("/", response_model=ClientResponse)
def create_client(
    *,
    db: Session = Depends(get_db),
    client_in: ClientCreate,
    current_user: User = Depends(deps.check_permission("clients:create")),
) -> Any:
    """
    Create new client
    """
    # Add organization info
    client_data = client_in.dict()
    client_data["organization_id"] = current_user.organization_id
    
    client = crud_client.create(db=db, obj_in=client_data)
    return client


@router.get("/{client_id}", response_model=ClientResponse)
def read_client(
    *,
    db: Session = Depends(get_db),
    client_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get client by ID
    """
    client = crud_client.get(db=db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if user has access to this client's organization
    if client.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    *,
    db: Session = Depends(get_db),
    client_id: UUID,
    client_in: ClientUpdate,
    current_user: User = Depends(deps.check_permission("clients:edit")),
) -> Any:
    """
    Update client
    """
    client = crud_client.get(db=db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if user has access to this client's organization
    if client.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    client = crud_client.update(db=db, db_obj=client, obj_in=client_in)
    return client


@router.delete("/{client_id}")
def delete_client(
    *,
    db: Session = Depends(get_db),
    client_id: UUID,
    current_user: User = Depends(deps.check_permission("clients:delete")),
) -> Any:
    """
    Delete client
    """
    client = crud_client.get(db=db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if user has access to this client's organization
    if client.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    client = crud_client.remove(db=db, id=client_id)
    return {"message": "Client deleted successfully"}


@router.get("/{client_id}/deals")
def get_client_deals(
    *,
    db: Session = Depends(get_db),
    client_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get deals for a specific client
    """
    client = crud_client.get(db=db, id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if user has access to this client's organization
    if client.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    from app.crud.crud_deal import crud_deal
    deals = crud_deal.get_by_client(db, client_id=client_id)
    return deals


@router.get("/stats/summary")
def get_clients_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get clients summary statistics
    """
    stats = crud_client.get_organization_stats(db, organization_id=current_user.organization_id)
    return stats
