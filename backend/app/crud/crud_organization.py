"""
CRUD operations for Organization model
"""
from typing import Any, Dict, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    """CRUD operations for Organization"""
    
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        return db.query(Organization).filter(Organization.slug == slug).first()
    
    def get_organization_stats(self, db: Session, *, organization_id: UUID) -> Dict[str, Any]:
        """Get comprehensive organization statistics"""
        
        # Import here to avoid circular imports
        from app.models.user import User
        from app.models.deal import Deal
        from app.models.client import Client
        from app.models.task import Task
        from app.models.document import Document
        
        # Get counts for all entities
        users_count = db.query(User).filter(User.organization_id == organization_id).count()
        deals_count = db.query(Deal).filter(Deal.organization_id == organization_id).count()
        clients_count = db.query(Client).filter(Client.organization_id == organization_id).count()
        tasks_count = db.query(Task).filter(Task.organization_id == organization_id).count()
        documents_count = db.query(Document).filter(Document.organization_id == organization_id).count()
        
        # Get active counts
        active_users = db.query(User).filter(
            User.organization_id == organization_id,
            User.is_active == True
        ).count()
        
        active_deals = db.query(Deal).filter(
            Deal.organization_id == organization_id,
            Deal.status == "active"
        ).count()
        
        # Get financial metrics
        total_deal_value = db.query(func.sum(Deal.deal_value)).filter(
            Deal.organization_id == organization_id
        ).scalar() or 0
        
        # Get recent activity counts (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_deals = db.query(Deal).filter(
            Deal.organization_id == organization_id,
            Deal.created_at >= thirty_days_ago
        ).count()
        
        recent_clients = db.query(Client).filter(
            Client.organization_id == organization_id,
            Client.created_at >= thirty_days_ago
        ).count()
        
        return {
            "overview": {
                "total_users": users_count,
                "active_users": active_users,
                "total_deals": deals_count,
                "active_deals": active_deals,
                "total_clients": clients_count,
                "total_tasks": tasks_count,
                "total_documents": documents_count
            },
            "financial": {
                "total_pipeline_value": float(total_deal_value),
                "average_deal_size": float(total_deal_value / deals_count) if deals_count > 0 else 0
            },
            "recent_activity": {
                "new_deals_30d": recent_deals,
                "new_clients_30d": recent_clients
            },
            "growth_metrics": {
                "user_growth_rate": 0,  # Calculate based on historical data
                "deal_growth_rate": 0,  # Calculate based on historical data
                "revenue_growth_rate": 0  # Calculate based on historical data
            }
        }


crud_organization = CRUDOrganization(Organization)
