"""
Compliance API endpoints with AI-powered analysis
"""
from typing import Any, List, Optional, Dict
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Body, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.db.database import get_db
from app.models.user import User
from app.services.compliance_ai import compliance_ai_service
from app.crud.crud_compliance import (
    crud_compliance_category,
    crud_compliance_requirement,
    crud_compliance_assessment,
    crud_regulatory_update,
    crud_compliance_dashboard
)
from app.schemas.compliance import (
    ComplianceCategory,
    ComplianceCategoryCreate,
    ComplianceCategoryUpdate,
    ComplianceRequirement,
    ComplianceRequirementCreate,
    ComplianceRequirementUpdate,
    ComplianceAssessment,
    ComplianceAssessmentCreate,
    ComplianceAssessmentUpdate,
    RegulatoryUpdate,
    RegulatoryUpdateCreate,
    RegulatoryUpdateUpdate,
    ComplianceDashboardSummary
)
from app.services.export_service import export_service
from app.services.audit_trails_service import audit_trails_service, AuditEventType, AuditSeverity

router = APIRouter()


# Dashboard endpoints
@router.get("/dashboard", response_model=dict)
def get_compliance_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get compliance dashboard summary"""
    summary = crud_compliance_dashboard.get_dashboard_summary(
        db, organization_id=current_user.organization_id
    )
    return summary


# Compliance Categories endpoints
@router.get("/categories", response_model=List[ComplianceCategory])
def get_compliance_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None)
):
    """Get compliance categories"""
    categories = crud_compliance_category.get_by_organization(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        is_active=is_active
    )
    return categories


@router.post("/categories", response_model=ComplianceCategory)
def create_compliance_category(
    *,
    db: Session = Depends(get_db),
    category_in: ComplianceCategoryCreate,
    current_user: User = Depends(deps.check_permission("compliance:create"))
):
    """Create new compliance category"""
    # Check if category code already exists
    existing = crud_compliance_category.get_by_code(
        db, code=category_in.code, organization_id=current_user.organization_id
    )
    if existing:
        raise HTTPException(status_code=400, detail="Category code already exists")
    
    category_data = category_in.dict()
    category_data["organization_id"] = current_user.organization_id
    
    category = crud_compliance_category.create(db=db, obj_in=category_data)
    return category


@router.get("/categories/{category_id}", response_model=ComplianceCategory)
def get_compliance_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get specific compliance category"""
    category = crud_compliance_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return category


@router.put("/categories/{category_id}", response_model=ComplianceCategory)
def update_compliance_category(
    category_id: UUID,
    category_update: ComplianceCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permission("compliance:update"))
):
    """Update compliance category"""
    category = crud_compliance_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    category = crud_compliance_category.update(db=db, db_obj=category, obj_in=category_update)
    return category


# Compliance Requirements endpoints
@router.get("/requirements", response_model=List[ComplianceRequirement])
def get_compliance_requirements(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    category_id: Optional[UUID] = Query(None)
):
    """Get compliance requirements"""
    requirements = crud_compliance_requirement.get_by_organization(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        status=status,
        category_id=category_id
    )
    return requirements


@router.post("/requirements", response_model=ComplianceRequirement)
def create_compliance_requirement(
    *,
    db: Session = Depends(get_db),
    requirement_in: ComplianceRequirementCreate,
    current_user: User = Depends(deps.check_permission("compliance:create"))
):
    """Create new compliance requirement"""
    requirement_data = requirement_in.dict()
    requirement_data["organization_id"] = current_user.organization_id
    
    requirement = crud_compliance_requirement.create(db=db, obj_in=requirement_data)
    return requirement


@router.get("/requirements/overdue", response_model=List[ComplianceRequirement])
def get_overdue_requirements(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get overdue compliance requirements"""
    requirements = crud_compliance_requirement.get_overdue(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )
    return requirements


@router.get("/requirements/upcoming-reviews", response_model=List[ComplianceRequirement])
def get_upcoming_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    days_ahead: int = Query(30, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get requirements with upcoming reviews"""
    requirements = crud_compliance_requirement.get_upcoming_reviews(
        db,
        organization_id=current_user.organization_id,
        days_ahead=days_ahead,
        skip=skip,
        limit=limit
    )
    return requirements


@router.get("/requirements/{requirement_id}", response_model=ComplianceRequirement)
def get_compliance_requirement(
    requirement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get specific compliance requirement"""
    requirement = crud_compliance_requirement.get(db, id=requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    if requirement.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return requirement


@router.put("/requirements/{requirement_id}", response_model=ComplianceRequirement)
def update_compliance_requirement(
    requirement_id: UUID,
    requirement_update: ComplianceRequirementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permission("compliance:update"))
):
    """Update compliance requirement"""
    requirement = crud_compliance_requirement.get(db, id=requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    if requirement.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    requirement = crud_compliance_requirement.update(db=db, db_obj=requirement, obj_in=requirement_update)
    return requirement


# Compliance Assessments endpoints
@router.get("/assessments", response_model=List[ComplianceAssessment])
def get_compliance_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    assessment_type: Optional[str] = Query(None)
):
    """Get compliance assessments"""
    assessments = crud_compliance_assessment.get_by_organization(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        assessment_type=assessment_type
    )
    return assessments


@router.post("/assessments", response_model=ComplianceAssessment)
def create_compliance_assessment(
    *,
    db: Session = Depends(get_db),
    assessment_in: ComplianceAssessmentCreate,
    current_user: User = Depends(deps.check_permission("compliance:assess"))
):
    """Create new compliance assessment"""
    assessment_data = assessment_in.dict()
    assessment_data["organization_id"] = current_user.organization_id
    assessment_data["assessed_by_id"] = current_user.id
    
    assessment = crud_compliance_assessment.create(db=db, obj_in=assessment_data)
    return assessment


# Regulatory Updates endpoints
@router.get("/regulatory-updates", response_model=List[RegulatoryUpdate])
def get_regulatory_updates(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_reviewed: Optional[bool] = Query(None),
    impact_level: Optional[str] = Query(None)
):
    """Get regulatory updates"""
    updates = crud_regulatory_update.get_by_organization(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        is_reviewed=is_reviewed,
        impact_level=impact_level
    )
    return updates


@router.post("/regulatory-updates", response_model=RegulatoryUpdate)
def create_regulatory_update(
    *,
    db: Session = Depends(get_db),
    update_in: RegulatoryUpdateCreate,
    current_user: User = Depends(deps.check_permission("compliance:create"))
):
    """Create new regulatory update"""
    update_data = update_in.dict()
    update_data["organization_id"] = current_user.organization_id
    
    update = crud_regulatory_update.create(db=db, obj_in=update_data)
    return update


@router.get("/regulatory-updates/unreviewed", response_model=List[RegulatoryUpdate])
def get_unreviewed_updates(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get unreviewed regulatory updates"""
    updates = crud_regulatory_update.get_unreviewed(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )
    return updates


# AI-Powered Compliance Analysis Endpoints

@router.post("/ai/analyze", response_model=dict)
async def analyze_organization_compliance(
    analysis_type: str = Query(default="comprehensive", description="Type of analysis to perform"),
    regulatory_focus: Optional[List[str]] = Query(default=None, description="Specific regulatory domains to focus on"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Perform AI-powered compliance analysis for the organization

    Analysis types:
    - comprehensive: Full compliance analysis
    - violation_detection: Focus on detecting violations
    - regulatory_monitoring: Monitor regulatory changes
    - pattern_analysis: Analyze compliance patterns
    - trend_analysis: Analyze compliance trends
    - risk_assessment: Assess compliance risks
    """
    try:
        result = await compliance_ai_service.analyze_organization_compliance(
            db=db,
            organization_id=current_user.organization_id,
            analysis_type=analysis_type,
            regulatory_focus=regulatory_focus
        )

        return {
            "status": "success",
            "analysis_type": analysis_type,
            "organization_id": str(current_user.organization_id),
            "result": result.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance analysis failed: {str(e)}")


@router.post("/ai/analyze/requirement/{requirement_id}", response_model=dict)
async def analyze_compliance_requirement(
    requirement_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Perform AI-powered analysis of a specific compliance requirement
    """
    try:
        result = await compliance_ai_service.analyze_compliance_requirement(
            db=db,
            requirement_id=requirement_id,
            organization_id=current_user.organization_id
        )

        return {
            "status": "success",
            "requirement_id": str(requirement_id),
            "organization_id": str(current_user.organization_id),
            "result": result.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Requirement analysis failed: {str(e)}")


@router.post("/ai/monitoring/setup", response_model=dict)
async def setup_regulatory_monitoring(
    monitoring_scope: Optional[List[str]] = Query(default=None, description="Regulatory domains to monitor"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Set up AI-powered regulatory change monitoring

    Monitoring scope options: sec, finra, aml, sox, gdpr, basel, dodd_frank, mifid
    """
    try:
        result = await compliance_ai_service.monitor_regulatory_changes(
            db=db,
            organization_id=current_user.organization_id,
            monitoring_scope=monitoring_scope
        )

        return {
            "status": "success",
            "organization_id": str(current_user.organization_id),
            "monitoring_setup": result.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring setup failed: {str(e)}")


@router.post("/ai/analyze/regulatory-update", response_model=dict)
async def analyze_regulatory_update(
    update_content: str,
    regulation_type: str,
    organization_context: Optional[dict] = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Analyze the impact of a specific regulatory update using AI

    Regulation types: sec, finra, aml, sox, gdpr, basel, dodd_frank, mifid, general
    """
    try:
        result = await compliance_ai_service.analyze_regulatory_update(
            update_content=update_content,
            regulation_type=regulation_type,
            organization_context=organization_context or {}
        )

        return {
            "status": "success",
            "regulation_type": regulation_type,
            "organization_id": str(current_user.organization_id),
            "analysis": result.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regulatory update analysis failed: {str(e)}")


@router.get("/ai/status", response_model=dict)
def get_compliance_ai_status(
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get current status and capabilities of the Compliance AI service
    """
    try:
        status = compliance_ai_service.get_service_status()

        return {
            "status": "success",
            "service_status": status,
            "organization_id": str(current_user.organization_id)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI status: {str(e)}")


@router.get("/ai/insights/summary", response_model=dict)
async def get_compliance_ai_insights_summary(
    days: int = Query(default=30, description="Number of days to include in summary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get a summary of recent AI compliance insights and trends
    """
    try:
        # Perform quick analysis for insights summary
        result = await compliance_ai_service.analyze_organization_compliance(
            db=db,
            organization_id=current_user.organization_id,
            analysis_type="trend_analysis",
            regulatory_focus=None
        )

        # Extract key insights for summary
        insights_summary = {
            "compliance_score": result.ai_insights.compliance_score,
            "risk_level": result.ai_insights.risk_level,
            "violations_count": len(result.ai_insights.violations_detected),
            "regulatory_changes_count": len(result.ai_insights.regulatory_changes),
            "active_alerts_count": len(result.ai_insights.monitoring_alerts),
            "recommendations_count": len(result.ai_insights.recommendations),
            "confidence_level": result.ai_insights.confidence_level,
            "analysis_date": result.analysis_date,
            "model_version": result.model_version
        }

        return {
            "status": "success",
            "organization_id": str(current_user.organization_id),
            "time_period_days": days,
            "insights_summary": insights_summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights summary: {str(e)}")


@router.post("/reports/export/pdf")
async def export_compliance_report_pdf(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    audit_scope: dict = None,
    report_format: str = "detailed",
    compliance_areas: List[str] = None
) -> Any:
    """
    Export compliance report to PDF format
    """
    try:
        # Get compliance data for the organization
        organization_id = current_user.organization_id

        # Get compliance categories and assessments
        categories = crud_compliance_category.get_by_organization(db=db, organization_id=organization_id)
        assessments = crud_compliance_assessment.get_by_organization(db=db, organization_id=organization_id)

        # Calculate compliance metrics
        total_assessments = len(assessments)
        passed_assessments = len([a for a in assessments if a.status == "compliant"])
        failed_assessments = len([a for a in assessments if a.status == "non_compliant"])
        warning_assessments = len([a for a in assessments if a.status == "warning"])

        compliance_score = (passed_assessments / total_assessments * 100) if total_assessments > 0 else 0

        # Prepare compliance data for export
        compliance_data = {
            "audit_period": audit_scope.get("audit_period", "Last 30 days") if audit_scope else "Last 30 days",
            "compliance_areas": compliance_areas or ["All"],
            "report_type": report_format,
            "summary": {
                "total_checks": total_assessments,
                "passed": passed_assessments,
                "failed": failed_assessments,
                "warnings": warning_assessments,
                "compliance_score": compliance_score
            },
            "findings": []
        }

        # Add detailed findings
        for assessment in assessments:
            finding = {
                "category": assessment.category.name if assessment.category else "Unknown",
                "status": assessment.status,
                "description": assessment.assessment_details.get("description", "") if assessment.assessment_details else "",
                "risk_level": assessment.risk_level or "Medium"
            }
            compliance_data["findings"].append(finding)

        # Get organization name
        organization_name = current_user.organization.name if current_user.organization else "DealVerse Organization"

        # Export to PDF
        pdf_data = await export_service.export_compliance_report_to_pdf(
            compliance_data=compliance_data,
            organization_name=organization_name
        )

        from fastapi.responses import Response

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=compliance_report_{organization_name.replace(' ', '_')}.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export compliance report: {str(e)}"
        )


@router.get("/audit-trail")
async def get_audit_trail(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, description="Number of events to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of events to skip", ge=0)
) -> Any:
    """
    Get audit trail with filtering and pagination
    """
    try:
        organization_id = current_user.organization_id

        # Parse date filters
        start_datetime = None
        end_datetime = None

        if start_date:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        # Build filters
        filters = {}
        if event_type:
            filters["event_type"] = event_type
        if severity:
            filters["severity"] = severity
        if user_id:
            filters["user_id"] = user_id
        if resource_type:
            filters["resource_type"] = resource_type

        # Get audit trail
        audit_data = await audit_trails_service.get_audit_trail(
            db=db,
            organization_id=organization_id,
            filters=filters,
            start_date=start_datetime,
            end_date=end_datetime,
            limit=limit,
            offset=offset
        )

        return {
            "message": "Audit trail retrieved successfully",
            "audit_trail": audit_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audit trail: {str(e)}"
        )


@router.post("/audit-trail/log")
async def log_audit_event(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    event_type: str = Body(..., description="Type of audit event"),
    resource_type: str = Body(..., description="Type of resource affected"),
    resource_id: Optional[str] = Body(None, description="ID of resource affected"),
    details: Optional[Dict[str, Any]] = Body(None, description="Additional event details"),
    severity: Optional[str] = Body(None, description="Event severity level"),
    request: Request = None
) -> Any:
    """
    Log a custom audit event
    """
    try:
        # Get request context
        ip_address = None
        user_agent = None

        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        # Validate event type
        try:
            audit_event_type = AuditEventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")

        # Validate severity if provided
        audit_severity = None
        if severity:
            try:
                audit_severity = AuditSeverity(severity)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")

        # Log the audit event
        audit_event = await audit_trails_service.log_audit_event(
            db=db,
            event_type=audit_event_type,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            resource_type=resource_type,
            resource_id=UUID(resource_id) if resource_id else None,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=audit_severity
        )

        return {
            "message": "Audit event logged successfully",
            "event_id": audit_event["id"],
            "event": audit_event
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to log audit event: {str(e)}"
        )


@router.get("/audit-trail/compliance-report")
async def generate_audit_compliance_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    report_type: str = Query("comprehensive", description="Type of compliance report"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)")
) -> Any:
    """
    Generate a compliance report based on audit trails
    """
    try:
        organization_id = current_user.organization_id

        # Parse date range
        start_datetime = None
        end_datetime = None

        if start_date:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        # Generate compliance report
        compliance_report = await audit_trails_service.generate_compliance_report(
            db=db,
            organization_id=organization_id,
            report_type=report_type,
            start_date=start_datetime,
            end_date=end_datetime
        )

        return {
            "message": "Compliance report generated successfully",
            "report": compliance_report
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate compliance report: {str(e)}"
        )


@router.get("/audit-trail/event-types")
def get_audit_event_types(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all available audit event types
    """
    try:
        event_types = []

        for event_type in AuditEventType:
            # Categorize event types
            category = "other"
            if "user" in event_type.value:
                category = "user"
            elif "deal" in event_type.value:
                category = "deal"
            elif "client" in event_type.value:
                category = "client"
            elif "document" in event_type.value:
                category = "document"
            elif "model" in event_type.value:
                category = "financial_model"
            elif "presentation" in event_type.value:
                category = "presentation"
            elif "compliance" in event_type.value:
                category = "compliance"
            elif "system" in event_type.value:
                category = "system"
            elif "security" in event_type.value:
                category = "security"
            elif "data" in event_type.value:
                category = "data"
            elif "report" in event_type.value:
                category = "report"

            event_types.append({
                "value": event_type.value,
                "name": event_type.value.replace("_", " ").title(),
                "category": category
            })

        # Group by category
        categorized_events = {}
        for event in event_types:
            category = event["category"]
            if category not in categorized_events:
                categorized_events[category] = []
            categorized_events[category].append(event)

        return {
            "message": "Audit event types retrieved successfully",
            "event_types": event_types,
            "categorized_events": categorized_events,
            "total_types": len(event_types)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audit event types: {str(e)}"
        )


@router.get("/audit-trail/severity-levels")
def get_audit_severity_levels(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all available audit severity levels
    """
    try:
        severity_levels = []

        for severity in AuditSeverity:
            # Add description for each severity level
            description = ""
            if severity == AuditSeverity.LOW:
                description = "Routine operations and normal user activities"
            elif severity == AuditSeverity.MEDIUM:
                description = "Important operations that may require attention"
            elif severity == AuditSeverity.HIGH:
                description = "High-risk operations that require monitoring"
            elif severity == AuditSeverity.CRITICAL:
                description = "Critical operations that require immediate attention"

            severity_levels.append({
                "value": severity.value,
                "name": severity.value.title(),
                "description": description
            })

        return {
            "message": "Audit severity levels retrieved successfully",
            "severity_levels": severity_levels
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audit severity levels: {str(e)}"
        )
