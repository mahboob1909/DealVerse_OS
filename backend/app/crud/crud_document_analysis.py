"""
CRUD operations for Document Analysis and Risk Assessment
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from app.crud.base import CRUDBase
from app.models.document_analysis import (
    DocumentAnalysis,
    RiskAssessment,
    DocumentCategory,
    DocumentReview,
    DocumentComparison
)


class CRUDDocumentAnalysis(CRUDBase[DocumentAnalysis, dict, dict]):
    """CRUD operations for DocumentAnalysis"""
    
    def create_analysis(
        self,
        db: Session,
        *,
        document_id: UUID,
        analysis_type: str,
        analysis_results: Dict[str, Any],
        organization_id: UUID,
        created_by_id: UUID
    ) -> DocumentAnalysis:
        """Create a new document analysis"""
        analysis_data = {
            "document_id": document_id,
            "analysis_type": analysis_type,
            "organization_id": organization_id,
            "created_by_id": created_by_id,
            **analysis_results
        }
        
        analysis = DocumentAnalysis(**analysis_data)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    
    def get_by_document(
        self,
        db: Session,
        *,
        document_id: UUID,
        analysis_type: Optional[str] = None
    ) -> List[DocumentAnalysis]:
        """Get analyses for a specific document"""
        query = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.document_id == document_id
        )
        
        if analysis_type:
            query = query.filter(DocumentAnalysis.analysis_type == analysis_type)
        
        return query.order_by(desc(DocumentAnalysis.analysis_date)).all()
    
    def get_latest_analysis(
        self,
        db: Session,
        *,
        document_id: UUID,
        analysis_type: Optional[str] = None
    ) -> Optional[DocumentAnalysis]:
        """Get the latest analysis for a document"""
        query = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.document_id == document_id
        )
        
        if analysis_type:
            query = query.filter(DocumentAnalysis.analysis_type == analysis_type)
        
        return query.order_by(desc(DocumentAnalysis.analysis_date)).first()
    
    def get_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        analysis_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[DocumentAnalysis]:
        """Get analyses by organization with filters"""
        query = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.organization_id == organization_id
        )
        
        if analysis_type:
            query = query.filter(DocumentAnalysis.analysis_type == analysis_type)
        
        if risk_level:
            query = query.filter(DocumentAnalysis.risk_level == risk_level)
        
        if date_from:
            query = query.filter(DocumentAnalysis.analysis_date >= date_from)
        
        if date_to:
            query = query.filter(DocumentAnalysis.analysis_date <= date_to)
        
        return query.order_by(desc(DocumentAnalysis.analysis_date)).offset(skip).limit(limit).all()
    
    def get_high_risk_analyses(
        self,
        db: Session,
        *,
        organization_id: UUID,
        risk_threshold: float = 70.0,
        limit: int = 20
    ) -> List[DocumentAnalysis]:
        """Get high-risk document analyses"""
        return db.query(DocumentAnalysis).filter(
            and_(
                DocumentAnalysis.organization_id == organization_id,
                DocumentAnalysis.overall_risk_score >= risk_threshold
            )
        ).order_by(desc(DocumentAnalysis.overall_risk_score)).limit(limit).all()
    
    def get_analysis_statistics(
        self,
        db: Session,
        *,
        organization_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get analysis statistics for organization"""
        query = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.organization_id == organization_id
        )
        
        if date_from:
            query = query.filter(DocumentAnalysis.analysis_date >= date_from)
        
        if date_to:
            query = query.filter(DocumentAnalysis.analysis_date <= date_to)
        
        analyses = query.all()
        
        if not analyses:
            return {
                "total_analyses": 0,
                "average_risk_score": 0,
                "risk_level_distribution": {},
                "analysis_type_distribution": {},
                "high_risk_count": 0
            }
        
        # Calculate statistics
        total_analyses = len(analyses)
        risk_scores = [float(a.overall_risk_score) for a in analyses if a.overall_risk_score is not None]
        average_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        # Risk level distribution
        risk_level_dist = {}
        analysis_type_dist = {}
        high_risk_count = 0
        
        for analysis in analyses:
            # Risk level distribution
            risk_level = analysis.risk_level or "unknown"
            risk_level_dist[risk_level] = risk_level_dist.get(risk_level, 0) + 1
            
            # Analysis type distribution
            analysis_type = analysis.analysis_type or "unknown"
            analysis_type_dist[analysis_type] = analysis_type_dist.get(analysis_type, 0) + 1
            
            # High risk count
            if analysis.overall_risk_score and float(analysis.overall_risk_score) >= 70:
                high_risk_count += 1
        
        return {
            "total_analyses": total_analyses,
            "average_risk_score": average_risk_score,
            "risk_level_distribution": risk_level_dist,
            "analysis_type_distribution": analysis_type_dist,
            "high_risk_count": high_risk_count
        }


class CRUDRiskAssessment(CRUDBase[RiskAssessment, dict, dict]):
    """CRUD operations for RiskAssessment"""
    
    def create_assessment(
        self,
        db: Session,
        *,
        assessment_data: Dict[str, Any],
        organization_id: UUID,
        created_by_id: UUID
    ) -> RiskAssessment:
        """Create a new risk assessment"""
        assessment_data.update({
            "organization_id": organization_id,
            "created_by_id": created_by_id
        })
        
        assessment = RiskAssessment(**assessment_data)
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment
    
    def get_by_deal(
        self,
        db: Session,
        *,
        deal_id: UUID,
        assessment_type: Optional[str] = None
    ) -> List[RiskAssessment]:
        """Get risk assessments for a specific deal"""
        query = db.query(RiskAssessment).filter(
            RiskAssessment.deal_id == deal_id
        )
        
        if assessment_type:
            query = query.filter(RiskAssessment.assessment_type == assessment_type)
        
        return query.order_by(desc(RiskAssessment.assessment_date)).all()
    
    def get_latest_assessment(
        self,
        db: Session,
        *,
        deal_id: UUID,
        assessment_type: str = "deal"
    ) -> Optional[RiskAssessment]:
        """Get the latest risk assessment for a deal"""
        return db.query(RiskAssessment).filter(
            and_(
                RiskAssessment.deal_id == deal_id,
                RiskAssessment.assessment_type == assessment_type
            )
        ).order_by(desc(RiskAssessment.assessment_date)).first()
    
    def get_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        assessment_type: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> List[RiskAssessment]:
        """Get risk assessments by organization"""
        query = db.query(RiskAssessment).filter(
            RiskAssessment.organization_id == organization_id
        )
        
        if assessment_type:
            query = query.filter(RiskAssessment.assessment_type == assessment_type)
        
        if risk_level:
            query = query.filter(RiskAssessment.risk_level == risk_level)
        
        return query.order_by(desc(RiskAssessment.assessment_date)).offset(skip).limit(limit).all()
    
    def get_critical_assessments(
        self,
        db: Session,
        *,
        organization_id: UUID,
        limit: int = 10
    ) -> List[RiskAssessment]:
        """Get critical risk assessments requiring attention"""
        return db.query(RiskAssessment).filter(
            and_(
                RiskAssessment.organization_id == organization_id,
                RiskAssessment.risk_level == "critical"
            )
        ).order_by(desc(RiskAssessment.overall_risk_score)).limit(limit).all()


class CRUDDocumentCategory(CRUDBase[DocumentCategory, dict, dict]):
    """CRUD operations for DocumentCategory"""
    
    def get_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID
    ) -> List[DocumentCategory]:
        """Get document categories for organization"""
        return db.query(DocumentCategory).filter(
            DocumentCategory.organization_id == organization_id
        ).order_by(DocumentCategory.name).all()
    
    def get_by_name(
        self,
        db: Session,
        *,
        name: str,
        organization_id: UUID
    ) -> Optional[DocumentCategory]:
        """Get document category by name"""
        return db.query(DocumentCategory).filter(
            and_(
                DocumentCategory.name == name,
                DocumentCategory.organization_id == organization_id
            )
        ).first()
    
    def create_category(
        self,
        db: Session,
        *,
        category_data: Dict[str, Any],
        organization_id: UUID,
        created_by_id: UUID
    ) -> DocumentCategory:
        """Create a new document category"""
        category_data.update({
            "organization_id": organization_id,
            "created_by_id": created_by_id
        })
        
        category = DocumentCategory(**category_data)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category


class CRUDDocumentReview(CRUDBase[DocumentReview, dict, dict]):
    """CRUD operations for DocumentReview"""
    
    def create_review(
        self,
        db: Session,
        *,
        review_data: Dict[str, Any],
        organization_id: UUID
    ) -> DocumentReview:
        """Create a new document review"""
        review_data.update({
            "organization_id": organization_id
        })
        
        review = DocumentReview(**review_data)
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
    
    def get_by_document(
        self,
        db: Session,
        *,
        document_id: UUID,
        review_type: Optional[str] = None
    ) -> List[DocumentReview]:
        """Get reviews for a specific document"""
        query = db.query(DocumentReview).filter(
            DocumentReview.document_id == document_id
        )
        
        if review_type:
            query = query.filter(DocumentReview.review_type == review_type)
        
        return query.order_by(desc(DocumentReview.created_at)).all()
    
    def get_pending_reviews(
        self,
        db: Session,
        *,
        organization_id: UUID,
        reviewer_id: Optional[UUID] = None
    ) -> List[DocumentReview]:
        """Get pending reviews for organization or specific reviewer"""
        query = db.query(DocumentReview).filter(
            and_(
                DocumentReview.organization_id == organization_id,
                DocumentReview.review_status == "pending"
            )
        )
        
        if reviewer_id:
            query = query.filter(DocumentReview.reviewer_id == reviewer_id)
        
        return query.order_by(DocumentReview.review_deadline).all()


class CRUDDocumentComparison(CRUDBase[DocumentComparison, dict, dict]):
    """CRUD operations for DocumentComparison"""
    
    def create_comparison(
        self,
        db: Session,
        *,
        comparison_data: Dict[str, Any],
        organization_id: UUID,
        created_by_id: UUID
    ) -> DocumentComparison:
        """Create a new document comparison"""
        comparison_data.update({
            "organization_id": organization_id,
            "created_by_id": created_by_id
        })
        
        comparison = DocumentComparison(**comparison_data)
        db.add(comparison)
        db.commit()
        db.refresh(comparison)
        return comparison
    
    def get_by_documents(
        self,
        db: Session,
        *,
        primary_document_id: UUID,
        secondary_document_id: UUID
    ) -> List[DocumentComparison]:
        """Get comparisons between two specific documents"""
        return db.query(DocumentComparison).filter(
            or_(
                and_(
                    DocumentComparison.primary_document_id == primary_document_id,
                    DocumentComparison.secondary_document_id == secondary_document_id
                ),
                and_(
                    DocumentComparison.primary_document_id == secondary_document_id,
                    DocumentComparison.secondary_document_id == primary_document_id
                )
            )
        ).order_by(desc(DocumentComparison.comparison_date)).all()


# Create instances
crud_document_analysis = CRUDDocumentAnalysis(DocumentAnalysis)
crud_risk_assessment = CRUDRiskAssessment(RiskAssessment)
crud_document_category = CRUDDocumentCategory(DocumentCategory)
crud_document_review = CRUDDocumentReview(DocumentReview)
crud_document_comparison = CRUDDocumentComparison(DocumentComparison)
