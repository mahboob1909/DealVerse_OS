#!/usr/bin/env python3
"""
Advanced Analytics Service for DealVerse OS
Provides business intelligence features with advanced metrics and insights
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc

from app.crud.crud_deal import crud_deal
from app.crud.crud_client import crud_client
from app.crud.crud_user import crud_user
from app.crud.crud_financial_model import crud_financial_model
from app.crud.crud_presentation import crud_presentation
from app.crud.crud_document import crud_document
from app.models.deal import Deal
from app.models.client import Client
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class AdvancedAnalyticsService:
    """Service for advanced analytics and business intelligence"""
    
    def __init__(self):
        self.cache_duration = 300  # 5 minutes cache
        self._cache = {}
    
    def get_comprehensive_dashboard_analytics(
        self, 
        db: Session, 
        organization_id: UUID,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard analytics with advanced metrics"""
        
        if not date_range:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)  # Last 90 days
            date_range = (start_date, end_date)
        
        start_date, end_date = date_range
        
        # Get core metrics
        deal_analytics = self._get_deal_analytics(db, organization_id, start_date, end_date)
        client_analytics = self._get_client_analytics(db, organization_id, start_date, end_date)
        team_analytics = self._get_team_analytics(db, organization_id, start_date, end_date)
        financial_analytics = self._get_financial_analytics(db, organization_id, start_date, end_date)
        
        # Calculate advanced KPIs
        advanced_kpis = self._calculate_advanced_kpis(
            deal_analytics, client_analytics, team_analytics, financial_analytics
        )
        
        # Get trend analysis
        trends = self._get_trend_analysis(db, organization_id, start_date, end_date)
        
        # Get predictive insights
        predictions = self._get_predictive_insights(db, organization_id, deal_analytics, trends)
        
        # Get performance benchmarks
        benchmarks = self._get_performance_benchmarks(db, organization_id, deal_analytics)
        
        return {
            "overview": {
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "organization_id": str(organization_id),
                "generated_at": datetime.utcnow().isoformat()
            },
            "kpis": advanced_kpis,
            "deal_analytics": deal_analytics,
            "client_analytics": client_analytics,
            "team_analytics": team_analytics,
            "financial_analytics": financial_analytics,
            "trends": trends,
            "predictions": predictions,
            "benchmarks": benchmarks
        }
    
    def _get_deal_analytics(
        self,
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get comprehensive deal analytics"""

        # Basic deal metrics using organization stats
        org_stats = crud_deal.get_organization_stats(db, organization_id=organization_id)
        total_deals = org_stats.get('total_deals', 0)
        active_deals = org_stats.get('active_deals', 0)
        
        # Deals in date range
        deals_in_range = db.query(Deal).filter(
            Deal.organization_id == organization_id,
            Deal.created_at >= start_date,
            Deal.created_at <= end_date
        ).all()
        
        # Deal stage analysis
        stage_distribution = {}
        total_value_by_stage = {}
        
        for deal in deals_in_range:
            stage = deal.stage or "Unknown"
            stage_distribution[stage] = stage_distribution.get(stage, 0) + 1
            total_value_by_stage[stage] = total_value_by_stage.get(stage, 0) + (deal.deal_value or 0)
        
        # Win rate calculation
        closed_won = len([d for d in deals_in_range if d.stage == "closed_won"])
        closed_lost = len([d for d in deals_in_range if d.stage == "closed_lost"])
        total_closed = closed_won + closed_lost
        win_rate = (closed_won / total_closed * 100) if total_closed > 0 else 0
        
        # Average deal size
        deal_values = [d.deal_value for d in deals_in_range if d.deal_value]
        avg_deal_size = sum(deal_values) / len(deal_values) if deal_values else 0
        
        # Deal velocity (average time to close)
        closed_deals = [d for d in deals_in_range if d.stage in ["closed_won", "closed_lost"]]
        deal_durations = []
        for deal in closed_deals:
            if deal.created_at and deal.updated_at:
                duration = (deal.updated_at - deal.created_at).days
                deal_durations.append(duration)
        
        avg_deal_duration = sum(deal_durations) / len(deal_durations) if deal_durations else 0
        
        return {
            "total_deals": total_deals,
            "active_deals": active_deals,
            "deals_in_period": len(deals_in_range),
            "stage_distribution": stage_distribution,
            "value_by_stage": total_value_by_stage,
            "win_rate": round(win_rate, 2),
            "average_deal_size": round(avg_deal_size, 2),
            "average_deal_duration_days": round(avg_deal_duration, 1),
            "total_pipeline_value": sum(total_value_by_stage.values()),
            "conversion_funnel": self._calculate_conversion_funnel(deals_in_range)
        }
    
    def _get_client_analytics(
        self,
        db: Session,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get comprehensive client analytics"""

        # Get client stats using organization stats method
        client_stats = crud_client.get_organization_stats(db, organization_id=organization_id)
        total_clients = client_stats.get('total_clients', 0)
        
        # Client acquisition in date range
        new_clients = db.query(Client).filter(
            Client.organization_id == organization_id,
            Client.created_at >= start_date,
            Client.created_at <= end_date
        ).count()
        
        # Client segmentation
        clients = crud_client.get_by_organization(db, organization_id=organization_id, limit=1000)
        
        industry_distribution = {}
        size_distribution = {}
        
        for client in clients:
            industry = client.industry or "Unknown"
            industry_distribution[industry] = industry_distribution.get(industry, 0) + 1
            
            size = client.company_size or "Unknown"
            size_distribution[size] = size_distribution.get(size, 0) + 1
        
        # Client lifetime value estimation
        client_deals = {}
        for client in clients:
            client_deals[client.id] = crud_deal.get_by_client(db, client.id)
        
        client_values = []
        for client_id, deals in client_deals.items():
            total_value = sum(deal.deal_value or 0 for deal in deals)
            if total_value > 0:
                client_values.append(total_value)
        
        avg_client_value = sum(client_values) / len(client_values) if client_values else 0
        
        return {
            "total_clients": total_clients,
            "new_clients_in_period": new_clients,
            "industry_distribution": industry_distribution,
            "size_distribution": size_distribution,
            "average_client_value": round(avg_client_value, 2),
            "client_acquisition_rate": round(new_clients / 90 * 30, 2),  # Monthly rate
            "top_industries": sorted(industry_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _get_team_analytics(
        self, 
        db: Session, 
        organization_id: UUID, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get team performance analytics"""
        
        team_members = crud_user.get_by_organization(db, organization_id=organization_id, limit=1000)
        
        # User activity analysis
        user_performance = {}
        for user in team_members:
            user_deals = crud_deal.get_by_user(db, user.id)
            deals_in_period = [d for d in user_deals if start_date <= d.created_at <= end_date]
            
            user_performance[str(user.id)] = {
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "total_deals": len(user_deals),
                "deals_in_period": len(deals_in_period),
                "total_deal_value": sum(d.deal_value or 0 for d in deals_in_period),
                "avg_deal_size": 0,
                "win_rate": 0
            }
            
            if deals_in_period:
                user_performance[str(user.id)]["avg_deal_size"] = (
                    user_performance[str(user.id)]["total_deal_value"] / len(deals_in_period)
                )
                
                won_deals = [d for d in deals_in_period if d.stage == "closed_won"]
                closed_deals = [d for d in deals_in_period if d.stage in ["closed_won", "closed_lost"]]
                
                if closed_deals:
                    user_performance[str(user.id)]["win_rate"] = len(won_deals) / len(closed_deals) * 100
        
        # Team productivity metrics
        total_team_deals = sum(p["deals_in_period"] for p in user_performance.values())
        avg_deals_per_user = total_team_deals / len(team_members) if team_members else 0
        
        return {
            "total_team_members": len(team_members),
            "user_performance": user_performance,
            "team_productivity": {
                "total_deals_in_period": total_team_deals,
                "average_deals_per_user": round(avg_deals_per_user, 2),
                "top_performers": self._get_top_performers(user_performance)
            }
        }
    
    def _get_financial_analytics(
        self, 
        db: Session, 
        organization_id: UUID, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get financial analytics from models and deals"""
        
        # Financial models analysis
        models = crud_financial_model.get_by_organization(db, organization_id=organization_id, limit=1000)
        models_in_period = [m for m in models if start_date <= m.created_at <= end_date]
        
        # Revenue projections from models
        total_projected_revenue = 0
        model_types = {}
        
        for model in models_in_period:
            if model.projections and isinstance(model.projections, dict):
                years = model.projections.get("years", [])
                for year_data in years:
                    total_projected_revenue += year_data.get("revenue", 0)
            
            model_type = model.model_type or "Unknown"
            model_types[model_type] = model_types.get(model_type, 0) + 1
        
        # Deal value analysis
        deals = crud_deal.get_by_organization(db, organization_id=organization_id, limit=1000)
        deals_in_period = [d for d in deals if start_date <= d.created_at <= end_date]
        
        total_deal_value = sum(d.deal_value or 0 for d in deals_in_period)
        won_deal_value = sum(d.deal_value or 0 for d in deals_in_period if d.stage == "closed_won")
        
        return {
            "financial_models": {
                "total_models": len(models),
                "models_in_period": len(models_in_period),
                "model_types": model_types,
                "projected_revenue": round(total_projected_revenue, 2)
            },
            "deal_financials": {
                "total_pipeline_value": round(total_deal_value, 2),
                "realized_revenue": round(won_deal_value, 2),
                "revenue_conversion_rate": round(won_deal_value / total_deal_value * 100, 2) if total_deal_value > 0 else 0
            }
        }
    
    def _calculate_advanced_kpis(
        self, 
        deal_analytics: Dict, 
        client_analytics: Dict, 
        team_analytics: Dict, 
        financial_analytics: Dict
    ) -> Dict[str, Any]:
        """Calculate advanced KPIs and business intelligence metrics"""
        
        return {
            "revenue_efficiency": {
                "revenue_per_deal": deal_analytics.get("average_deal_size", 0),
                "revenue_per_client": client_analytics.get("average_client_value", 0),
                "revenue_per_team_member": (
                    financial_analytics["deal_financials"]["realized_revenue"] / 
                    team_analytics["total_team_members"]
                ) if team_analytics["total_team_members"] > 0 else 0
            },
            "growth_metrics": {
                "deal_velocity": deal_analytics.get("average_deal_duration_days", 0),
                "client_acquisition_rate": client_analytics.get("client_acquisition_rate", 0),
                "pipeline_growth_rate": 0,  # Would need historical data
                "win_rate_trend": deal_analytics.get("win_rate", 0)
            },
            "operational_efficiency": {
                "deals_per_team_member": team_analytics["team_productivity"]["average_deals_per_user"],
                "conversion_rate": deal_analytics.get("win_rate", 0),
                "pipeline_coverage": (
                    deal_analytics.get("total_pipeline_value", 0) / 
                    financial_analytics["deal_financials"]["realized_revenue"]
                ) if financial_analytics["deal_financials"]["realized_revenue"] > 0 else 0
            }
        }
    
    def _calculate_conversion_funnel(self, deals: List[Deal]) -> Dict[str, Any]:
        """Calculate conversion funnel metrics"""
        
        stage_order = ["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"]
        funnel = {}
        
        for stage in stage_order:
            funnel[stage] = len([d for d in deals if d.stage == stage])
        
        return funnel
    
    def _get_top_performers(self, user_performance: Dict) -> List[Dict]:
        """Get top performing team members"""
        
        performers = []
        for user_id, performance in user_performance.items():
            performers.append({
                "user_id": user_id,
                "name": performance["name"],
                "deals_count": performance["deals_in_period"],
                "total_value": performance["total_deal_value"],
                "win_rate": performance["win_rate"]
            })
        
        # Sort by total deal value
        performers.sort(key=lambda x: x["total_value"], reverse=True)
        return performers[:5]
    
    def _get_trend_analysis(
        self, 
        db: Session, 
        organization_id: UUID, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get trend analysis over time"""
        
        # Weekly trends
        weekly_trends = []
        current_date = start_date
        
        while current_date < end_date:
            week_end = min(current_date + timedelta(days=7), end_date)
            
            week_deals = db.query(Deal).filter(
                Deal.organization_id == organization_id,
                Deal.created_at >= current_date,
                Deal.created_at < week_end
            ).all()
            
            weekly_trends.append({
                "week_start": current_date.isoformat(),
                "week_end": week_end.isoformat(),
                "deals_created": len(week_deals),
                "total_value": sum(d.deal_value or 0 for d in week_deals),
                "won_deals": len([d for d in week_deals if d.stage == "closed_won"])
            })
            
            current_date = week_end
        
        return {
            "weekly_trends": weekly_trends,
            "trend_summary": {
                "total_weeks": len(weekly_trends),
                "avg_deals_per_week": sum(w["deals_created"] for w in weekly_trends) / len(weekly_trends) if weekly_trends else 0,
                "avg_value_per_week": sum(w["total_value"] for w in weekly_trends) / len(weekly_trends) if weekly_trends else 0
            }
        }
    
    def _get_predictive_insights(
        self, 
        db: Session, 
        organization_id: UUID, 
        deal_analytics: Dict, 
        trends: Dict
    ) -> Dict[str, Any]:
        """Generate predictive insights based on historical data"""
        
        # Simple trend-based predictions
        weekly_trends = trends.get("weekly_trends", [])
        
        if len(weekly_trends) >= 4:  # Need at least 4 weeks of data
            recent_weeks = weekly_trends[-4:]
            
            # Calculate growth rates
            deals_growth = self._calculate_growth_rate([w["deals_created"] for w in recent_weeks])
            value_growth = self._calculate_growth_rate([w["total_value"] for w in recent_weeks])
            
            # Project next month
            current_avg_deals = sum(w["deals_created"] for w in recent_weeks) / len(recent_weeks)
            current_avg_value = sum(w["total_value"] for w in recent_weeks) / len(recent_weeks)
            
            projected_deals = current_avg_deals * (1 + deals_growth) * 4  # 4 weeks
            projected_value = current_avg_value * (1 + value_growth) * 4
            
            return {
                "next_month_projection": {
                    "projected_deals": round(projected_deals, 0),
                    "projected_value": round(projected_value, 2),
                    "confidence": "medium",  # Simple confidence level
                    "growth_rate_deals": round(deals_growth * 100, 2),
                    "growth_rate_value": round(value_growth * 100, 2)
                },
                "recommendations": self._generate_recommendations(deal_analytics, trends)
            }
        
        return {
            "next_month_projection": {
                "message": "Insufficient data for predictions",
                "confidence": "low"
            },
            "recommendations": []
        }
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate simple growth rate from a list of values"""
        if len(values) < 2:
            return 0
        
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if first_half == 0:
            return 0
        
        return (second_half - first_half) / first_half
    
    def _generate_recommendations(self, deal_analytics: Dict, trends: Dict) -> List[str]:
        """Generate actionable recommendations based on analytics"""
        
        recommendations = []
        
        # Win rate recommendations
        win_rate = deal_analytics.get("win_rate", 0)
        if win_rate < 20:
            recommendations.append("Consider improving qualification process - win rate is below industry average")
        elif win_rate > 60:
            recommendations.append("Excellent win rate! Consider increasing deal volume to maximize revenue")
        
        # Deal duration recommendations
        avg_duration = deal_analytics.get("average_deal_duration_days", 0)
        if avg_duration > 90:
            recommendations.append("Deal cycles are lengthy - consider streamlining the sales process")
        
        # Pipeline recommendations
        pipeline_value = deal_analytics.get("total_pipeline_value", 0)
        if pipeline_value < 100000:
            recommendations.append("Pipeline value is low - focus on prospecting and lead generation")
        
        return recommendations
    
    def _get_performance_benchmarks(
        self, 
        db: Session, 
        organization_id: UUID, 
        deal_analytics: Dict
    ) -> Dict[str, Any]:
        """Get performance benchmarks and industry comparisons"""
        
        # Industry benchmarks (simplified - in production, these would come from external data)
        industry_benchmarks = {
            "win_rate": {"excellent": 60, "good": 40, "average": 25, "poor": 15},
            "deal_duration_days": {"excellent": 30, "good": 60, "average": 90, "poor": 120},
            "average_deal_size": {"excellent": 100000, "good": 50000, "average": 25000, "poor": 10000}
        }
        
        # Compare current performance to benchmarks
        current_performance = {
            "win_rate": deal_analytics.get("win_rate", 0),
            "deal_duration_days": deal_analytics.get("average_deal_duration_days", 0),
            "average_deal_size": deal_analytics.get("average_deal_size", 0)
        }
        
        performance_ratings = {}
        for metric, value in current_performance.items():
            benchmarks = industry_benchmarks.get(metric, {})
            
            if value >= benchmarks.get("excellent", 0):
                rating = "excellent"
            elif value >= benchmarks.get("good", 0):
                rating = "good"
            elif value >= benchmarks.get("average", 0):
                rating = "average"
            else:
                rating = "poor"
            
            performance_ratings[metric] = {
                "current_value": value,
                "rating": rating,
                "benchmarks": benchmarks
            }
        
        return {
            "performance_ratings": performance_ratings,
            "overall_score": self._calculate_overall_score(performance_ratings)
        }
    
    def _calculate_overall_score(self, performance_ratings: Dict) -> Dict[str, Any]:
        """Calculate overall performance score"""
        
        rating_scores = {"excellent": 4, "good": 3, "average": 2, "poor": 1}
        
        total_score = 0
        max_score = 0
        
        for metric, data in performance_ratings.items():
            rating = data["rating"]
            score = rating_scores.get(rating, 1)
            total_score += score
            max_score += 4
        
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        if percentage >= 80:
            overall_rating = "excellent"
        elif percentage >= 60:
            overall_rating = "good"
        elif percentage >= 40:
            overall_rating = "average"
        else:
            overall_rating = "needs_improvement"
        
        return {
            "score": round(percentage, 1),
            "rating": overall_rating,
            "total_metrics": len(performance_ratings)
        }


# Create global instance
advanced_analytics_service = AdvancedAnalyticsService()
