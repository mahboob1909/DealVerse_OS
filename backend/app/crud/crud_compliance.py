"""
CRUD operations for Compliance models
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.crud.base import CRUDBase
from app.models.compliance import (
    ComplianceCategory, 
    ComplianceRequirement, 
    ComplianceAssessment, 
    ComplianceAuditLog,
    RegulatoryUpdate,
    ComplianceStatus
)
from app.schemas.compliance import (
    ComplianceCategoryCreate, 
    ComplianceCategoryUpdate,
    ComplianceRequirementCreate, 
    ComplianceRequirementUpdate,
    ComplianceAssessmentCreate, 
    ComplianceAssessmentUpdate,
    RegulatoryUpdateCreate,
    RegulatoryUpdateUpdate
)


class CRUDComplianceCategory(CRUDBase[ComplianceCategory, ComplianceCategoryCreate, ComplianceCategoryUpdate]):
    """CRUD operations for ComplianceCategory"""
    
    def get_by_organization(
        self, 
        db: Session, 
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[ComplianceCategory]:
        """Get compliance categories by organization"""
        query = (
            db.query(self.model)
            .filter(ComplianceCategory.organization_id == organization_id)
        )
        
        if is_active is not None:
            query = query.filter(ComplianceCategory.is_active == is_active)
        
        return query.order_by(ComplianceCategory.priority_level, ComplianceCategory.name).offset(skip).limit(limit).all()
    
    def get_by_code(self, db: Session, code: str, organization_id: UUID) -> Optional[ComplianceCategory]:
        """Get compliance category by code"""
        return (
            db.query(self.model)
            .filter(ComplianceCategory.code == code)
            .filter(ComplianceCategory.organization_id == organization_id)
            .first()
        )


class CRUDComplianceRequirement(CRUDBase[ComplianceRequirement, ComplianceRequirementCreate, ComplianceRequirementUpdate]):
    """CRUD operations for ComplianceRequirement"""
    
    def get_by_organization(
        self, 
        db: Session, 
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        category_id: Optional[UUID] = None
    ) -> List[ComplianceRequirement]:
        """Get compliance requirements by organization"""
        query = (
            db.query(self.model)
            .filter(ComplianceRequirement.organization_id == organization_id)
        )
        
        if status:
            query = query.filter(ComplianceRequirement.status == status)
        if category_id:
            query = query.filter(ComplianceRequirement.category_id == category_id)
        
        return query.order_by(ComplianceRequirement.due_date.asc()).offset(skip).limit(limit).all()
    
    def get_by_category(
        self, 
        db: Session, 
        category_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[ComplianceRequirement]:
        """Get requirements by category"""
        return (
            db.query(self.model)
            .filter(ComplianceRequirement.category_id == category_id)
            .order_by(ComplianceRequirement.due_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_overdue(
        self, 
        db: Session, 
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[ComplianceRequirement]:
        """Get overdue requirements"""
        return (
            db.query(self.model)
            .filter(ComplianceRequirement.organization_id == organization_id)
            .filter(ComplianceRequirement.due_date < datetime.utcnow())
            .filter(ComplianceRequirement.status != ComplianceStatus.COMPLIANT)
            .order_by(ComplianceRequirement.due_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_upcoming_reviews(
        self, 
        db: Session, 
        organization_id: UUID,
        days_ahead: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[ComplianceRequirement]:
        """Get requirements with upcoming reviews"""
        future_date = datetime.utcnow() + timedelta(days=days_ahead)
        return (
            db.query(self.model)
            .filter(ComplianceRequirement.organization_id == organization_id)
            .filter(ComplianceRequirement.next_review_date <= future_date)
            .filter(ComplianceRequirement.next_review_date >= datetime.utcnow())
            .order_by(ComplianceRequirement.next_review_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDComplianceAssessment(CRUDBase[ComplianceAssessment, ComplianceAssessmentCreate, ComplianceAssessmentUpdate]):
    """CRUD operations for ComplianceAssessment"""
    
    def get_by_organization(
        self, 
        db: Session, 
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        assessment_type: Optional[str] = None
    ) -> List[ComplianceAssessment]:
        """Get assessments by organization"""
        query = (
            db.query(self.model)
            .filter(ComplianceAssessment.organization_id == organization_id)
        )
        
        if assessment_type:
            query = query.filter(ComplianceAssessment.assessment_type == assessment_type)
        
        return query.order_by(ComplianceAssessment.assessment_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_requirement(
        self, 
        db: Session, 
        requirement_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[ComplianceAssessment]:
        """Get assessments by requirement"""
        return (
            db.query(self.model)
            .filter(ComplianceAssessment.requirement_id == requirement_id)
            .order_by(ComplianceAssessment.assessment_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_recent(
        self, 
        db: Session, 
        organization_id: UUID,
        days_back: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[ComplianceAssessment]:
        """Get recent assessments"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        return (
            db.query(self.model)
            .filter(ComplianceAssessment.organization_id == organization_id)
            .filter(ComplianceAssessment.assessment_date >= cutoff_date)
            .order_by(ComplianceAssessment.assessment_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDRegulatoryUpdate(CRUDBase[RegulatoryUpdate, RegulatoryUpdateCreate, RegulatoryUpdateUpdate]):
    """CRUD operations for RegulatoryUpdate"""
    
    def get_by_organization(
        self, 
        db: Session, 
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        is_reviewed: Optional[bool] = None,
        impact_level: Optional[str] = None
    ) -> List[RegulatoryUpdate]:
        """Get regulatory updates by organization"""
        query = (
            db.query(self.model)
            .filter(RegulatoryUpdate.organization_id == organization_id)
        )
        
        if is_reviewed is not None:
            query = query.filter(RegulatoryUpdate.is_reviewed == is_reviewed)
        if impact_level:
            query = query.filter(RegulatoryUpdate.impact_level == impact_level)
        
        return query.order_by(RegulatoryUpdate.publication_date.desc()).offset(skip).limit(limit).all()
    
    def get_unreviewed(
        self, 
        db: Session, 
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[RegulatoryUpdate]:
        """Get unreviewed regulatory updates"""
        return (
            db.query(self.model)
            .filter(RegulatoryUpdate.organization_id == organization_id)
            .filter(RegulatoryUpdate.is_reviewed == False)
            .order_by(RegulatoryUpdate.publication_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class CRUDComplianceDashboard:
    """CRUD operations for compliance dashboard data"""
    
    def get_dashboard_summary(self, db: Session, organization_id: UUID) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        
        # Get requirement counts by status
        requirement_counts = (
            db.query(
                ComplianceRequirement.status,
                func.count(ComplianceRequirement.id).label('count')
            )
            .filter(ComplianceRequirement.organization_id == organization_id)
            .group_by(ComplianceRequirement.status)
            .all()
        )
        
        status_counts = {status: 0 for status in ComplianceStatus}
        for status, count in requirement_counts:
            status_counts[status] = count
        
        total_requirements = sum(status_counts.values())
        
        # Calculate overall compliance score
        if total_requirements > 0:
            compliant_weight = status_counts.get(ComplianceStatus.COMPLIANT, 0) * 100
            warning_weight = status_counts.get(ComplianceStatus.WARNING, 0) * 70
            pending_weight = status_counts.get(ComplianceStatus.PENDING, 0) * 50
            
            overall_score = (compliant_weight + warning_weight + pending_weight) / total_requirements
        else:
            overall_score = 100.0
        
        # Get categories summary
        categories = (
            db.query(ComplianceCategory)
            .filter(ComplianceCategory.organization_id == organization_id)
            .filter(ComplianceCategory.is_active == True)
            .all()
        )
        
        categories_summary = []
        for category in categories:
            cat_requirements = (
                db.query(ComplianceRequirement)
                .filter(ComplianceRequirement.category_id == category.id)
                .all()
            )
            
            cat_total = len(cat_requirements)
            cat_compliant = len([r for r in cat_requirements if r.status == ComplianceStatus.COMPLIANT])
            cat_score = (cat_compliant / cat_total * 100) if cat_total > 0 else 100
            
            categories_summary.append({
                "id": str(category.id),
                "name": category.name,
                "code": category.code,
                "total_requirements": cat_total,
                "compliant_requirements": cat_compliant,
                "compliance_score": round(cat_score, 1),
                "status": "compliant" if cat_score >= 95 else "warning" if cat_score >= 80 else "non_compliant"
            })
        
        # Get recent assessments
        recent_assessments = (
            db.query(ComplianceAssessment)
            .filter(ComplianceAssessment.organization_id == organization_id)
            .order_by(ComplianceAssessment.assessment_date.desc())
            .limit(5)
            .all()
        )
        
        # Get upcoming reviews
        upcoming_reviews = (
            db.query(ComplianceRequirement)
            .filter(ComplianceRequirement.organization_id == organization_id)
            .filter(ComplianceRequirement.next_review_date >= datetime.utcnow())
            .filter(ComplianceRequirement.next_review_date <= datetime.utcnow() + timedelta(days=30))
            .order_by(ComplianceRequirement.next_review_date.asc())
            .limit(10)
            .all()
        )
        
        # Get regulatory updates count
        total_updates = (
            db.query(RegulatoryUpdate)
            .filter(RegulatoryUpdate.organization_id == organization_id)
            .count()
        )
        
        unreviewed_updates = (
            db.query(RegulatoryUpdate)
            .filter(RegulatoryUpdate.organization_id == organization_id)
            .filter(RegulatoryUpdate.is_reviewed == False)
            .count()
        )
        
        return {
            "total_requirements": total_requirements,
            "compliant_requirements": status_counts.get(ComplianceStatus.COMPLIANT, 0),
            "warning_requirements": status_counts.get(ComplianceStatus.WARNING, 0),
            "non_compliant_requirements": status_counts.get(ComplianceStatus.NON_COMPLIANT, 0),
            "pending_requirements": status_counts.get(ComplianceStatus.PENDING, 0),
            "overall_compliance_score": round(overall_score, 1),
            "categories_summary": categories_summary,
            "recent_assessments": [
                {
                    "id": str(a.id),
                    "assessment_date": a.assessment_date.isoformat(),
                    "status": a.status,
                    "score": a.score,
                    "assessment_type": a.assessment_type
                } for a in recent_assessments
            ],
            "upcoming_reviews": [
                {
                    "id": str(r.id),
                    "title": r.title,
                    "next_review_date": r.next_review_date.isoformat() if r.next_review_date else None,
                    "status": r.status,
                    "category_name": r.category.name if r.category else None
                } for r in upcoming_reviews
            ],
            "regulatory_updates_count": total_updates,
            "unreviewed_updates_count": unreviewed_updates
        }


# Create CRUD instances
crud_compliance_category = CRUDComplianceCategory(ComplianceCategory)
crud_compliance_requirement = CRUDComplianceRequirement(ComplianceRequirement)
crud_compliance_assessment = CRUDComplianceAssessment(ComplianceAssessment)
crud_regulatory_update = CRUDRegulatoryUpdate(RegulatoryUpdate)
crud_compliance_dashboard = CRUDComplianceDashboard()
