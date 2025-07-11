"""
Analytics and reporting endpoints
"""
from typing import Any, Dict, List
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_deal import crud_deal
from app.crud.crud_client import crud_client
from app.crud.crud_user import crud_user
from app.db.database import get_db
from app.models.user import User
from app.services.export_service import export_service
from app.services.advanced_analytics_service import advanced_analytics_service
from app.middleware.cache_middleware import cache_response
from app.services.cache_service import cache_service, cached

router = APIRouter()


@router.get("/dashboard")
@cache_response(ttl=120, key_prefix="dashboard")
def get_dashboard_analytics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get comprehensive dashboard analytics with caching
    """
    organization_id = current_user.organization_id

    # Generate cache key for dashboard data
    cache_key = cache_service._generate_key(
        "dashboard_analytics",
        str(organization_id)
    )

    # Try cache first
    cached_dashboard = cache_service.get(cache_key)
    if cached_dashboard is not None:
        return cached_dashboard

    # Get deal statistics
    deal_stats = crud_deal.get_organization_stats(db, organization_id=organization_id)

    # Get client statistics
    client_stats = crud_client.get_organization_stats(db, organization_id=organization_id)

    # Get recent deals with relations for better performance
    recent_deals_raw = crud_deal.get_recent_deals(
        db,
        organization_id=organization_id,
        limit=5,
        include_relations=True
    )

    # Convert Deal objects to dictionaries for serialization
    recent_deals = []
    for deal in recent_deals_raw:
        recent_deals.append({
            "id": str(deal.id),
            "title": deal.title,
            "deal_type": deal.deal_type,
            "deal_value": float(deal.deal_value) if deal.deal_value else None,
            "currency": deal.currency,
            "stage": deal.stage,
            "status": deal.status,
            "target_company": deal.target_company,
            "expected_close_date": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
            "created_at": deal.created_at.isoformat(),
            "updated_at": deal.updated_at.isoformat()
        })
    
    # Get team statistics
    team_count = crud_user.get_by_organization(db, organization_id=organization_id, limit=1000)
    team_stats = {
        "total_users": len(team_count),
        "active_users": len([u for u in team_count if u.is_active]),
        "roles": {}
    }
    
    # Count users by role
    for user in team_count:
        role = user.role
        team_stats["roles"][role] = team_stats["roles"].get(role, 0) + 1
    
    # Prepare dashboard data
    dashboard_data = {
        "deals": deal_stats,
        "clients": client_stats,
        "team": team_stats,
        "recent_deals": recent_deals,
        "recent_clients": client_stats.get("recent_clients", [])
    }

    # Cache the dashboard data
    cache_service.set(cache_key, dashboard_data, ttl=120)

    return dashboard_data


@router.get("/deals/performance")
def get_deals_performance(
    db: Session = Depends(get_db),
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get deal performance analytics
    """
    organization_id = current_user.organization_id
    
    # Get basic deal stats
    deal_stats = crud_deal.get_organization_stats(db, organization_id=organization_id)
    
    # Calculate performance metrics
    performance_metrics = {
        "conversion_rate": deal_stats.get("win_rate", 0),
        "average_deal_size": deal_stats.get("average_deal_size", 0),
        "total_pipeline_value": deal_stats.get("total_value", 0),
        "deals_closed_this_month": deal_stats.get("closed_deals", 0),
        "active_opportunities": deal_stats.get("active_deals", 0),
        "stage_distribution": deal_stats.get("deals_by_stage", {}),
        "type_distribution": deal_stats.get("deals_by_type", {}),
        "monthly_trends": deal_stats.get("monthly_revenue", [])
    }
    
    return performance_metrics


@router.get("/clients/insights")
def get_client_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get client relationship insights
    """
    organization_id = current_user.organization_id
    
    # Get client statistics
    client_stats = crud_client.get_organization_stats(db, organization_id=organization_id)
    
    # Calculate client insights
    insights = {
        "total_clients": client_stats.get("total_clients", 0),
        "client_acquisition": {
            "prospects": client_stats.get("prospects", 0),
            "active_clients": client_stats.get("active_clients", 0),
            "conversion_rate": 0  # Calculate based on historical data
        },
        "industry_breakdown": client_stats.get("clients_by_industry", {}),
        "source_analysis": client_stats.get("clients_by_source", {}),
        "relationship_status": client_stats.get("clients_by_type", {}),
        "recent_activity": client_stats.get("recent_clients", [])
    }
    
    # Calculate conversion rate
    total_prospects = client_stats.get("prospects", 0)
    active_clients = client_stats.get("active_clients", 0)
    if total_prospects > 0:
        insights["client_acquisition"]["conversion_rate"] = round(
            (active_clients / (total_prospects + active_clients)) * 100, 2
        )
    
    return insights


@router.get("/team/productivity")
def get_team_productivity(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get team productivity analytics
    """
    organization_id = current_user.organization_id
    
    # Get team members
    team_members = crud_user.get_by_organization(db, organization_id=organization_id, limit=1000)
    
    # Calculate productivity metrics
    productivity_metrics = {
        "team_size": len(team_members),
        "active_members": len([u for u in team_members if u.is_active]),
        "role_distribution": {},
        "recent_activity": [],
        "performance_indicators": {
            "deals_per_user": 0,
            "clients_per_user": 0,
            "average_deal_value": 0
        }
    }
    
    # Count by role
    for user in team_members:
        role = user.role
        productivity_metrics["role_distribution"][role] = \
            productivity_metrics["role_distribution"].get(role, 0) + 1
    
    # Get deal and client counts for performance indicators
    deal_stats = crud_deal.get_organization_stats(db, organization_id=organization_id)
    client_stats = crud_client.get_organization_stats(db, organization_id=organization_id)
    
    if len(team_members) > 0:
        productivity_metrics["performance_indicators"]["deals_per_user"] = round(
            deal_stats.get("total_deals", 0) / len(team_members), 2
        )
        productivity_metrics["performance_indicators"]["clients_per_user"] = round(
            client_stats.get("total_clients", 0) / len(team_members), 2
        )
    
    productivity_metrics["performance_indicators"]["average_deal_value"] = \
        deal_stats.get("average_deal_size", 0)
    
    return productivity_metrics


@router.get("/reports/executive-summary")
def get_executive_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permission("analytics:read")),
) -> Any:
    """
    Get executive summary report
    """
    organization_id = current_user.organization_id
    
    # Get all statistics
    deal_stats = crud_deal.get_organization_stats(db, organization_id=organization_id)
    client_stats = crud_client.get_organization_stats(db, organization_id=organization_id)
    team_members = crud_user.get_by_organization(db, organization_id=organization_id, limit=1000)
    
    # Create executive summary
    summary = {
        "period": "Current Period",
        "generated_at": datetime.utcnow().isoformat(),
        "key_metrics": {
            "total_deals": deal_stats.get("total_deals", 0),
            "active_deals": deal_stats.get("active_deals", 0),
            "total_pipeline_value": deal_stats.get("total_value", 0),
            "win_rate": deal_stats.get("win_rate", 0),
            "total_clients": client_stats.get("total_clients", 0),
            "team_size": len(team_members)
        },
        "performance_highlights": {
            "deals_closed": deal_stats.get("closed_deals", 0),
            "new_clients": client_stats.get("prospects", 0),
            "average_deal_size": deal_stats.get("average_deal_size", 0),
            "client_conversion_rate": 0  # Calculate based on data
        },
        "trends": {
            "deal_stages": deal_stats.get("deals_by_stage", {}),
            "client_industries": client_stats.get("clients_by_industry", {}),
            "monthly_performance": deal_stats.get("monthly_revenue", [])
        },
        "recommendations": [
            "Focus on high-value prospects in top-performing industries",
            "Optimize deal pipeline for faster conversion",
            "Expand team in high-growth areas",
            "Implement additional client retention strategies"
        ]
    }
    
    return summary


@router.get("/export/excel")
async def export_analytics_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Export analytics dashboard data to Excel format
    """
    try:
        organization_id = current_user.organization_id

        # Get analytics data
        deal_stats = crud_deal.get_organization_stats(db, organization_id=organization_id)
        client_stats = crud_client.get_organization_stats(db, organization_id=organization_id)
        team_members = crud_user.get_by_organization(db, organization_id=organization_id, limit=1000)

        # Prepare analytics data for export
        analytics_data = {
            "kpis": {
                "total_deals": deal_stats.get("total_deals", 0),
                "active_deals": deal_stats.get("active_deals", 0),
                "total_deal_value": deal_stats.get("total_deal_value", 0),
                "average_deal_size": deal_stats.get("average_deal_size", 0),
                "total_clients": client_stats.get("total_clients", 0),
                "active_clients": client_stats.get("active_clients", 0),
                "team_members": len(team_members)
            },
            "metrics": [
                {
                    "name": "Deal Conversion Rate",
                    "current_value": deal_stats.get("conversion_rate", 0),
                    "previous_value": deal_stats.get("previous_conversion_rate", 0),
                    "change_percent": deal_stats.get("conversion_rate_change", 0)
                },
                {
                    "name": "Average Deal Duration",
                    "current_value": deal_stats.get("average_duration", 0),
                    "previous_value": deal_stats.get("previous_average_duration", 0),
                    "change_percent": deal_stats.get("duration_change", 0)
                },
                {
                    "name": "Client Satisfaction",
                    "current_value": client_stats.get("satisfaction_score", 0),
                    "previous_value": client_stats.get("previous_satisfaction", 0),
                    "change_percent": client_stats.get("satisfaction_change", 0)
                }
            ],
            "trends": [
                {
                    "date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    "metric": "Total Deals",
                    "value": deal_stats.get("deals_30_days_ago", 0)
                },
                {
                    "date": (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
                    "metric": "Total Deals",
                    "value": deal_stats.get("deals_15_days_ago", 0)
                },
                {
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "metric": "Total Deals",
                    "value": deal_stats.get("total_deals", 0)
                }
            ]
        }

        # Get organization name
        organization_name = current_user.organization.name if current_user.organization else "DealVerse Organization"

        # Export to Excel
        excel_data = await export_service.export_analytics_to_excel(
            analytics_data=analytics_data,
            organization_name=organization_name
        )

        from fastapi.responses import Response

        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=analytics_dashboard_{organization_name.replace(' ', '_')}.xlsx"
            }
        )

    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export analytics to Excel: {str(e)}"
        )


@router.get("/advanced")
def get_advanced_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    days: int = Query(90, description="Number of days to analyze", ge=7, le=365)
) -> Any:
    """
    Get advanced analytics dashboard with business intelligence features
    """
    try:
        organization_id = current_user.organization_id

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = (start_date, end_date)

        # Get comprehensive analytics
        analytics = advanced_analytics_service.get_comprehensive_dashboard_analytics(
            db=db,
            organization_id=organization_id,
            date_range=date_range
        )

        return {
            "message": "Advanced analytics retrieved successfully",
            "analytics": analytics
        }

    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get advanced analytics: {str(e)}"
        )


@router.get("/insights")
def get_business_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    focus_area: str = Query("all", description="Focus area: deals, clients, team, financial")
) -> Any:
    """
    Get focused business insights for specific areas
    """
    try:
        organization_id = current_user.organization_id

        # Get comprehensive analytics first
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        date_range = (start_date, end_date)

        full_analytics = advanced_analytics_service.get_comprehensive_dashboard_analytics(
            db=db,
            organization_id=organization_id,
            date_range=date_range
        )

        # Extract focused insights based on area
        if focus_area == "deals":
            insights = {
                "focus_area": "deals",
                "analytics": full_analytics["deal_analytics"],
                "kpis": full_analytics["kpis"]["growth_metrics"],
                "trends": full_analytics["trends"],
                "recommendations": full_analytics["predictions"]["recommendations"]
            }
        elif focus_area == "clients":
            insights = {
                "focus_area": "clients",
                "analytics": full_analytics["client_analytics"],
                "kpis": full_analytics["kpis"]["revenue_efficiency"],
                "recommendations": []
            }
        elif focus_area == "team":
            insights = {
                "focus_area": "team",
                "analytics": full_analytics["team_analytics"],
                "kpis": full_analytics["kpis"]["operational_efficiency"],
                "recommendations": []
            }
        elif focus_area == "financial":
            insights = {
                "focus_area": "financial",
                "analytics": full_analytics["financial_analytics"],
                "kpis": full_analytics["kpis"]["revenue_efficiency"],
                "predictions": full_analytics["predictions"],
                "recommendations": []
            }
        else:
            insights = full_analytics

        return {
            "message": f"Business insights for {focus_area} retrieved successfully",
            "insights": insights
        }

    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get business insights: {str(e)}"
        )


@router.get("/benchmarks")
def get_performance_benchmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get performance benchmarks and industry comparisons
    """
    try:
        organization_id = current_user.organization_id

        # Get deal analytics for benchmarking
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        deal_analytics = advanced_analytics_service._get_deal_analytics(
            db=db,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date
        )

        benchmarks = advanced_analytics_service._get_performance_benchmarks(
            db=db,
            organization_id=organization_id,
            deal_analytics=deal_analytics
        )

        return {
            "message": "Performance benchmarks retrieved successfully",
            "benchmarks": benchmarks,
            "current_performance": {
                "win_rate": deal_analytics.get("win_rate", 0),
                "average_deal_duration": deal_analytics.get("average_deal_duration_days", 0),
                "average_deal_size": deal_analytics.get("average_deal_size", 0),
                "total_pipeline_value": deal_analytics.get("total_pipeline_value", 0)
            }
        }

    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance benchmarks: {str(e)}"
        )


@router.get("/predictions")
def get_predictive_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    prediction_period: int = Query(30, description="Prediction period in days", ge=7, le=90)
) -> Any:
    """
    Get predictive analytics and forecasting
    """
    try:
        organization_id = current_user.organization_id

        # Get historical data for predictions
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)  # Use 90 days of history
        date_range = (start_date, end_date)

        # Get analytics and trends
        deal_analytics = advanced_analytics_service._get_deal_analytics(
            db=db,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date
        )

        trends = advanced_analytics_service._get_trend_analysis(
            db=db,
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date
        )

        predictions = advanced_analytics_service._get_predictive_insights(
            db=db,
            organization_id=organization_id,
            deal_analytics=deal_analytics,
            trends=trends
        )

        return {
            "message": f"Predictive analytics for {prediction_period} days retrieved successfully",
            "predictions": predictions,
            "historical_trends": trends,
            "prediction_period_days": prediction_period
        }

    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get predictive analytics: {str(e)}"
        )
