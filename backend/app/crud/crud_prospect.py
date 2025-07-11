"""
CRUD operations for Prospect AI module
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from app.crud.base import CRUDBase
from app.models.prospect import Prospect, ProspectAnalysis, MarketIntelligence
from app.schemas.prospect import (
    ProspectCreate, 
    ProspectUpdate, 
    ProspectSearchRequest,
    ProspectAnalysisRequest
)


class CRUDProspect(CRUDBase[Prospect, ProspectCreate, ProspectUpdate]):
    """CRUD operations for Prospect"""
    
    def get_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[ProspectSearchRequest] = None
    ) -> List[Prospect]:
        """Get prospects by organization with optional filters"""
        query = db.query(Prospect).filter(Prospect.organization_id == organization_id)
        
        if filters:
            # Apply search filters
            if filters.query:
                search_term = f"%{filters.query}%"
                query = query.filter(
                    or_(
                        Prospect.company_name.ilike(search_term),
                        Prospect.description.ilike(search_term),
                        Prospect.industry.ilike(search_term)
                    )
                )
            
            if filters.industry:
                query = query.filter(Prospect.industry == filters.industry)
            
            if filters.location:
                query = query.filter(Prospect.location.ilike(f"%{filters.location}%"))
            
            if filters.min_revenue:
                query = query.filter(Prospect.revenue >= filters.min_revenue)
            
            if filters.max_revenue:
                query = query.filter(Prospect.revenue <= filters.max_revenue)
            
            if filters.min_ai_score:
                query = query.filter(Prospect.ai_score >= filters.min_ai_score)
            
            if filters.status:
                query = query.filter(Prospect.status == filters.status)
            
            if filters.stage:
                query = query.filter(Prospect.stage == filters.stage)
            
            if filters.priority:
                query = query.filter(Prospect.priority == filters.priority)
            
            if filters.assigned_to_id:
                query = query.filter(Prospect.assigned_to_id == filters.assigned_to_id)
            
            # Apply sorting
            sort_column = getattr(Prospect, filters.sort_by, Prospect.ai_score)
            if filters.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            # Default sorting by AI score descending
            query = query.order_by(desc(Prospect.ai_score))
        
        return query.offset(skip).limit(limit).all()
    
    def count_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID,
        filters: Optional[ProspectSearchRequest] = None
    ) -> int:
        """Count prospects by organization with optional filters"""
        query = db.query(func.count(Prospect.id)).filter(
            Prospect.organization_id == organization_id
        )
        
        if filters:
            # Apply same filters as get_by_organization
            if filters.query:
                search_term = f"%{filters.query}%"
                query = query.filter(
                    or_(
                        Prospect.company_name.ilike(search_term),
                        Prospect.description.ilike(search_term),
                        Prospect.industry.ilike(search_term)
                    )
                )
            
            if filters.industry:
                query = query.filter(Prospect.industry == filters.industry)
            
            if filters.location:
                query = query.filter(Prospect.location.ilike(f"%{filters.location}%"))
            
            if filters.min_revenue:
                query = query.filter(Prospect.revenue >= filters.min_revenue)
            
            if filters.max_revenue:
                query = query.filter(Prospect.revenue <= filters.max_revenue)
            
            if filters.min_ai_score:
                query = query.filter(Prospect.ai_score >= filters.min_ai_score)
            
            if filters.status:
                query = query.filter(Prospect.status == filters.status)
            
            if filters.stage:
                query = query.filter(Prospect.stage == filters.stage)
            
            if filters.priority:
                query = query.filter(Prospect.priority == filters.priority)
            
            if filters.assigned_to_id:
                query = query.filter(Prospect.assigned_to_id == filters.assigned_to_id)
        
        return query.scalar()
    
    def get_by_company_name(
        self,
        db: Session,
        *,
        company_name: str,
        organization_id: UUID
    ) -> Optional[Prospect]:
        """Get prospect by company name within organization"""
        return db.query(Prospect).filter(
            and_(
                Prospect.company_name == company_name,
                Prospect.organization_id == organization_id
            )
        ).first()
    
    def get_high_priority_prospects(
        self,
        db: Session,
        *,
        organization_id: UUID,
        limit: int = 10
    ) -> List[Prospect]:
        """Get high priority prospects for organization"""
        return db.query(Prospect).filter(
            and_(
                Prospect.organization_id == organization_id,
                Prospect.priority.in_(["high", "critical"]),
                Prospect.status.in_(["identified", "analyzing", "qualified"])
            )
        ).order_by(
            desc(Prospect.ai_score),
            desc(Prospect.deal_probability)
        ).limit(limit).all()
    
    def get_prospects_requiring_follow_up(
        self,
        db: Session,
        *,
        organization_id: UUID,
        days_ahead: int = 7
    ) -> List[Prospect]:
        """Get prospects requiring follow-up within specified days"""
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return db.query(Prospect).filter(
            and_(
                Prospect.organization_id == organization_id,
                Prospect.next_follow_up <= cutoff_date,
                Prospect.status.in_(["contacted", "engaged"])
            )
        ).order_by(Prospect.next_follow_up).all()
    
    def update_ai_scores(
        self,
        db: Session,
        *,
        prospect_id: UUID,
        ai_score: Decimal,
        confidence_level: str,
        deal_probability: Decimal,
        estimated_deal_size: Optional[Decimal] = None,
        risk_factors: Optional[List[str]] = None,
        opportunities: Optional[List[str]] = None,
        recommended_approach: Optional[str] = None
    ) -> Prospect:
        """Update AI scoring results for a prospect"""
        prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
        
        if prospect:
            prospect.ai_score = ai_score
            prospect.confidence_level = confidence_level
            prospect.deal_probability = deal_probability
            prospect.analysis_date = datetime.utcnow()
            
            if estimated_deal_size is not None:
                prospect.estimated_deal_size = estimated_deal_size
            
            if risk_factors is not None:
                prospect.risk_factors = risk_factors
            
            if opportunities is not None:
                prospect.opportunities = opportunities
            
            if recommended_approach is not None:
                prospect.recommended_approach = recommended_approach
            
            # Update status if it's still in initial stages
            if prospect.status == "identified":
                prospect.status = "analyzing"
            
            db.add(prospect)
            db.commit()
            db.refresh(prospect)
        
        return prospect
    
    def get_industry_statistics(
        self,
        db: Session,
        *,
        organization_id: UUID,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics for prospects by industry"""
        query = db.query(Prospect).filter(Prospect.organization_id == organization_id)
        
        if industry:
            query = query.filter(Prospect.industry == industry)
        
        prospects = query.all()
        
        if not prospects:
            return {
                "total_prospects": 0,
                "average_ai_score": 0,
                "average_deal_probability": 0,
                "total_estimated_value": 0,
                "status_breakdown": {},
                "priority_breakdown": {}
            }
        
        # Calculate statistics
        total_prospects = len(prospects)
        ai_scores = [p.ai_score for p in prospects if p.ai_score is not None]
        deal_probs = [p.deal_probability for p in prospects if p.deal_probability is not None]
        deal_sizes = [p.estimated_deal_size for p in prospects if p.estimated_deal_size is not None]
        
        # Status and priority breakdowns
        status_breakdown = {}
        priority_breakdown = {}
        
        for prospect in prospects:
            status_breakdown[prospect.status] = status_breakdown.get(prospect.status, 0) + 1
            priority_breakdown[prospect.priority] = priority_breakdown.get(prospect.priority, 0) + 1
        
        return {
            "total_prospects": total_prospects,
            "average_ai_score": sum(ai_scores) / len(ai_scores) if ai_scores else 0,
            "average_deal_probability": sum(deal_probs) / len(deal_probs) if deal_probs else 0,
            "total_estimated_value": sum(deal_sizes) if deal_sizes else 0,
            "status_breakdown": status_breakdown,
            "priority_breakdown": priority_breakdown
        }


class CRUDProspectAnalysis(CRUDBase[ProspectAnalysis, dict, dict]):
    """CRUD operations for ProspectAnalysis"""
    
    def create_analysis(
        self,
        db: Session,
        *,
        prospect_id: UUID,
        analysis_type: str,
        results: Dict[str, Any],
        organization_id: UUID,
        created_by_id: UUID
    ) -> ProspectAnalysis:
        """Create a new prospect analysis"""
        analysis_data = {
            "prospect_id": prospect_id,
            "analysis_type": analysis_type,
            "organization_id": organization_id,
            "created_by_id": created_by_id,
            **results
        }
        
        analysis = ProspectAnalysis(**analysis_data)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    
    def get_latest_analysis(
        self,
        db: Session,
        *,
        prospect_id: UUID,
        analysis_type: Optional[str] = None
    ) -> Optional[ProspectAnalysis]:
        """Get the latest analysis for a prospect"""
        query = db.query(ProspectAnalysis).filter(
            ProspectAnalysis.prospect_id == prospect_id
        )
        
        if analysis_type:
            query = query.filter(ProspectAnalysis.analysis_type == analysis_type)
        
        return query.order_by(desc(ProspectAnalysis.analysis_date)).first()


class CRUDMarketIntelligence(CRUDBase[MarketIntelligence, dict, dict]):
    """CRUD operations for MarketIntelligence"""
    
    def get_latest_intelligence(
        self,
        db: Session,
        *,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        period_type: str = "monthly"
    ) -> Optional[MarketIntelligence]:
        """Get latest market intelligence data"""
        query = db.query(MarketIntelligence)
        
        if industry:
            query = query.filter(MarketIntelligence.industry == industry)
        
        if region:
            query = query.filter(MarketIntelligence.region == region)
        
        query = query.filter(MarketIntelligence.period_type == period_type)
        
        return query.order_by(desc(MarketIntelligence.period_end)).first()
    
    def create_intelligence_report(
        self,
        db: Session,
        *,
        data: Dict[str, Any],
        organization_id: UUID,
        created_by_id: UUID
    ) -> MarketIntelligence:
        """Create a new market intelligence report"""
        intelligence_data = {
            "organization_id": organization_id,
            "created_by_id": created_by_id,
            **data
        }
        
        intelligence = MarketIntelligence(**intelligence_data)
        db.add(intelligence)
        db.commit()
        db.refresh(intelligence)
        return intelligence


# Create instances
crud_prospect = CRUDProspect(Prospect)
crud_prospect_analysis = CRUDProspectAnalysis(ProspectAnalysis)
crud_market_intelligence = CRUDMarketIntelligence(MarketIntelligence)
