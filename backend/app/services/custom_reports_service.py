#!/usr/bin/env python3
"""
Custom Reports Service for DealVerse OS
Provides automated report creation with templates and customization options
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc

from app.crud.crud_deal import crud_deal
from app.crud.crud_client import crud_client
from app.crud.crud_user import crud_user
from app.crud.crud_financial_model import crud_financial_model
from app.crud.crud_presentation import crud_presentation
from app.services.export_service import export_service
from app.services.advanced_analytics_service import advanced_analytics_service
import logging

logger = logging.getLogger(__name__)


class CustomReportsService:
    """Service for custom report generation with templates"""
    
    def __init__(self):
        self.report_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize predefined report templates"""
        return {
            "executive_summary": {
                "name": "Executive Summary Report",
                "description": "High-level overview of business performance",
                "sections": [
                    "overview_metrics",
                    "deal_performance",
                    "client_insights",
                    "team_productivity",
                    "financial_highlights"
                ],
                "default_period": 90,
                "format_options": ["pdf", "excel"],
                "charts": ["deal_pipeline", "revenue_trend", "win_rate_chart"]
            },
            "sales_performance": {
                "name": "Sales Performance Report",
                "description": "Detailed analysis of sales activities and results",
                "sections": [
                    "deal_analytics",
                    "sales_funnel",
                    "team_performance",
                    "client_acquisition",
                    "forecasting"
                ],
                "default_period": 30,
                "format_options": ["pdf", "excel"],
                "charts": ["sales_funnel", "team_leaderboard", "monthly_trends"]
            },
            "client_analysis": {
                "name": "Client Analysis Report",
                "description": "Comprehensive client portfolio and relationship analysis",
                "sections": [
                    "client_overview",
                    "industry_analysis",
                    "client_value_analysis",
                    "retention_metrics",
                    "growth_opportunities"
                ],
                "default_period": 180,
                "format_options": ["pdf", "excel"],
                "charts": ["industry_distribution", "client_value_segments", "retention_trends"]
            },
            "financial_summary": {
                "name": "Financial Summary Report",
                "description": "Financial performance and projections overview",
                "sections": [
                    "revenue_analysis",
                    "deal_value_trends",
                    "financial_projections",
                    "roi_analysis",
                    "budget_vs_actual"
                ],
                "default_period": 90,
                "format_options": ["pdf", "excel"],
                "charts": ["revenue_chart", "projection_chart", "roi_analysis"]
            },
            "team_productivity": {
                "name": "Team Productivity Report",
                "description": "Team performance metrics and individual contributions",
                "sections": [
                    "team_overview",
                    "individual_performance",
                    "productivity_metrics",
                    "goal_tracking",
                    "development_recommendations"
                ],
                "default_period": 30,
                "format_options": ["pdf", "excel"],
                "charts": ["team_performance", "individual_metrics", "goal_progress"]
            },
            "compliance_audit": {
                "name": "Compliance Audit Report",
                "description": "Comprehensive compliance status and audit findings",
                "sections": [
                    "compliance_overview",
                    "audit_findings",
                    "risk_assessment",
                    "remediation_plan",
                    "regulatory_updates"
                ],
                "default_period": 90,
                "format_options": ["pdf"],
                "charts": ["compliance_score", "risk_matrix", "audit_timeline"]
            }
        }
    
    async def generate_custom_report(
        self,
        db: Session,
        organization_id: UUID,
        template_id: str,
        customizations: Optional[Dict[str, Any]] = None,
        date_range: Optional[tuple] = None,
        format_type: str = "pdf"
    ) -> Dict[str, Any]:
        """Generate a custom report based on template and customizations"""
        
        if template_id not in self.report_templates:
            raise ValueError(f"Unknown template: {template_id}")
        
        template = self.report_templates[template_id]
        customizations = customizations or {}
        
        # Set date range
        if not date_range:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=template["default_period"])
            date_range = (start_date, end_date)
        
        # Generate report data
        report_data = await self._generate_report_data(
            db=db,
            organization_id=organization_id,
            template=template,
            customizations=customizations,
            date_range=date_range
        )
        
        # Apply customizations
        report_data = self._apply_customizations(report_data, customizations)
        
        # Generate the report in requested format
        if format_type == "pdf":
            report_content = await self._generate_pdf_report(report_data, template)
        elif format_type == "excel":
            report_content = await self._generate_excel_report(report_data, template)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return {
            "report_id": str(uuid4()),
            "template_id": template_id,
            "template_name": template["name"],
            "generated_at": datetime.utcnow().isoformat(),
            "date_range": {
                "start": date_range[0].isoformat(),
                "end": date_range[1].isoformat()
            },
            "format": format_type,
            "content": report_content,
            "metadata": {
                "organization_id": str(organization_id),
                "sections_included": report_data.get("sections", []),
                "customizations_applied": list(customizations.keys()) if customizations else []
            }
        }
    
    async def _generate_report_data(
        self,
        db: Session,
        organization_id: UUID,
        template: Dict,
        customizations: Dict,
        date_range: tuple
    ) -> Dict[str, Any]:
        """Generate the core data for the report"""
        
        start_date, end_date = date_range
        
        # Get comprehensive analytics
        analytics = advanced_analytics_service.get_comprehensive_dashboard_analytics(
            db=db,
            organization_id=organization_id,
            date_range=date_range
        )
        
        # Build report data based on template sections
        report_data = {
            "template_name": template["name"],
            "description": template["description"],
            "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "sections": {},
            "charts": {},
            "summary": {}
        }
        
        # Generate each section
        for section in template["sections"]:
            report_data["sections"][section] = await self._generate_section_data(
                section, analytics, db, organization_id, date_range
            )
        
        # Generate charts
        for chart in template.get("charts", []):
            report_data["charts"][chart] = self._generate_chart_data(chart, analytics)
        
        # Generate executive summary
        report_data["summary"] = self._generate_executive_summary(analytics, template)
        
        return report_data
    
    async def _generate_section_data(
        self,
        section: str,
        analytics: Dict,
        db: Session,
        organization_id: UUID,
        date_range: tuple
    ) -> Dict[str, Any]:
        """Generate data for a specific report section"""
        
        if section == "overview_metrics":
            return {
                "title": "Business Overview",
                "metrics": {
                    "total_deals": analytics["deal_analytics"]["total_deals"],
                    "active_deals": analytics["deal_analytics"]["active_deals"],
                    "win_rate": analytics["deal_analytics"]["win_rate"],
                    "pipeline_value": analytics["deal_analytics"]["total_pipeline_value"],
                    "team_size": analytics["team_analytics"]["total_team_members"],
                    "client_count": analytics["client_analytics"]["total_clients"]
                }
            }
        
        elif section == "deal_performance":
            return {
                "title": "Deal Performance Analysis",
                "metrics": analytics["deal_analytics"],
                "trends": analytics["trends"]["weekly_trends"],
                "stage_distribution": analytics["deal_analytics"]["stage_distribution"],
                "conversion_funnel": analytics["deal_analytics"]["conversion_funnel"]
            }
        
        elif section == "client_insights":
            return {
                "title": "Client Portfolio Insights",
                "metrics": analytics["client_analytics"],
                "industry_breakdown": analytics["client_analytics"]["industry_distribution"],
                "top_industries": analytics["client_analytics"]["top_industries"],
                "acquisition_trends": {
                    "new_clients": analytics["client_analytics"]["new_clients_in_period"],
                    "acquisition_rate": analytics["client_analytics"]["client_acquisition_rate"]
                }
            }
        
        elif section == "team_productivity":
            return {
                "title": "Team Performance & Productivity",
                "metrics": analytics["team_analytics"],
                "top_performers": analytics["team_analytics"]["team_productivity"]["top_performers"],
                "productivity_metrics": analytics["kpis"]["operational_efficiency"]
            }
        
        elif section == "financial_highlights":
            return {
                "title": "Financial Performance Highlights",
                "metrics": analytics["financial_analytics"],
                "revenue_efficiency": analytics["kpis"]["revenue_efficiency"],
                "projections": analytics["predictions"]["next_month_projection"]
            }
        
        elif section == "sales_funnel":
            return {
                "title": "Sales Funnel Analysis",
                "funnel_data": analytics["deal_analytics"]["conversion_funnel"],
                "conversion_rates": self._calculate_conversion_rates(analytics["deal_analytics"]),
                "bottlenecks": self._identify_funnel_bottlenecks(analytics["deal_analytics"])
            }
        
        elif section == "forecasting":
            return {
                "title": "Sales Forecasting",
                "predictions": analytics["predictions"],
                "trends": analytics["trends"],
                "recommendations": analytics["predictions"]["recommendations"]
            }
        
        elif section == "compliance_overview":
            # This would integrate with compliance data when available
            return {
                "title": "Compliance Status Overview",
                "status": "Data not available - integrate with compliance module",
                "placeholder": True
            }
        
        else:
            return {
                "title": f"Section: {section.replace('_', ' ').title()}",
                "content": "Section data not implemented",
                "placeholder": True
            }
    
    def _generate_chart_data(self, chart_type: str, analytics: Dict) -> Dict[str, Any]:
        """Generate chart data for visualization"""
        
        if chart_type == "deal_pipeline":
            return {
                "type": "bar",
                "title": "Deal Pipeline by Stage",
                "data": analytics["deal_analytics"]["stage_distribution"],
                "labels": list(analytics["deal_analytics"]["stage_distribution"].keys()),
                "values": list(analytics["deal_analytics"]["stage_distribution"].values())
            }
        
        elif chart_type == "revenue_trend":
            weekly_trends = analytics["trends"]["weekly_trends"]
            return {
                "type": "line",
                "title": "Revenue Trend",
                "data": {
                    "labels": [w["week_start"][:10] for w in weekly_trends],
                    "values": [w["total_value"] for w in weekly_trends]
                }
            }
        
        elif chart_type == "win_rate_chart":
            return {
                "type": "gauge",
                "title": "Win Rate",
                "value": analytics["deal_analytics"]["win_rate"],
                "max_value": 100,
                "unit": "%"
            }
        
        elif chart_type == "team_performance":
            top_performers = analytics["team_analytics"]["team_productivity"]["top_performers"]
            return {
                "type": "horizontal_bar",
                "title": "Team Performance",
                "data": {
                    "labels": [p["name"] for p in top_performers[:5]],
                    "values": [p["total_value"] for p in top_performers[:5]]
                }
            }
        
        elif chart_type == "industry_distribution":
            return {
                "type": "pie",
                "title": "Client Industry Distribution",
                "data": analytics["client_analytics"]["industry_distribution"]
            }
        
        else:
            return {
                "type": "placeholder",
                "title": f"Chart: {chart_type.replace('_', ' ').title()}",
                "message": "Chart data not implemented"
            }
    
    def _generate_executive_summary(self, analytics: Dict, template: Dict) -> Dict[str, Any]:
        """Generate executive summary for the report"""
        
        # Key insights based on analytics
        insights = []
        
        win_rate = analytics["deal_analytics"]["win_rate"]
        if win_rate > 50:
            insights.append(f"Strong sales performance with {win_rate:.1f}% win rate")
        elif win_rate < 25:
            insights.append(f"Win rate of {win_rate:.1f}% indicates need for sales process improvement")
        
        pipeline_value = analytics["deal_analytics"]["total_pipeline_value"]
        if pipeline_value > 1000000:
            insights.append(f"Healthy pipeline value of ${pipeline_value:,.0f}")
        
        team_productivity = analytics["team_analytics"]["team_productivity"]["average_deals_per_user"]
        insights.append(f"Team averaging {team_productivity:.1f} deals per member")
        
        # Recommendations from predictions
        recommendations = analytics["predictions"].get("recommendations", [])
        
        return {
            "title": "Executive Summary",
            "period": template["default_period"],
            "key_insights": insights,
            "recommendations": recommendations,
            "overall_performance": analytics["benchmarks"]["overall_score"]["rating"],
            "performance_score": analytics["benchmarks"]["overall_score"]["score"]
        }
    
    def _calculate_conversion_rates(self, deal_analytics: Dict) -> Dict[str, float]:
        """Calculate conversion rates between funnel stages"""
        
        funnel = deal_analytics["conversion_funnel"]
        conversion_rates = {}
        
        stages = ["prospecting", "qualification", "proposal", "negotiation", "closed_won"]
        
        for i in range(len(stages) - 1):
            current_stage = stages[i]
            next_stage = stages[i + 1]
            
            current_count = funnel.get(current_stage, 0)
            next_count = funnel.get(next_stage, 0)
            
            if current_count > 0:
                conversion_rate = (next_count / current_count) * 100
                conversion_rates[f"{current_stage}_to_{next_stage}"] = round(conversion_rate, 2)
        
        return conversion_rates
    
    def _identify_funnel_bottlenecks(self, deal_analytics: Dict) -> List[str]:
        """Identify bottlenecks in the sales funnel"""
        
        conversion_rates = self._calculate_conversion_rates(deal_analytics)
        bottlenecks = []
        
        for stage_conversion, rate in conversion_rates.items():
            if rate < 30:  # Less than 30% conversion is considered a bottleneck
                stage = stage_conversion.split("_to_")[0]
                bottlenecks.append(f"Low conversion from {stage.replace('_', ' ')} ({rate}%)")
        
        return bottlenecks
    
    def _apply_customizations(self, report_data: Dict, customizations: Dict) -> Dict[str, Any]:
        """Apply user customizations to the report data"""
        
        if not customizations:
            return report_data
        
        # Apply section filters
        if "sections" in customizations:
            filtered_sections = {}
            for section_id in customizations["sections"]:
                if section_id in report_data["sections"]:
                    filtered_sections[section_id] = report_data["sections"][section_id]
            report_data["sections"] = filtered_sections
        
        # Apply chart filters
        if "charts" in customizations:
            filtered_charts = {}
            for chart_id in customizations["charts"]:
                if chart_id in report_data["charts"]:
                    filtered_charts[chart_id] = report_data["charts"][chart_id]
            report_data["charts"] = filtered_charts
        
        # Apply custom title
        if "title" in customizations:
            report_data["custom_title"] = customizations["title"]
        
        # Apply custom branding
        if "branding" in customizations:
            report_data["branding"] = customizations["branding"]
        
        return report_data
    
    async def _generate_pdf_report(self, report_data: Dict, template: Dict) -> bytes:
        """Generate PDF report from report data"""
        
        # Convert report data to format expected by export service
        model_data = {
            "name": report_data.get("custom_title", template["name"]),
            "created_at": datetime.now().strftime('%Y-%m-%d'),
            "updated_at": datetime.now().strftime('%Y-%m-%d'),
            "model_type": "Custom Report",
            "key_metrics": self._extract_key_metrics(report_data),
            "projections": {"sections": report_data["sections"]},
            "assumptions": {"template": template["name"], "charts": list(report_data["charts"].keys())}
        }
        
        return await export_service.export_financial_model_to_pdf(
            model_data=model_data,
            model_id=uuid4(),
            organization_name="DealVerse Organization"
        )
    
    async def _generate_excel_report(self, report_data: Dict, template: Dict) -> bytes:
        """Generate Excel report from report data"""
        
        # Convert report data to format expected by export service
        model_data = {
            "name": report_data.get("custom_title", template["name"]),
            "created_at": datetime.now().strftime('%Y-%m-%d'),
            "updated_at": datetime.now().strftime('%Y-%m-%d'),
            "model_type": "Custom Report",
            "key_metrics": self._extract_key_metrics(report_data),
            "projections": {"sections": report_data["sections"]},
            "assumptions": {"template": template["name"], "charts": list(report_data["charts"].keys())}
        }
        
        return await export_service.export_financial_model_to_excel(
            model_data=model_data,
            model_id=uuid4(),
            organization_name="DealVerse Organization"
        )
    
    def _extract_key_metrics(self, report_data: Dict) -> Dict[str, Any]:
        """Extract key metrics from report data for export"""
        
        metrics = {}
        
        # Extract metrics from overview section
        if "overview_metrics" in report_data["sections"]:
            overview = report_data["sections"]["overview_metrics"]
            metrics.update(overview.get("metrics", {}))
        
        # Extract performance score
        if "summary" in report_data:
            summary = report_data["summary"]
            metrics["performance_score"] = summary.get("performance_score", 0)
            metrics["overall_rating"] = summary.get("overall_performance", "average")
        
        return metrics
    
    def get_available_templates(self) -> Dict[str, Dict]:
        """Get all available report templates"""
        return self.report_templates
    
    def get_template_details(self, template_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific template"""
        if template_id not in self.report_templates:
            raise ValueError(f"Unknown template: {template_id}")
        
        return self.report_templates[template_id]


# Create global instance
custom_reports_service = CustomReportsService()
