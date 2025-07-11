"""
Pydantic schemas for Prospect AI module
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Base schemas
class ProspectBase(BaseModel):
    """Base prospect schema"""
    company_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    
    # Financial information
    revenue: Optional[Decimal] = None
    revenue_currency: str = "USD"
    ebitda: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    enterprise_value: Optional[Decimal] = None
    employees: Optional[str] = None
    
    # Growth metrics
    revenue_growth_rate: Optional[Decimal] = None
    ebitda_margin: Optional[Decimal] = None
    profit_margin: Optional[Decimal] = None
    debt_to_equity: Optional[Decimal] = None
    
    # Contact information
    primary_contact: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    # Metadata
    tags: List[str] = []
    notes: Optional[str] = None


class ProspectCreate(ProspectBase):
    """Schema for creating a new prospect"""
    assigned_to_id: Optional[UUID] = None
    priority: str = "medium"
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed = ["low", "medium", "high", "critical"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of: {allowed}")
        return v


class ProspectUpdate(BaseModel):
    """Schema for updating a prospect"""
    company_name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    revenue: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    employees: Optional[str] = None
    
    # AI scoring (updated by analysis)
    ai_score: Optional[Decimal] = None
    confidence_level: Optional[str] = None
    deal_probability: Optional[Decimal] = None
    estimated_deal_size: Optional[Decimal] = None
    
    # Status updates
    status: Optional[str] = None
    stage: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[UUID] = None
    
    # Contact tracking
    last_contact_date: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    
    # Metadata
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ProspectResponse(ProspectBase):
    """Schema for prospect responses"""
    id: UUID
    
    # AI scoring results
    ai_score: Optional[Decimal] = None
    confidence_level: Optional[str] = None
    deal_probability: Optional[Decimal] = None
    estimated_deal_size: Optional[Decimal] = None
    estimated_deal_size_currency: str = "USD"
    
    # Score breakdown
    strategic_fit_score: Optional[Decimal] = None
    financial_health_score: Optional[Decimal] = None
    market_position_score: Optional[Decimal] = None
    growth_potential_score: Optional[Decimal] = None
    
    # Risk and opportunities
    risk_factors: List[str] = []
    opportunities: List[str] = []
    recommended_approach: Optional[str] = None
    deal_type_recommendation: Optional[str] = None
    target_timeline: Optional[str] = None
    
    # Status and tracking
    status: str
    stage: str
    priority: str
    
    # Dates
    analysis_date: Optional[datetime] = None
    last_contact_date: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    last_data_update: Optional[datetime] = None
    
    # Relationships
    organization_id: UUID
    created_by_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Analysis schemas
class ProspectAnalysisRequest(BaseModel):
    """Request schema for prospect analysis"""
    company_name: str
    industry: Optional[str] = None
    location: Optional[str] = None
    revenue: Optional[Decimal] = None
    employees: Optional[str] = None
    market_cap: Optional[Decimal] = None
    
    financial_data: Optional[Dict[str, Any]] = {}
    criteria: Optional[Dict[str, Any]] = {}
    analysis_type: str = "full"  # "full", "financial", "market", "competitive"
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed = ["full", "financial", "market", "competitive"]
        if v not in allowed:
            raise ValueError(f"Analysis type must be one of: {allowed}")
        return v


class ProspectAnalysisResponse(BaseModel):
    """Response schema for prospect analysis"""
    prospect_id: Optional[UUID] = None
    ai_score: Decimal
    confidence_level: str
    risk_factors: List[str]
    opportunities: List[str]
    deal_probability: Decimal
    estimated_deal_size: Optional[Decimal] = None
    recommended_approach: str
    
    analysis_details: Dict[str, Any] = {
        "financial_health": 0,
        "market_position": 0,
        "growth_potential": 0,
        "strategic_fit": 0
    }
    
    processing_time: Optional[Decimal] = None
    analysis_date: datetime
    model_version: Optional[str] = None


class ProspectScoringRequest(BaseModel):
    """Request schema for prospect scoring"""
    prospects: List[Dict[str, Any]]
    scoring_criteria: Dict[str, Decimal] = {
        "revenue_weight": 0.25,
        "growth_weight": 0.25,
        "profitability_weight": 0.25,
        "market_position_weight": 0.25
    }
    
    @validator('scoring_criteria')
    def validate_weights(cls, v):
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError("Scoring criteria weights must sum to 1.0")
        return v


class ScoredProspect(BaseModel):
    """Individual scored prospect"""
    company_id: Optional[str] = None
    company_name: str
    total_score: Decimal
    score_breakdown: Dict[str, Decimal]
    ranking: int
    recommendation: str


class ProspectScoringResponse(BaseModel):
    """Response schema for prospect scoring"""
    scored_prospects: List[ScoredProspect]
    summary: Dict[str, Any] = {
        "total_prospects": 0,
        "average_score": 0,
        "top_quartile_threshold": 0
    }


# Market Intelligence schemas
class MarketIntelligenceRequest(BaseModel):
    """Request schema for market intelligence"""
    industry: Optional[str] = None
    region: Optional[str] = None
    time_period: str = "3M"  # "1M", "3M", "6M", "1Y"
    deal_type: Optional[str] = None
    
    @validator('time_period')
    def validate_time_period(cls, v):
        allowed = ["1M", "3M", "6M", "1Y"]
        if v not in allowed:
            raise ValueError(f"Time period must be one of: {allowed}")
        return v


class MarketTransaction(BaseModel):
    """Market transaction data"""
    target: str
    acquirer: Optional[str] = None
    deal_size: Optional[Decimal] = None
    industry: str
    date: str
    deal_type: str


class MarketAlert(BaseModel):
    """Market alert information"""
    type: str
    message: str
    severity: str
    date: str


class IndustryTrend(BaseModel):
    """Industry trend data"""
    industry: str
    growth_rate: Decimal
    deal_activity: int
    key_drivers: List[str]
    outlook: str


class MarketIntelligenceResponse(BaseModel):
    """Response schema for market intelligence"""
    market_overview: Dict[str, Any] = {
        "total_deal_volume": 0,
        "average_deal_size": 0,
        "deal_count": 0,
        "market_sentiment": "neutral"
    }
    
    industry_trends: List[IndustryTrend] = []
    recent_transactions: List[MarketTransaction] = []
    market_alerts: List[MarketAlert] = []
    
    generated_at: datetime
    time_period: str
    data_sources: List[str] = []


# Search and filtering schemas
class ProspectSearchRequest(BaseModel):
    """Request schema for prospect search"""
    query: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    min_revenue: Optional[Decimal] = None
    max_revenue: Optional[Decimal] = None
    min_ai_score: Optional[Decimal] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[UUID] = None
    
    # Pagination
    skip: int = 0
    limit: int = 100
    
    # Sorting
    sort_by: str = "ai_score"
    sort_order: str = "desc"
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed = ["ai_score", "deal_probability", "revenue", "created_at", "company_name"]
        if v not in allowed:
            raise ValueError(f"Sort by must be one of: {allowed}")
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        allowed = ["asc", "desc"]
        if v not in allowed:
            raise ValueError(f"Sort order must be one of: {allowed}")
        return v


class ProspectListResponse(BaseModel):
    """Response schema for prospect lists"""
    prospects: List[ProspectResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
