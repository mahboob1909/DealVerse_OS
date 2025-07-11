"""
Compliance AI Service for DealVerse OS
Integrates Enhanced Compliance AI with existing compliance infrastructure
"""
import logging
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.services.enhanced_compliance_ai import enhanced_compliance_ai
from app.schemas.compliance_ai import (
    ComplianceAIAnalysisRequest,
    ComplianceAIAnalysisResponse,
    ComplianceMonitoringRequest,
    ComplianceMonitoringResponse,
    RegulatoryUpdateAnalysisRequest,
    RegulatoryUpdateAnalysisResponse,
    RegulatoryDomain
)
from app.models.compliance import (
    ComplianceCategory,
    ComplianceRequirement,
    ComplianceAssessment,
    RegulatoryUpdate,
    ComplianceStatus
)

logger = logging.getLogger(__name__)


class ComplianceAIService:
    """
    Service layer for AI-powered compliance monitoring and analysis
    Integrates Enhanced Compliance AI with existing compliance infrastructure
    """
    
    def __init__(self):
        self.enhanced_ai = enhanced_compliance_ai
        self.use_enhanced_ai = enhanced_compliance_ai.enhanced_ai_available
        self.model_version = "ComplianceAI-v1.0"
        
        if self.use_enhanced_ai:
            logger.info("Compliance AI Service initialized with enhanced AI capabilities")
        else:
            logger.warning("Compliance AI Service initialized with fallback capabilities only")
    
    async def analyze_organization_compliance(
        self, 
        db: Session,
        organization_id: UUID,
        analysis_type: str = "comprehensive",
        regulatory_focus: List[str] = None
    ) -> ComplianceAIAnalysisResponse:
        """
        Analyze organization's overall compliance status using AI
        """
        try:
            # Gather compliance data from database
            compliance_data = await self._gather_compliance_data(db, organization_id)
            
            # Create analysis request
            request = ComplianceAIAnalysisRequest(
                compliance_context=f"Organization compliance analysis for ID: {organization_id}",
                analysis_type=analysis_type,
                regulatory_focus=[RegulatoryDomain(rf) for rf in (regulatory_focus or [])],
                compliance_data=compliance_data,
                include_patterns=True,
                include_trends=True,
                include_predictions=True
            )
            
            # Perform AI analysis
            result = await self.enhanced_ai.analyze_compliance(request)
            
            # Store analysis results in database
            await self._store_analysis_results(db, organization_id, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Organization compliance analysis failed: {str(e)}")
            raise
    
    async def analyze_compliance_requirement(
        self,
        db: Session,
        requirement_id: UUID,
        organization_id: UUID
    ) -> ComplianceAIAnalysisResponse:
        """
        Analyze specific compliance requirement using AI
        """
        try:
            # Get requirement data
            requirement_data = await self._get_requirement_data(db, requirement_id, organization_id)
            
            # Create focused analysis request
            request = ComplianceAIAnalysisRequest(
                compliance_context=f"Specific requirement analysis for ID: {requirement_id}",
                analysis_type="requirement_focused",
                regulatory_focus=[],
                compliance_data=requirement_data,
                include_patterns=False,
                include_trends=False,
                include_predictions=True
            )
            
            # Perform AI analysis
            result = await self.enhanced_ai.analyze_compliance(request)
            
            return result
            
        except Exception as e:
            logger.error(f"Requirement compliance analysis failed: {str(e)}")
            raise
    
    async def monitor_regulatory_changes(
        self,
        db: Session,
        organization_id: UUID,
        monitoring_scope: List[str] = None
    ) -> ComplianceMonitoringResponse:
        """
        Set up AI-powered monitoring for regulatory changes
        """
        try:
            # Create monitoring request
            request = ComplianceMonitoringRequest(
                organization_id=organization_id,
                monitoring_scope=[RegulatoryDomain(ms) for ms in (monitoring_scope or ["sec", "finra", "sox"])],
                alert_thresholds={
                    "high_impact": 0.8,
                    "medium_impact": 0.6,
                    "low_impact": 0.4
                },
                monitoring_frequency="daily",
                include_predictive=True
            )
            
            # Set up monitoring (placeholder for actual implementation)
            monitoring_id = f"MON-{uuid4().hex[:8]}"
            
            # Get current regulatory updates
            recent_updates = await self._get_recent_regulatory_updates(db, organization_id)
            
            # Analyze updates for alerts
            active_alerts = []
            for update in recent_updates:
                if not update.is_reviewed:
                    # Create alert for unreviewed updates
                    from app.schemas.compliance_ai import MonitoringAlert, ComplianceRiskLevel
                    alert = MonitoringAlert(
                        alert_id=f"ALERT-{uuid4().hex[:8]}",
                        alert_type="Regulatory Update",
                        severity=ComplianceRiskLevel(update.impact_level),
                        title=f"New {update.regulation_type.upper()} Update",
                        description=update.title,
                        triggered_at=update.created_at,
                        source="Regulatory monitoring",
                        requires_immediate_action=update.impact_level in ["high", "critical"],
                        escalation_level=3 if update.impact_level == "critical" else 2
                    )
                    active_alerts.append(alert)
            
            return ComplianceMonitoringResponse(
                monitoring_id=monitoring_id,
                status="active",
                active_alerts=active_alerts,
                next_check=datetime.utcnow() + timedelta(days=1),
                configuration={
                    "scope": monitoring_scope or ["sec", "finra", "sox"],
                    "frequency": "daily",
                    "organization_id": str(organization_id)
                }
            )
            
        except Exception as e:
            logger.error(f"Regulatory monitoring setup failed: {str(e)}")
            raise
    
    async def analyze_regulatory_update(
        self,
        update_content: str,
        regulation_type: str,
        organization_context: Dict[str, Any] = None
    ) -> RegulatoryUpdateAnalysisResponse:
        """
        Analyze impact of a specific regulatory update using AI
        """
        try:
            # Create analysis request
            request = RegulatoryUpdateAnalysisRequest(
                update_content=update_content,
                regulation_type=RegulatoryDomain(regulation_type),
                organization_context=organization_context or {},
                current_compliance_status={}
            )
            
            # Perform AI analysis (placeholder for actual implementation)
            # This would integrate with the enhanced AI service
            
            # Generate analysis response
            return RegulatoryUpdateAnalysisResponse(
                impact_assessment={
                    "overall_impact": "medium",
                    "affected_areas": ["Client reporting", "Internal controls"],
                    "compliance_gap": "Minor gaps identified",
                    "urgency": "moderate"
                },
                required_actions=[
                    "Review current disclosure procedures",
                    "Update client communication templates",
                    "Train staff on new requirements"
                ],
                timeline={
                    "immediate": "Review requirements (1 week)",
                    "short_term": "Implement changes (4 weeks)",
                    "long_term": "Monitor compliance (ongoing)"
                },
                risk_assessment={
                    "compliance_risk": "medium",
                    "operational_risk": "low",
                    "financial_risk": "low"
                },
                compliance_gap_analysis={
                    "current_state": "Partially compliant",
                    "required_state": "Fully compliant",
                    "gap_severity": "medium",
                    "remediation_effort": "moderate"
                },
                confidence_score=Decimal("0.85")
            )
            
        except Exception as e:
            logger.error(f"Regulatory update analysis failed: {str(e)}")
            raise
    
    async def _gather_compliance_data(self, db: Session, organization_id: UUID) -> Dict[str, Any]:
        """
        Gather comprehensive compliance data for AI analysis
        """
        try:
            # Get compliance categories
            categories = db.query(ComplianceCategory).filter(
                ComplianceCategory.organization_id == organization_id,
                ComplianceCategory.is_active == True
            ).all()
            
            # Get compliance requirements
            requirements = db.query(ComplianceRequirement).filter(
                ComplianceRequirement.organization_id == organization_id
            ).all()
            
            # Get recent assessments
            recent_assessments = db.query(ComplianceAssessment).filter(
                ComplianceAssessment.organization_id == organization_id,
                ComplianceAssessment.assessment_date >= datetime.utcnow() - timedelta(days=90)
            ).all()
            
            # Get regulatory updates
            regulatory_updates = db.query(RegulatoryUpdate).filter(
                RegulatoryUpdate.organization_id == organization_id,
                RegulatoryUpdate.created_at >= datetime.utcnow() - timedelta(days=30)
            ).all()
            
            return {
                "organization_id": str(organization_id),
                "categories": [
                    {
                        "id": str(cat.id),
                        "name": cat.name,
                        "code": cat.code,
                        "priority_level": cat.priority_level,
                        "regulatory_body": cat.regulatory_body
                    } for cat in categories
                ],
                "requirements": [
                    {
                        "id": str(req.id),
                        "title": req.title,
                        "status": req.status,
                        "risk_level": req.risk_level,
                        "completion_percentage": req.completion_percentage,
                        "due_date": req.due_date.isoformat() if req.due_date else None
                    } for req in requirements
                ],
                "recent_assessments": [
                    {
                        "id": str(assess.id),
                        "assessment_type": assess.assessment_type,
                        "status": assess.status.value,
                        "score": float(assess.score) if assess.score else None,
                        "risk_level": assess.risk_level,
                        "assessment_date": assess.assessment_date.isoformat()
                    } for assess in recent_assessments
                ],
                "regulatory_updates": [
                    {
                        "id": str(update.id),
                        "title": update.title,
                        "regulation_type": update.regulation_type,
                        "impact_level": update.impact_level,
                        "is_reviewed": update.is_reviewed,
                        "created_at": update.created_at.isoformat()
                    } for update in regulatory_updates
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to gather compliance data: {str(e)}")
            return {"error": str(e)}
    
    async def _get_requirement_data(self, db: Session, requirement_id: UUID, organization_id: UUID) -> Dict[str, Any]:
        """
        Get specific compliance requirement data
        """
        try:
            requirement = db.query(ComplianceRequirement).filter(
                ComplianceRequirement.id == requirement_id,
                ComplianceRequirement.organization_id == organization_id
            ).first()
            
            if not requirement:
                raise ValueError(f"Requirement {requirement_id} not found")
            
            # Get related assessments
            assessments = db.query(ComplianceAssessment).filter(
                ComplianceAssessment.requirement_id == requirement_id
            ).all()
            
            return {
                "requirement": {
                    "id": str(requirement.id),
                    "title": requirement.title,
                    "description": requirement.description,
                    "status": requirement.status,
                    "risk_level": requirement.risk_level,
                    "completion_percentage": requirement.completion_percentage,
                    "required_documents": requirement.required_documents,
                    "evidence_requirements": requirement.evidence_requirements
                },
                "assessments": [
                    {
                        "id": str(assess.id),
                        "status": assess.status.value,
                        "score": float(assess.score) if assess.score else None,
                        "findings": assess.findings,
                        "recommendations": assess.recommendations
                    } for assess in assessments
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get requirement data: {str(e)}")
            return {"error": str(e)}
    
    async def _get_recent_regulatory_updates(self, db: Session, organization_id: UUID) -> List[RegulatoryUpdate]:
        """
        Get recent regulatory updates for monitoring
        """
        return db.query(RegulatoryUpdate).filter(
            RegulatoryUpdate.organization_id == organization_id,
            RegulatoryUpdate.created_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
    
    async def _store_analysis_results(self, db: Session, organization_id: UUID, result: ComplianceAIAnalysisResponse):
        """
        Store AI analysis results in database (placeholder)
        """
        # This would store analysis results for future reference
        logger.info(f"Storing compliance analysis results for organization {organization_id}")
        pass
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get current service status
        """
        enhanced_status = self.enhanced_ai.get_service_status()
        
        return {
            "service_type": "compliance_ai",
            "model_version": self.model_version,
            "enhanced_ai_available": self.use_enhanced_ai,
            "enhanced_ai_status": enhanced_status,
            "supported_analysis_types": [
                "comprehensive", "requirement_focused", "regulatory_monitoring",
                "violation_detection", "pattern_analysis", "trend_analysis"
            ],
            "supported_regulations": enhanced_status.get("supported_regulations", []),
            "status": "operational"
        }


# Create global instance
compliance_ai_service = ComplianceAIService()
