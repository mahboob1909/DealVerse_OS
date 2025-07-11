"""
CRUD operations for Deal model
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_, desc

from app.crud.base import CRUDBase
from app.models.deal import Deal
from app.schemas.deal import DealCreate, DealUpdate


class CRUDDeal(CRUDBase[Deal, DealCreate, DealUpdate]):
    """CRUD operations for Deal"""
    
    def get_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        include_relations: bool = False
    ) -> List[Deal]:
        """Get deals by organization with optional filters and eager loading"""
        query = db.query(Deal).filter(Deal.organization_id == organization_id)

        # Add eager loading to prevent N+1 queries
        if include_relations:
            query = query.options(
                joinedload(Deal.client),
                joinedload(Deal.created_by),
                joinedload(Deal.organization),
                selectinload(Deal.tasks),
                selectinload(Deal.documents),
                selectinload(Deal.financial_models)
            )

        if stage:
            query = query.filter(Deal.stage == stage)
        if status:
            query = query.filter(Deal.status == status)

        # Add ordering for consistent results
        query = query.order_by(desc(Deal.updated_at))

        return query.offset(skip).limit(limit).all()
    
    def get_by_client(
        self,
        db: Session,
        *,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_relations: bool = False
    ) -> List[Deal]:
        """Get deals by client with optional eager loading"""
        query = db.query(Deal).filter(Deal.client_id == client_id)

        # Add eager loading to prevent N+1 queries
        if include_relations:
            query = query.options(
                joinedload(Deal.client),
                joinedload(Deal.created_by),
                joinedload(Deal.organization),
                selectinload(Deal.tasks),
                selectinload(Deal.documents)
            )

        return (
            query
            .order_by(desc(Deal.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_user(
        self,
        db: Session,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_relations: bool = False
    ) -> List[Deal]:
        """Get deals created by user with optional eager loading"""
        query = db.query(Deal).filter(Deal.created_by_id == user_id)

        # Add eager loading to prevent N+1 queries
        if include_relations:
            query = query.options(
                joinedload(Deal.client),
                joinedload(Deal.created_by),
                joinedload(Deal.organization),
                selectinload(Deal.tasks),
                selectinload(Deal.documents)
            )

        return (
            query
            .order_by(desc(Deal.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recent_deals(
        self,
        db: Session,
        *,
        organization_id: UUID,
        limit: int = 10,
        include_relations: bool = True
    ) -> List[Deal]:
        """Get recent deals for organization with eager loading"""
        query = db.query(Deal).filter(Deal.organization_id == organization_id)

        # Add eager loading for dashboard display
        if include_relations:
            query = query.options(
                joinedload(Deal.client),
                joinedload(Deal.created_by),
                selectinload(Deal.tasks).joinedload("assignee")
            )

        return (
            query
            .order_by(desc(Deal.updated_at))
            .limit(limit)
            .all()
        )
    
    def get_organization_stats(self, db: Session, *, organization_id: UUID) -> Dict[str, Any]:
        """Get deal statistics for organization"""
        
        # Basic counts
        total_deals = db.query(Deal).filter(Deal.organization_id == organization_id).count()
        active_deals = db.query(Deal).filter(
            and_(Deal.organization_id == organization_id, Deal.status == "active")
        ).count()
        closed_deals = db.query(Deal).filter(
            and_(Deal.organization_id == organization_id, Deal.stage == "closed")
        ).count()
        
        # Financial metrics
        total_value_result = db.query(func.sum(Deal.deal_value)).filter(
            Deal.organization_id == organization_id
        ).scalar()
        total_value = float(total_value_result) if total_value_result else 0.0
        
        average_deal_size = total_value / total_deals if total_deals > 0 else 0.0
        
        # Win rate calculation
        lost_deals = db.query(Deal).filter(
            and_(Deal.organization_id == organization_id, Deal.stage == "lost")
        ).count()
        completed_deals = closed_deals + lost_deals
        win_rate = (closed_deals / completed_deals * 100) if completed_deals > 0 else 0.0
        
        # Deals by stage
        stage_counts = db.query(Deal.stage, func.count(Deal.id)).filter(
            Deal.organization_id == organization_id
        ).group_by(Deal.stage).all()
        deals_by_stage = {stage: count for stage, count in stage_counts}
        
        # Deals by type
        type_counts = db.query(Deal.deal_type, func.count(Deal.id)).filter(
            Deal.organization_id == organization_id
        ).group_by(Deal.deal_type).all()
        deals_by_type = {deal_type: count for deal_type, count in type_counts}
        
        # Monthly revenue (simplified - last 12 months)
        monthly_revenue = []
        for i in range(12):
            month_name = f"Month {i+1}"  # Simplified for now
            revenue = total_value / 12  # Simplified calculation
            monthly_revenue.append({
                "month": month_name,
                "revenue": revenue,
                "deals": total_deals // 12
            })
        
        return {
            "total_deals": total_deals,
            "active_deals": active_deals,
            "closed_deals": closed_deals,
            "total_value": total_value,
            "average_deal_size": average_deal_size,
            "win_rate": round(win_rate, 2),
            "deals_by_stage": deals_by_stage,
            "deals_by_type": deals_by_type,
            "monthly_revenue": monthly_revenue
        }
    
    def search_deals(
        self,
        db: Session,
        *,
        organization_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 100,
        include_relations: bool = False
    ) -> List[Deal]:
        """Search deals by title, description, or target company with optimized query"""
        search_filter = f"%{query}%"

        query_obj = db.query(Deal).filter(
            and_(
                Deal.organization_id == organization_id,
                (
                    Deal.title.ilike(search_filter) |
                    Deal.description.ilike(search_filter) |
                    Deal.target_company.ilike(search_filter)
                )
            )
        )

        # Add eager loading for search results
        if include_relations:
            query_obj = query_obj.options(
                joinedload(Deal.client),
                joinedload(Deal.created_by)
            )

        return (
            query_obj
            .order_by(desc(Deal.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_full_details(self, db: Session, *, deal_id: UUID) -> Optional[Deal]:
        """Get deal with all related data in a single query"""
        return (
            db.query(Deal)
            .filter(Deal.id == deal_id)
            .options(
                joinedload(Deal.client),
                joinedload(Deal.created_by),
                joinedload(Deal.organization),
                selectinload(Deal.tasks).joinedload("assignee"),
                selectinload(Deal.documents).joinedload("uploaded_by"),
                selectinload(Deal.financial_models).joinedload("created_by")
            )
            .first()
        )

    def get_dashboard_deals(
        self,
        db: Session,
        *,
        organization_id: UUID,
        limit: int = 20
    ) -> List[Deal]:
        """Get deals optimized for dashboard display"""
        return (
            db.query(Deal)
            .filter(Deal.organization_id == organization_id)
            .options(
                joinedload(Deal.client),
                joinedload(Deal.created_by),
                # Only load task count, not full tasks
                selectinload(Deal.tasks).load_only("id", "status")
            )
            .order_by(desc(Deal.updated_at))
            .limit(limit)
            .all()
        )

    def count_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID,
        stage: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """Count deals by organization with optional filters"""
        query = db.query(Deal).filter(Deal.organization_id == organization_id)

        if stage:
            query = query.filter(Deal.stage == stage)
        if status:
            query = query.filter(Deal.status == status)

        return query.count()


crud_deal = CRUDDeal(Deal)
