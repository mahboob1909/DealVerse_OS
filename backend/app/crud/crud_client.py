"""
CRUD operations for Client model
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.crud.base import CRUDBase
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    """CRUD operations for Client"""
    
    def get_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        client_type: Optional[str] = None,
        industry: Optional[str] = None
    ) -> List[Client]:
        """Get clients by organization with optional filters"""
        query = db.query(Client).filter(Client.organization_id == organization_id)
        
        if client_type:
            query = query.filter(Client.client_type == client_type)
        if industry:
            query = query.filter(Client.industry == industry)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[Client]:
        """Get client by email"""
        return db.query(Client).filter(Client.email == email).first()
    
    def search_clients(
        self,
        db: Session,
        *,
        organization_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Client]:
        """Search clients by name, company, or email"""
        search_filter = f"%{query}%"
        return (
            db.query(Client)
            .filter(
                and_(
                    Client.organization_id == organization_id,
                    (
                        Client.name.ilike(search_filter) |
                        Client.company.ilike(search_filter) |
                        Client.email.ilike(search_filter)
                    )
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recent_clients(
        self, db: Session, *, organization_id: UUID, limit: int = 10
    ) -> List[Client]:
        """Get recent clients for organization"""
        return (
            db.query(Client)
            .filter(Client.organization_id == organization_id)
            .order_by(Client.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_organization_stats(self, db: Session, *, organization_id: UUID) -> Dict[str, Any]:
        """Get client statistics for organization"""
        
        # Basic counts
        total_clients = db.query(Client).filter(Client.organization_id == organization_id).count()
        prospects = db.query(Client).filter(
            and_(Client.organization_id == organization_id, Client.client_type == "prospect")
        ).count()
        active_clients = db.query(Client).filter(
            and_(Client.organization_id == organization_id, Client.client_type == "active")
        ).count()
        inactive_clients = db.query(Client).filter(
            and_(Client.organization_id == organization_id, Client.client_type == "inactive")
        ).count()
        
        # Clients by type
        type_counts = db.query(Client.client_type, func.count(Client.id)).filter(
            Client.organization_id == organization_id
        ).group_by(Client.client_type).all()
        clients_by_type = {client_type: count for client_type, count in type_counts}
        
        # Clients by industry
        industry_counts = db.query(Client.industry, func.count(Client.id)).filter(
            and_(Client.organization_id == organization_id, Client.industry.isnot(None))
        ).group_by(Client.industry).all()
        clients_by_industry = {industry: count for industry, count in industry_counts}
        
        # Clients by source
        source_counts = db.query(Client.source, func.count(Client.id)).filter(
            and_(Client.organization_id == organization_id, Client.source.isnot(None))
        ).group_by(Client.source).all()
        clients_by_source = {source: count for source, count in source_counts}
        
        # Recent clients
        recent_clients_raw = self.get_recent_clients(db, organization_id=organization_id, limit=5)

        # Convert Client objects to dictionaries for serialization
        recent_clients = []
        for client in recent_clients_raw:
            recent_clients.append({
                "id": str(client.id),
                "name": client.name,
                "company": client.company,
                "email": client.email,
                "client_type": client.client_type,
                "relationship_status": client.relationship_status,
                "industry": client.industry,
                "created_at": client.created_at.isoformat(),
                "updated_at": client.updated_at.isoformat()
            })
        
        return {
            "total_clients": total_clients,
            "prospects": prospects,
            "active_clients": active_clients,
            "inactive_clients": inactive_clients,
            "clients_by_type": clients_by_type,
            "clients_by_industry": clients_by_industry,
            "clients_by_source": clients_by_source,
            "recent_clients": recent_clients
        }


crud_client = CRUDClient(Client)
