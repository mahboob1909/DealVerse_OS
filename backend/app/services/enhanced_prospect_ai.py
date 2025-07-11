"""
Enhanced Prospect AI Service for DealVerse OS
Real AI integration for prospect scoring, market analysis, and opportunity identification
"""
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import json

from app.services.real_ai_service import real_ai_service
from app.schemas.prospect import (
    ProspectAnalysisRequest,
    ProspectAnalysisResponse,
    ProspectScoringRequest,
    ProspectScoringResponse,
    ScoredProspect,
    MarketAlert,
    IndustryTrend
)
from app.core.ai_config import get_ai_settings

logger = logging.getLogger(__name__)


class EnhancedProspectAI:
    """
    Enhanced Prospect AI service with real AI integration
    for advanced prospect scoring and market analysis
    """
    
    def __init__(self):
        self.settings = get_ai_settings()
        self.real_ai = real_ai_service
        self.model_version = "Enhanced-ProspectAI-v1.0"

        # Check if enhanced AI is available
        self.enhanced_ai_available = bool(
            self.settings.openrouter_api_key or
            self.settings.openai_api_key or
            self.settings.anthropic_api_key
        )

        if self.enhanced_ai_available:
            logger.info(f"Enhanced Prospect AI initialized with {self.settings.preferred_ai_provider}")
        else:
            logger.warning("Enhanced Prospect AI initialized without real AI provider")
        
    async def analyze_prospect_enhanced(
        self,
        request: ProspectAnalysisRequest
    ) -> ProspectAnalysisResponse:
        """
        Enhanced prospect analysis using real AI
        """
        start_time = time.time()
        
        try:
            # Build comprehensive analysis context
            analysis_context = self._build_prospect_context(request)
            
            # Perform AI-powered analysis
            ai_results = await self._perform_ai_prospect_analysis(analysis_context)
            
            # Calculate enhanced scores and metrics
            enhanced_metrics = self._calculate_enhanced_metrics(ai_results, request)
            
            # Generate strategic recommendations
            recommendations = await self._generate_strategic_recommendations(
                ai_results, request, enhanced_metrics
            )
            
            # Calculate processing time
            processing_time = Decimal(str(time.time() - start_time))
            
            return ProspectAnalysisResponse(
                ai_score=enhanced_metrics["ai_score"],
                confidence_level=enhanced_metrics["confidence_level"],
                deal_probability=enhanced_metrics["deal_probability"],
                estimated_deal_size=enhanced_metrics["estimated_deal_size"],
                risk_factors=enhanced_metrics["risk_factors"],
                opportunities=enhanced_metrics["opportunities"],
                recommended_approach=recommendations["primary_approach"],
                analysis_details=enhanced_metrics["detailed_scores"],
                processing_time=processing_time,
                analysis_date=datetime.utcnow(),
                model_version=self.model_version
            )
            
        except Exception as e:
            logger.error(f"Enhanced prospect analysis failed: {str(e)}")
            # Fallback to basic analysis
            return await self._fallback_prospect_analysis(request, start_time)
    
    def _build_prospect_context(self, request: ProspectAnalysisRequest) -> Dict[str, Any]:
        """Build comprehensive context for AI analysis"""
        
        # Format financial data for AI analysis
        financial_summary = self._format_financial_data(request.financial_data or {})
        
        # Build company profile
        company_profile = f"""
        Company: {request.company_name}
        Industry: {request.industry or 'Not specified'}
        Location: {request.location or 'Not specified'}
        Revenue: ${request.revenue:,.2f} if request.revenue else 'Not disclosed'
        Employees: {request.employees or 'Not specified'}
        Market Cap: ${request.market_cap:,.2f} if request.market_cap else 'Not disclosed'
        
        Financial Data:
        {financial_summary}
        
        Analysis Type: {request.analysis_type}
        """
        
        return {
            "company_profile": company_profile.strip(),
            "analysis_type": request.analysis_type,
            "industry": request.industry,
            "revenue": float(request.revenue) if request.revenue else None,
            "market_cap": float(request.market_cap) if request.market_cap else None,
            "financial_data": request.financial_data or {},
            "criteria": request.criteria or {}
        }
    
    def _format_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """Format financial data for AI analysis"""
        if not financial_data:
            return "No financial data provided"
        
        formatted_lines = []
        for key, value in financial_data.items():
            if value is not None:
                formatted_lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted_lines) if formatted_lines else "No financial data provided"
    
    async def _perform_ai_prospect_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI-powered prospect analysis"""
        try:
            # Call AI service with prospect analysis prompt
            ai_response = await self.real_ai._call_ai_service(
                prompt_type="prospect_analysis",
                context=context
            )
            
            # Parse AI response
            parsed_results = self.real_ai._parse_ai_response(ai_response)
            
            return parsed_results
            
        except Exception as e:
            logger.warning(f"AI prospect analysis failed: {str(e)}")
            return self._get_fallback_ai_results(context)
    
    def _calculate_enhanced_metrics(
        self,
        ai_results: Dict[str, Any],
        request: ProspectAnalysisRequest
    ) -> Dict[str, Any]:
        """Calculate enhanced metrics from AI results"""
        
        # Extract AI score with fallback calculation
        ai_score = ai_results.get("ai_score", self._calculate_fallback_score(request))
        if isinstance(ai_score, str):
            try:
                ai_score = Decimal(ai_score)
            except:
                ai_score = self._calculate_fallback_score(request)
        
        # Determine confidence level
        confidence_level = self._determine_confidence_level(
            ai_score, ai_results.get("confidence", 0.8)
        )
        
        # Calculate deal probability
        deal_probability = self._calculate_deal_probability(ai_score, request)
        
        # Estimate deal size
        estimated_deal_size = self._estimate_deal_size(request, ai_results)
        
        # Extract risk factors and opportunities
        risk_factors = ai_results.get("risk_factors", self._generate_fallback_risks(request))
        opportunities = ai_results.get("opportunities", self._generate_fallback_opportunities(request))
        
        # Calculate detailed scores
        detailed_scores = self._calculate_detailed_scores(ai_results, request)
        
        return {
            "ai_score": ai_score,
            "confidence_level": confidence_level,
            "deal_probability": deal_probability,
            "estimated_deal_size": estimated_deal_size,
            "risk_factors": risk_factors,
            "opportunities": opportunities,
            "detailed_scores": detailed_scores
        }
    
    def _calculate_fallback_score(self, request: ProspectAnalysisRequest) -> Decimal:
        """Calculate fallback AI score when AI analysis fails"""
        score = 50.0  # Base score
        
        # Industry factor
        high_value_industries = ["technology", "healthcare", "financial", "energy"]
        if request.industry and any(ind in request.industry.lower() for ind in high_value_industries):
            score += 15
        
        # Revenue factor
        if request.revenue:
            if request.revenue >= 1_000_000_000:  # $1B+
                score += 20
            elif request.revenue >= 100_000_000:  # $100M+
                score += 15
            elif request.revenue >= 10_000_000:  # $10M+
                score += 10
        
        # Market cap factor
        if request.market_cap:
            if request.market_cap >= 1_000_000_000:  # $1B+
                score += 10
            elif request.market_cap >= 100_000_000:  # $100M+
                score += 8
        
        return Decimal(str(min(100, max(0, score))))
    
    def _determine_confidence_level(self, ai_score: Decimal, ai_confidence: float) -> str:
        """Determine confidence level based on score and AI confidence"""
        confidence_score = float(ai_score) * ai_confidence / 100
        
        if confidence_score >= 80:
            return "high"
        elif confidence_score >= 60:
            return "medium"
        else:
            return "low"
    
    def _calculate_deal_probability(
        self,
        ai_score: Decimal,
        request: ProspectAnalysisRequest
    ) -> Decimal:
        """Calculate deal probability based on AI score and other factors"""
        base_probability = float(ai_score) * 0.8  # Base on AI score
        
        # Adjust based on industry
        if request.industry:
            if "technology" in request.industry.lower():
                base_probability *= 1.1
            elif "healthcare" in request.industry.lower():
                base_probability *= 1.05
        
        # Adjust based on company size
        if request.revenue:
            if request.revenue >= 100_000_000:  # $100M+
                base_probability *= 1.1
            elif request.revenue >= 10_000_000:  # $10M+
                base_probability *= 1.05
        
        return Decimal(str(min(100, max(0, base_probability))))
    
    def _estimate_deal_size(
        self,
        request: ProspectAnalysisRequest,
        ai_results: Dict[str, Any]
    ) -> Decimal:
        """Estimate potential deal size"""
        
        # Base estimation on revenue if available
        if request.revenue:
            # Typical M&A deals are 1-3x revenue for most industries
            base_estimate = float(request.revenue) * 2.0
        elif request.market_cap:
            # Use market cap as base
            base_estimate = float(request.market_cap) * 1.2
        else:
            # Default estimate based on industry
            industry_estimates = {
                "technology": 50_000_000,
                "healthcare": 30_000_000,
                "financial": 100_000_000,
                "manufacturing": 25_000_000,
                "retail": 20_000_000
            }
            base_estimate = industry_estimates.get(
                request.industry.lower() if request.industry else "other",
                15_000_000
            )
        
        # Adjust based on AI analysis results
        ai_multiplier = ai_results.get("deal_size_multiplier", 1.0)
        if isinstance(ai_multiplier, str):
            try:
                ai_multiplier = float(ai_multiplier)
            except:
                ai_multiplier = 1.0
        
        final_estimate = base_estimate * ai_multiplier
        
        return Decimal(str(max(1_000_000, final_estimate)))  # Minimum $1M
    
    def _generate_fallback_risks(self, request: ProspectAnalysisRequest) -> List[str]:
        """Generate fallback risk factors"""
        risks = []
        
        if not request.revenue:
            risks.append("Limited financial transparency")
        
        if request.industry:
            industry_risks = {
                "technology": "Rapid technological change and competition",
                "healthcare": "Regulatory compliance and approval risks",
                "retail": "Consumer behavior shifts and market volatility",
                "manufacturing": "Supply chain and operational risks"
            }
            industry_risk = industry_risks.get(request.industry.lower())
            if industry_risk:
                risks.append(industry_risk)
        
        if not request.location:
            risks.append("Geographic market uncertainty")
        
        return risks or ["Standard market and operational risks"]
    
    def _generate_fallback_opportunities(self, request: ProspectAnalysisRequest) -> List[str]:
        """Generate fallback opportunities"""
        opportunities = []
        
        if request.industry:
            industry_opportunities = {
                "technology": "Digital transformation and innovation potential",
                "healthcare": "Aging population and healthcare demand growth",
                "financial": "Fintech integration and digital services expansion",
                "manufacturing": "Automation and efficiency improvements"
            }
            industry_opp = industry_opportunities.get(request.industry.lower())
            if industry_opp:
                opportunities.append(industry_opp)
        
        if request.revenue and request.revenue >= 50_000_000:
            opportunities.append("Scale advantages and market consolidation potential")
        
        return opportunities or ["Market expansion and operational optimization"]
    
    def _calculate_detailed_scores(
        self,
        ai_results: Dict[str, Any],
        request: ProspectAnalysisRequest
    ) -> Dict[str, int]:
        """Calculate detailed scoring breakdown"""
        
        # Extract from AI results or calculate fallbacks
        financial_health = ai_results.get("financial_health", 75)
        market_position = ai_results.get("market_position", 70)
        growth_potential = ai_results.get("growth_potential", 80)
        strategic_fit = ai_results.get("strategic_fit", 75)
        
        # Ensure all scores are integers
        return {
            "financial_health": int(financial_health),
            "market_position": int(market_position),
            "growth_potential": int(growth_potential),
            "strategic_fit": int(strategic_fit)
        }
    
    async def _generate_strategic_recommendations(
        self,
        ai_results: Dict[str, Any],
        request: ProspectAnalysisRequest,
        metrics: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate strategic recommendations"""
        
        ai_score = float(metrics["ai_score"])
        
        if ai_score >= 85:
            primary_approach = "Immediate engagement with senior leadership. High-priority target with strong strategic fit."
        elif ai_score >= 70:
            primary_approach = "Structured approach with detailed due diligence. Strong potential with manageable risks."
        elif ai_score >= 55:
            primary_approach = "Cautious evaluation with focus on risk mitigation. Monitor for improved conditions."
        else:
            primary_approach = "Limited engagement. Consider only if strategic circumstances change significantly."
        
        return {
            "primary_approach": primary_approach
        }
    
    def _get_fallback_ai_results(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback results when AI analysis fails"""
        return {
            "ai_score": 65,
            "confidence": 0.7,
            "financial_health": 70,
            "market_position": 65,
            "growth_potential": 75,
            "strategic_fit": 70,
            "risk_factors": ["Limited AI analysis available"],
            "opportunities": ["Standard market opportunities"],
            "deal_size_multiplier": 1.0
        }
    
    async def _fallback_prospect_analysis(
        self,
        request: ProspectAnalysisRequest,
        start_time: float
    ) -> ProspectAnalysisResponse:
        """Provide fallback analysis when enhanced analysis fails"""
        
        # Use basic scoring algorithm
        ai_score = self._calculate_fallback_score(request)
        processing_time = Decimal(str(time.time() - start_time))
        
        return ProspectAnalysisResponse(
            ai_score=ai_score,
            confidence_level="medium",
            deal_probability=ai_score * Decimal("0.8"),
            estimated_deal_size=Decimal("25000000"),  # $25M default
            risk_factors=self._generate_fallback_risks(request),
            opportunities=self._generate_fallback_opportunities(request),
            recommended_approach="Standard evaluation approach recommended",
            analysis_details={
                "financial_health": 70,
                "market_position": 65,
                "growth_potential": 75,
                "strategic_fit": 70
            },
            processing_time=processing_time,
            analysis_date=datetime.utcnow(),
            model_version=f"{self.model_version}-Fallback"
        )


# Create global instance
enhanced_prospect_ai = EnhancedProspectAI()
