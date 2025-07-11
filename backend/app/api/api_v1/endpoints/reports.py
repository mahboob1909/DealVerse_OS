"""
Custom Reports API endpoints
"""
from typing import Any, List, Optional, Dict
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api import deps
from app.db.database import get_db
from app.models.user import User
from app.services.custom_reports_service import custom_reports_service
from app.services.streaming_export_service import streaming_export_service
from app.crud.crud_deal import crud_deal
from app.crud.crud_client import crud_client
from app.crud.crud_document import crud_document

router = APIRouter()


class ReportGenerationRequest(BaseModel):
    template_id: str
    customizations: Optional[Dict[str, Any]] = None
    date_range_days: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    format_type: str = "pdf"
    title: Optional[str] = None


class ReportCustomization(BaseModel):
    sections: Optional[List[str]] = None
    charts: Optional[List[str]] = None
    title: Optional[str] = None
    branding: Optional[Dict[str, Any]] = None


@router.get("/templates")
def get_report_templates(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all available report templates
    """
    try:
        templates = custom_reports_service.get_available_templates()
        
        return {
            "message": "Report templates retrieved successfully",
            "templates": templates,
            "total_templates": len(templates)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get report templates: {str(e)}"
        )


@router.get("/templates/{template_id}")
def get_template_details(
    template_id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed information about a specific template
    """
    try:
        template_details = custom_reports_service.get_template_details(template_id)
        
        return {
            "message": "Template details retrieved successfully",
            "template": template_details,
            "template_id": template_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get template details: {str(e)}"
        )


@router.post("/generate")
async def generate_custom_report(
    request: ReportGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate a custom report based on template and customizations
    """
    try:
        organization_id = current_user.organization_id
        
        # Parse date range
        date_range = None
        if request.start_date and request.end_date:
            start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
            date_range = (start_date, end_date)
        elif request.date_range_days:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=request.date_range_days)
            date_range = (start_date, end_date)
        
        # Prepare customizations
        customizations = request.customizations or {}
        if request.title:
            customizations["title"] = request.title
        
        # Generate the report
        report = await custom_reports_service.generate_custom_report(
            db=db,
            organization_id=organization_id,
            template_id=request.template_id,
            customizations=customizations,
            date_range=date_range,
            format_type=request.format_type
        )
        
        # Return the report content as a file download
        if request.format_type == "pdf":
            media_type = "application/pdf"
            file_extension = "pdf"
        elif request.format_type == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_extension = "xlsx"
        else:
            raise HTTPException(status_code=400, detail="Unsupported format type")
        
        filename = f"{request.template_id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        
        return Response(
            content=report["content"],
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Report-ID": report["report_id"],
                "X-Template-ID": report["template_id"],
                "X-Generated-At": report["generated_at"]
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post("/preview")
async def preview_report_data(
    request: ReportGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Preview report data without generating the actual file
    """
    try:
        organization_id = current_user.organization_id
        
        # Parse date range
        date_range = None
        if request.start_date and request.end_date:
            start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
            date_range = (start_date, end_date)
        elif request.date_range_days:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=request.date_range_days)
            date_range = (start_date, end_date)
        
        # Get template details
        template = custom_reports_service.get_template_details(request.template_id)
        
        # Prepare customizations
        customizations = request.customizations or {}
        if request.title:
            customizations["title"] = request.title
        
        # Generate report data (without creating the file)
        if not date_range:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=template["default_period"])
            date_range = (start_date, end_date)
        
        report_data = await custom_reports_service._generate_report_data(
            db=db,
            organization_id=organization_id,
            template=template,
            customizations=customizations,
            date_range=date_range
        )
        
        # Apply customizations
        report_data = custom_reports_service._apply_customizations(report_data, customizations)
        
        return {
            "message": "Report preview generated successfully",
            "preview": {
                "template_id": request.template_id,
                "template_name": template["name"],
                "date_range": {
                    "start": date_range[0].isoformat(),
                    "end": date_range[1].isoformat()
                },
                "sections": list(report_data["sections"].keys()),
                "charts": list(report_data["charts"].keys()),
                "summary": report_data["summary"],
                "sample_data": {
                    section_id: {
                        "title": section_data.get("title", ""),
                        "metrics_count": len(section_data.get("metrics", {})),
                        "has_data": not section_data.get("placeholder", False)
                    }
                    for section_id, section_data in report_data["sections"].items()
                }
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report preview: {str(e)}"
        )


@router.get("/templates/{template_id}/sections")
def get_template_sections(
    template_id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get available sections for a specific template
    """
    try:
        template = custom_reports_service.get_template_details(template_id)
        
        # Define section descriptions
        section_descriptions = {
            "overview_metrics": "High-level business metrics and KPIs",
            "deal_performance": "Detailed deal analytics and performance metrics",
            "client_insights": "Client portfolio analysis and insights",
            "team_productivity": "Team performance and productivity metrics",
            "financial_highlights": "Financial performance and projections",
            "sales_funnel": "Sales funnel analysis and conversion rates",
            "forecasting": "Predictive analytics and forecasting",
            "compliance_overview": "Compliance status and audit findings",
            "deal_analytics": "Comprehensive deal analysis",
            "client_overview": "Client portfolio overview",
            "industry_analysis": "Industry distribution and trends",
            "client_value_analysis": "Client value segmentation",
            "retention_metrics": "Client retention and churn analysis",
            "growth_opportunities": "Identified growth opportunities",
            "revenue_analysis": "Revenue trends and analysis",
            "deal_value_trends": "Deal value patterns and trends",
            "financial_projections": "Financial forecasting and projections",
            "roi_analysis": "Return on investment analysis",
            "budget_vs_actual": "Budget performance analysis",
            "team_overview": "Team composition and overview",
            "individual_performance": "Individual team member performance",
            "productivity_metrics": "Team productivity measurements",
            "goal_tracking": "Goal progress and achievement tracking",
            "development_recommendations": "Team development suggestions",
            "audit_findings": "Detailed audit findings and issues",
            "risk_assessment": "Risk analysis and assessment",
            "remediation_plan": "Compliance remediation recommendations",
            "regulatory_updates": "Recent regulatory changes and updates"
        }
        
        sections = []
        for section_id in template["sections"]:
            sections.append({
                "id": section_id,
                "name": section_id.replace("_", " ").title(),
                "description": section_descriptions.get(section_id, "Section description not available")
            })
        
        return {
            "message": "Template sections retrieved successfully",
            "template_id": template_id,
            "template_name": template["name"],
            "sections": sections,
            "total_sections": len(sections)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get template sections: {str(e)}"
        )


@router.get("/templates/{template_id}/charts")
def get_template_charts(
    template_id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get available charts for a specific template
    """
    try:
        template = custom_reports_service.get_template_details(template_id)
        
        # Define chart descriptions
        chart_descriptions = {
            "deal_pipeline": "Bar chart showing deal distribution by stage",
            "revenue_trend": "Line chart showing revenue trends over time",
            "win_rate_chart": "Gauge chart displaying current win rate",
            "sales_funnel": "Funnel chart showing sales conversion stages",
            "team_leaderboard": "Bar chart ranking team performance",
            "monthly_trends": "Line chart showing monthly performance trends",
            "industry_distribution": "Pie chart showing client industry breakdown",
            "client_value_segments": "Bar chart showing client value distribution",
            "retention_trends": "Line chart showing client retention over time",
            "revenue_chart": "Bar chart showing revenue by period",
            "projection_chart": "Line chart showing financial projections",
            "roi_analysis": "Bar chart showing ROI by investment",
            "team_performance": "Horizontal bar chart showing team metrics",
            "individual_metrics": "Bar chart showing individual performance",
            "goal_progress": "Progress chart showing goal achievement",
            "compliance_score": "Gauge chart showing compliance rating",
            "risk_matrix": "Matrix chart showing risk assessment",
            "audit_timeline": "Timeline chart showing audit progress"
        }
        
        charts = []
        for chart_id in template.get("charts", []):
            charts.append({
                "id": chart_id,
                "name": chart_id.replace("_", " ").title(),
                "description": chart_descriptions.get(chart_id, "Chart description not available"),
                "type": "visualization"
            })
        
        return {
            "message": "Template charts retrieved successfully",
            "template_id": template_id,
            "template_name": template["name"],
            "charts": charts,
            "total_charts": len(charts)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get template charts: {str(e)}"
        )


@router.get("/export/deals/stream")
async def stream_deals_export(
    db: Session = Depends(get_db),
    format_type: str = Query("excel", description="Export format: excel, pdf, csv"),
    stage: Optional[str] = Query(None, description="Filter by deal stage"),
    status: Optional[str] = Query(None, description="Filter by deal status"),
    current_user: User = Depends(deps.get_current_active_user),
) -> StreamingResponse:
    """
    Stream large deals export with progress tracking
    """
    try:
        organization_id = current_user.organization_id

        # Get total count for progress calculation
        total_deals = crud_deal.count_by_organization(
            db,
            organization_id=organization_id,
            stage=stage,
            status=status
        )

        if total_deals == 0:
            raise HTTPException(status_code=404, detail="No deals found for export")

        # Create data generator function
        async def get_deals_chunk(offset: int, limit: int):
            deals = crud_deal.get_by_organization(
                db,
                organization_id=organization_id,
                skip=offset,
                limit=limit,
                stage=stage,
                status=status,
                include_relations=True
            )

            # Convert to dict format
            deals_data = []
            for deal in deals:
                deal_dict = {
                    "ID": str(deal.id),
                    "Title": deal.title,
                    "Type": deal.deal_type,
                    "Stage": deal.stage,
                    "Status": deal.status,
                    "Value": float(deal.deal_value) if deal.deal_value else 0,
                    "Currency": deal.currency,
                    "Target Company": deal.target_company,
                    "Industry": deal.target_industry,
                    "Location": deal.target_location,
                    "Expected Close": deal.expected_close_date.isoformat() if deal.expected_close_date else "",
                    "Created": deal.created_at.isoformat(),
                    "Updated": deal.updated_at.isoformat(),
                    "Client": deal.client.name if deal.client else "",
                    "Created By": deal.created_by.full_name if deal.created_by else ""
                }
                deals_data.append(deal_dict)

            return deals_data

        # Create data generator
        data_generator = streaming_export_service.create_data_generator(
            get_deals_chunk,
            total_deals,
            chunk_size=500
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"deals_export_{timestamp}.{format_type}"

        # Stream export based on format
        if format_type.lower() == "excel":
            headers = list(next(await data_generator.__anext__())[0].keys()) if total_deals > 0 else []
            data_generator = streaming_export_service.create_data_generator(
                get_deals_chunk, total_deals, chunk_size=500
            )
            return await streaming_export_service.stream_excel_export(
                data_generator, headers, filename
            )
        elif format_type.lower() == "pdf":
            return await streaming_export_service.stream_pdf_export(
                data_generator, "Deals Export Report", filename
            )
        elif format_type.lower() == "csv":
            return await streaming_export_service.stream_csv_export(
                data_generator, filename
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported format type")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


@router.get("/export/progress/{export_id}")
def get_export_progress(
    export_id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get export progress by ID
    """
    progress = streaming_export_service.get_export_progress(export_id)

    if not progress:
        raise HTTPException(status_code=404, detail="Export progress not found")

    return progress
