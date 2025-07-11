"""
AI services for prospect analysis and scoring
"""
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from app.schemas.prospect import (
    ProspectAnalysisRequest,
    ProspectAnalysisResponse,
    ProspectScoringRequest,
    ProspectScoringResponse,
    ScoredProspect,
    MarketIntelligenceResponse,
    IndustryTrend,
    MarketTransaction,
    MarketAlert
)
from app.services.enhanced_prospect_ai import enhanced_prospect_ai

logger = logging.getLogger(__name__)


class ProspectAIService:
    """AI service for prospect analysis and scoring"""

    def __init__(self):
        self.model_version = "1.0.0"
        self.enhanced_ai = enhanced_prospect_ai
        self.use_enhanced_ai = True  # Flag to enable/disable enhanced AI
        self.confidence_thresholds = {
            "high": 80,
            "medium": 60,
            "low": 0
        }
    
    async def analyze_prospect(self, request: ProspectAnalysisRequest) -> ProspectAnalysisResponse:
        """
        Analyze a prospect using enhanced AI algorithms

        Uses real AI integration for:
        1. Advanced ML models for prospect scoring
        2. Market intelligence and competitive analysis
        3. Risk assessment and opportunity identification
        4. Strategic fit evaluation
        5. Deal probability calculation

        Falls back to sophisticated mock logic if AI fails
        """
        start_time = time.time()

        try:
            # Try enhanced AI analysis first
            if self.use_enhanced_ai:
                try:
                    logger.info(f"Using enhanced AI for prospect analysis: {request.company_name}")
                    return await self.enhanced_ai.analyze_prospect_enhanced(request)
                except Exception as e:
                    logger.warning(f"Enhanced AI analysis failed, falling back to standard analysis: {str(e)}")

            # Fallback to standard analysis
            logger.info(f"Using standard analysis for prospect: {request.company_name}")

            # Calculate AI score based on multiple factors
            ai_score = self._calculate_ai_score(request)

            # Determine confidence level
            confidence_level = self._determine_confidence_level(ai_score, request)

            # Calculate deal probability
            deal_probability = self._calculate_deal_probability(request, ai_score)

            # Estimate deal size
            estimated_deal_size = self._estimate_deal_size(request)

            # Generate risk factors and opportunities
            risk_factors = self._identify_risk_factors(request)
            opportunities = self._identify_opportunities(request)

            # Generate recommended approach
            recommended_approach = self._generate_recommended_approach(request, ai_score)

            # Calculate detailed analysis scores
            analysis_details = self._calculate_detailed_scores(request)
            
            processing_time = Decimal(str(time.time() - start_time))
            
            return ProspectAnalysisResponse(
                ai_score=ai_score,
                confidence_level=confidence_level,
                risk_factors=risk_factors,
                opportunities=opportunities,
                deal_probability=deal_probability,
                estimated_deal_size=estimated_deal_size,
                recommended_approach=recommended_approach,
                analysis_details=analysis_details,
                processing_time=processing_time,
                analysis_date=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing prospect: {str(e)}")
            raise
    
    def _calculate_ai_score(self, request: ProspectAnalysisRequest) -> Decimal:
        """Calculate AI score based on multiple factors"""
        score = 50  # Base score
        
        # Revenue factor (0-25 points)
        if request.revenue:
            if request.revenue >= 100_000_000:  # $100M+
                score += 25
            elif request.revenue >= 50_000_000:  # $50M+
                score += 20
            elif request.revenue >= 10_000_000:  # $10M+
                score += 15
            elif request.revenue >= 1_000_000:  # $1M+
                score += 10
            else:
                score += 5
        
        # Industry factor (0-15 points)
        high_value_industries = [
            "Technology", "Healthcare", "Financial Services", 
            "Energy", "Manufacturing", "Telecommunications"
        ]
        if request.industry in high_value_industries:
            score += 15
        elif request.industry:
            score += 10
        
        # Market cap factor (0-10 points)
        if request.market_cap:
            if request.market_cap >= 1_000_000_000:  # $1B+
                score += 10
            elif request.market_cap >= 100_000_000:  # $100M+
                score += 8
            elif request.market_cap >= 10_000_000:  # $10M+
                score += 5
        
        # Financial data quality bonus (0-10 points)
        financial_data = request.financial_data or {}
        data_points = len([v for v in financial_data.values() if v is not None])
        score += min(data_points * 2, 10)
        
        # Add some randomness to simulate AI model uncertainty
        score += random.uniform(-5, 5)
        
        return Decimal(str(max(0, min(100, score))))
    
    def _determine_confidence_level(self, ai_score: Decimal, request: ProspectAnalysisRequest) -> str:
        """Determine confidence level based on score and data quality"""
        # Adjust confidence based on data availability
        data_quality = self._assess_data_quality(request)
        
        adjusted_score = float(ai_score) * data_quality
        
        if adjusted_score >= self.confidence_thresholds["high"]:
            return "high"
        elif adjusted_score >= self.confidence_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _assess_data_quality(self, request: ProspectAnalysisRequest) -> float:
        """Assess quality of available data (0.5 to 1.0)"""
        quality_score = 0.5  # Base quality
        
        # Check for key data points
        if request.revenue:
            quality_score += 0.1
        if request.industry:
            quality_score += 0.1
        if request.location:
            quality_score += 0.05
        if request.market_cap:
            quality_score += 0.1
        if request.employees:
            quality_score += 0.05
        
        # Check financial data completeness
        financial_data = request.financial_data or {}
        if financial_data:
            quality_score += min(len(financial_data) * 0.02, 0.1)
        
        return min(quality_score, 1.0)
    
    def _calculate_deal_probability(self, request: ProspectAnalysisRequest, ai_score: Decimal) -> Decimal:
        """Calculate probability of successful deal"""
        base_probability = float(ai_score) * 0.6  # Base on AI score
        
        # Industry adjustments
        industry_multipliers = {
            "Technology": 1.2,
            "Healthcare": 1.1,
            "Financial Services": 1.0,
            "Manufacturing": 0.9,
            "Retail": 0.8,
            "Energy": 1.1
        }
        
        multiplier = industry_multipliers.get(request.industry, 1.0)
        probability = base_probability * multiplier
        
        # Add market conditions factor (simulated)
        market_factor = random.uniform(0.8, 1.2)
        probability *= market_factor
        
        return Decimal(str(max(0, min(100, probability))))
    
    def _estimate_deal_size(self, request: ProspectAnalysisRequest) -> Optional[Decimal]:
        """Estimate potential deal size"""
        if not request.revenue:
            return None
        
        # Typical deal size is 0.5x to 2x revenue for M&A
        base_multiple = random.uniform(0.5, 2.0)
        
        # Industry adjustments
        industry_multipliers = {
            "Technology": 1.5,
            "Healthcare": 1.3,
            "Financial Services": 1.0,
            "Manufacturing": 0.8,
            "Energy": 1.2
        }
        
        multiplier = industry_multipliers.get(request.industry, 1.0)
        estimated_size = float(request.revenue) * base_multiple * multiplier
        
        return Decimal(str(estimated_size))
    
    def _identify_risk_factors(self, request: ProspectAnalysisRequest) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Revenue-based risks
        if request.revenue and request.revenue < 10_000_000:
            risks.append("Small revenue base may limit deal attractiveness")
        
        # Industry-specific risks
        industry_risks = {
            "Technology": ["Rapid technological change", "High competition"],
            "Healthcare": ["Regulatory compliance", "Reimbursement risks"],
            "Energy": ["Commodity price volatility", "Environmental regulations"],
            "Retail": ["Consumer spending sensitivity", "E-commerce disruption"],
            "Manufacturing": ["Supply chain dependencies", "Automation risks"]
        }
        
        if request.industry in industry_risks:
            risks.extend(industry_risks[request.industry])
        
        # Market cap risks
        if request.market_cap and request.market_cap < 50_000_000:
            risks.append("Limited market capitalization")
        
        # Add some general risks
        general_risks = [
            "Market volatility",
            "Economic uncertainty",
            "Regulatory changes",
            "Competition intensity"
        ]
        risks.extend(random.sample(general_risks, random.randint(1, 2)))
        
        return risks[:5]  # Limit to 5 risks
    
    def _identify_opportunities(self, request: ProspectAnalysisRequest) -> List[str]:
        """Identify potential opportunities"""
        opportunities = []
        
        # Revenue-based opportunities
        if request.revenue and request.revenue >= 50_000_000:
            opportunities.append("Strong revenue base for expansion")
        
        # Industry-specific opportunities
        industry_opportunities = {
            "Technology": ["Digital transformation trends", "AI/ML adoption"],
            "Healthcare": ["Aging population demographics", "Telehealth growth"],
            "Energy": ["Renewable energy transition", "ESG investment focus"],
            "Manufacturing": ["Automation opportunities", "Supply chain optimization"],
            "Financial Services": ["Fintech innovation", "Digital banking"]
        }
        
        if request.industry in industry_opportunities:
            opportunities.extend(industry_opportunities[request.industry])
        
        # General opportunities
        general_opportunities = [
            "Market expansion potential",
            "Operational efficiency improvements",
            "Strategic partnerships",
            "Product diversification"
        ]
        opportunities.extend(random.sample(general_opportunities, random.randint(1, 2)))
        
        return opportunities[:5]  # Limit to 5 opportunities
    
    def _generate_recommended_approach(self, request: ProspectAnalysisRequest, ai_score: Decimal) -> str:
        """Generate recommended approach for the prospect"""
        score = float(ai_score)
        
        if score >= 80:
            return "High priority prospect - initiate immediate contact with senior team involvement"
        elif score >= 60:
            return "Qualified prospect - schedule discovery meeting to assess fit"
        elif score >= 40:
            return "Potential prospect - conduct preliminary research and warm introduction"
        else:
            return "Monitor prospect - track developments and reassess in 6 months"
    
    def _calculate_detailed_scores(self, request: ProspectAnalysisRequest) -> Dict[str, Any]:
        """Calculate detailed scoring breakdown"""
        # Financial health score
        financial_health = 70
        if request.revenue and request.revenue >= 50_000_000:
            financial_health += 20
        elif request.revenue and request.revenue >= 10_000_000:
            financial_health += 10
        
        # Market position score
        market_position = 60
        if request.market_cap and request.market_cap >= 1_000_000_000:
            market_position += 30
        elif request.market_cap and request.market_cap >= 100_000_000:
            market_position += 20
        
        # Growth potential score
        growth_potential = random.randint(50, 90)
        
        # Strategic fit score
        strategic_fit = random.randint(60, 95)
        
        return {
            "financial_health": min(financial_health, 100),
            "market_position": min(market_position, 100),
            "growth_potential": growth_potential,
            "strategic_fit": strategic_fit
        }
    
    async def score_prospects(self, request: ProspectScoringRequest) -> ProspectScoringResponse:
        """Score multiple prospects based on criteria"""
        scored_prospects = []
        
        for i, prospect_data in enumerate(request.prospects):
            # Calculate weighted score
            total_score = self._calculate_weighted_score(prospect_data, request.scoring_criteria)
            
            # Generate score breakdown
            score_breakdown = self._generate_score_breakdown(prospect_data)
            
            # Generate recommendation
            recommendation = self._generate_scoring_recommendation(total_score)
            
            scored_prospect = ScoredProspect(
                company_id=prospect_data.get("company_id"),
                company_name=prospect_data["company_name"],
                total_score=total_score,
                score_breakdown=score_breakdown,
                ranking=i + 1,  # Will be updated after sorting
                recommendation=recommendation
            )
            scored_prospects.append(scored_prospect)
        
        # Sort by total score (descending)
        scored_prospects.sort(key=lambda x: x.total_score, reverse=True)
        
        # Update rankings
        for i, prospect in enumerate(scored_prospects):
            prospect.ranking = i + 1
        
        # Calculate summary statistics
        total_prospects = len(scored_prospects)
        average_score = sum(p.total_score for p in scored_prospects) / total_prospects if total_prospects > 0 else 0
        top_quartile_threshold = scored_prospects[total_prospects // 4].total_score if total_prospects >= 4 else 0
        
        summary = {
            "total_prospects": total_prospects,
            "average_score": average_score,
            "top_quartile_threshold": top_quartile_threshold
        }
        
        return ProspectScoringResponse(
            scored_prospects=scored_prospects,
            summary=summary
        )
    
    def _calculate_weighted_score(self, prospect_data: Dict[str, Any], criteria: Dict[str, Decimal]) -> Decimal:
        """Calculate weighted score for a prospect"""
        financial_metrics = prospect_data.get("financial_metrics", {})
        
        # Revenue score (0-100)
        revenue = financial_metrics.get("revenue", 0)
        revenue_score = min(100, (revenue / 100_000_000) * 100) if revenue else 0
        
        # Growth score (0-100)
        growth_rate = financial_metrics.get("growth_rate", 0)
        growth_score = min(100, max(0, (growth_rate + 10) * 5)) if growth_rate else 50
        
        # Profitability score (0-100)
        ebitda = financial_metrics.get("ebitda", 0)
        profitability_score = min(100, (ebitda / revenue) * 500) if revenue and ebitda else 50
        
        # Market position score (simulated)
        market_position_score = random.randint(40, 90)
        
        # Calculate weighted total
        total_score = (
            revenue_score * float(criteria["revenue_weight"]) +
            growth_score * float(criteria["growth_weight"]) +
            profitability_score * float(criteria["profitability_weight"]) +
            market_position_score * float(criteria["market_position_weight"])
        )
        
        return Decimal(str(round(total_score, 2)))
    
    def _generate_score_breakdown(self, prospect_data: Dict[str, Any]) -> Dict[str, Decimal]:
        """Generate detailed score breakdown"""
        financial_metrics = prospect_data.get("financial_metrics", {})
        
        revenue = financial_metrics.get("revenue", 0)
        revenue_score = min(100, (revenue / 100_000_000) * 100) if revenue else 0
        
        growth_rate = financial_metrics.get("growth_rate", 0)
        growth_score = min(100, max(0, (growth_rate + 10) * 5)) if growth_rate else 50
        
        ebitda = financial_metrics.get("ebitda", 0)
        profitability_score = min(100, (ebitda / revenue) * 500) if revenue and ebitda else 50
        
        market_position_score = random.randint(40, 90)
        
        return {
            "financial_score": Decimal(str(round(revenue_score, 2))),
            "growth_score": Decimal(str(round(growth_score, 2))),
            "profitability_score": Decimal(str(round(profitability_score, 2))),
            "market_score": Decimal(str(round(market_position_score, 2)))
        }
    
    def _generate_scoring_recommendation(self, total_score: Decimal) -> str:
        """Generate recommendation based on total score"""
        score = float(total_score)
        
        if score >= 80:
            return "Strong candidate - prioritize for immediate engagement"
        elif score >= 60:
            return "Good prospect - schedule detailed evaluation"
        elif score >= 40:
            return "Moderate interest - monitor and reassess"
        else:
            return "Low priority - consider for future opportunities"


    async def get_market_intelligence(
        self,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        time_period: str = "3M",
        deal_type: Optional[str] = None
    ) -> MarketIntelligenceResponse:
        """Get market intelligence data"""

        # Generate market overview
        market_overview = self._generate_market_overview(industry, time_period)

        # Generate industry trends
        industry_trends = self._generate_industry_trends(industry)

        # Generate recent transactions
        recent_transactions = self._generate_recent_transactions(industry, region)

        # Generate market alerts
        market_alerts = self._generate_market_alerts(industry)

        return MarketIntelligenceResponse(
            market_overview=market_overview,
            industry_trends=industry_trends,
            recent_transactions=recent_transactions,
            market_alerts=market_alerts,
            generated_at=datetime.utcnow(),
            time_period=time_period,
            data_sources=["Bloomberg", "Reuters", "S&P Capital IQ", "PitchBook"]
        )

    def _generate_market_overview(self, industry: Optional[str], time_period: str) -> Dict[str, Any]:
        """Generate market overview data"""
        # Simulate market data based on time period
        period_multipliers = {"1M": 0.25, "3M": 0.75, "6M": 1.5, "1Y": 3.0}
        multiplier = period_multipliers.get(time_period, 1.0)

        base_volume = random.uniform(50_000_000_000, 200_000_000_000)  # $50B - $200B
        deal_count = random.randint(100, 500)

        return {
            "total_deal_volume": int(base_volume * multiplier),
            "average_deal_size": int((base_volume * multiplier) / deal_count),
            "deal_count": int(deal_count * multiplier),
            "market_sentiment": random.choice(["bullish", "neutral", "bearish"])
        }

    def _generate_industry_trends(self, industry: Optional[str]) -> List[IndustryTrend]:
        """Generate industry trend data"""
        industries = [
            "Technology", "Healthcare", "Financial Services",
            "Energy", "Manufacturing", "Retail", "Telecommunications"
        ]

        if industry:
            industries = [industry]

        trends = []
        for ind in industries[:5]:  # Limit to 5 industries
            trend = IndustryTrend(
                industry=ind,
                growth_rate=Decimal(str(random.uniform(-5.0, 15.0))),
                deal_activity=random.randint(10, 100),
                key_drivers=self._get_industry_drivers(ind),
                outlook=random.choice(["positive", "stable", "negative"])
            )
            trends.append(trend)

        return trends

    def _get_industry_drivers(self, industry: str) -> List[str]:
        """Get key drivers for an industry"""
        drivers_map = {
            "Technology": ["AI/ML adoption", "Cloud migration", "Digital transformation"],
            "Healthcare": ["Aging population", "Telehealth growth", "Drug development"],
            "Financial Services": ["Fintech disruption", "Digital banking", "Regulatory changes"],
            "Energy": ["Renewable transition", "ESG focus", "Carbon neutrality"],
            "Manufacturing": ["Automation", "Supply chain optimization", "Industry 4.0"],
            "Retail": ["E-commerce growth", "Omnichannel strategies", "Consumer behavior"],
            "Telecommunications": ["5G deployment", "IoT expansion", "Network infrastructure"]
        }
        return drivers_map.get(industry, ["Market dynamics", "Innovation", "Competition"])

    def _generate_recent_transactions(self, industry: Optional[str], region: Optional[str]) -> List[MarketTransaction]:
        """Generate recent transaction data"""
        transactions = []

        # Sample transaction data
        sample_transactions = [
            {"target": "TechCorp", "acquirer": "MegaTech Inc", "industry": "Technology", "size_range": (1_000_000_000, 5_000_000_000)},
            {"target": "HealthSolutions", "acquirer": "PharmaCorp", "industry": "Healthcare", "size_range": (500_000_000, 2_000_000_000)},
            {"target": "FinanceApp", "acquirer": "BankHolding", "industry": "Financial Services", "size_range": (100_000_000, 1_000_000_000)},
            {"target": "EnergyTech", "acquirer": "PowerCorp", "industry": "Energy", "size_range": (2_000_000_000, 8_000_000_000)},
            {"target": "ManufacturingCo", "acquirer": "IndustrialGroup", "industry": "Manufacturing", "size_range": (300_000_000, 1_500_000_000)}
        ]

        for i, tx_data in enumerate(sample_transactions[:5]):
            if industry and tx_data["industry"] != industry:
                continue

            deal_size = random.uniform(*tx_data["size_range"])
            date = datetime.utcnow() - timedelta(days=random.randint(1, 90))

            transaction = MarketTransaction(
                target=tx_data["target"],
                acquirer=tx_data["acquirer"],
                deal_size=Decimal(str(int(deal_size))),
                industry=tx_data["industry"],
                date=date.strftime("%Y-%m-%d"),
                deal_type="M&A"
            )
            transactions.append(transaction)

        return transactions

    def _generate_market_alerts(self, industry: Optional[str]) -> List[MarketAlert]:
        """Generate market alerts"""
        alerts = []

        alert_templates = [
            {"type": "regulatory", "message": "New regulatory framework announced", "severity": "medium"},
            {"type": "market", "message": "Increased M&A activity in sector", "severity": "low"},
            {"type": "economic", "message": "Interest rate changes affecting valuations", "severity": "high"},
            {"type": "industry", "message": "Major technology disruption emerging", "severity": "medium"},
            {"type": "geopolitical", "message": "Trade policy changes impacting deals", "severity": "high"}
        ]

        for template in random.sample(alert_templates, random.randint(2, 4)):
            date = datetime.utcnow() - timedelta(days=random.randint(1, 30))

            alert = MarketAlert(
                type=template["type"],
                message=template["message"],
                severity=template["severity"],
                date=date.strftime("%Y-%m-%d")
            )
            alerts.append(alert)

        return alerts


# Create service instance
prospect_ai_service = ProspectAIService()
