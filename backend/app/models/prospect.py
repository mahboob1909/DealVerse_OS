"""
Prospect model for AI-powered deal sourcing and scoring
"""
from sqlalchemy import Column, String, Text, Numeric, JSON, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.models.base import BaseModel


class Prospect(BaseModel):
    """Prospect model for AI-powered deal sourcing and opportunity management"""
    
    __tablename__ = "prospects"
    
    # Basic company information
    company_name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    industry = Column(String(100), index=True)
    sub_industry = Column(String(100))
    location = Column(String(255))
    country = Column(String(100))
    region = Column(String(100))
    
    # Financial information
    revenue = Column(Numeric(15, 2))
    revenue_currency = Column(String(3), default="USD")
    ebitda = Column(Numeric(15, 2))
    market_cap = Column(Numeric(15, 2))
    enterprise_value = Column(Numeric(15, 2))
    employees = Column(String(20))  # e.g., "100-500", "1000+"
    
    # Growth metrics
    revenue_growth_rate = Column(Numeric(5, 2))  # Percentage
    ebitda_margin = Column(Numeric(5, 2))  # Percentage
    profit_margin = Column(Numeric(5, 2))  # Percentage
    debt_to_equity = Column(Numeric(5, 2))
    
    # AI Scoring and Analysis
    ai_score = Column(Numeric(5, 2))  # 0-100 AI confidence score
    confidence_level = Column(String(20))  # "low", "medium", "high"
    deal_probability = Column(Numeric(5, 2))  # 0-100 percentage
    estimated_deal_size = Column(Numeric(15, 2))
    estimated_deal_size_currency = Column(String(3), default="USD")
    
    # Risk and opportunity assessment
    risk_factors = Column(JSON, default=list)  # List of identified risks
    opportunities = Column(JSON, default=list)  # List of opportunities
    strategic_fit_score = Column(Numeric(5, 2))  # 0-100
    financial_health_score = Column(Numeric(5, 2))  # 0-100
    market_position_score = Column(Numeric(5, 2))  # 0-100
    growth_potential_score = Column(Numeric(5, 2))  # 0-100
    
    # Deal context
    recommended_approach = Column(Text)
    deal_type_recommendation = Column(String(50))  # "M&A", "IPO", "Debt", "Equity"
    target_timeline = Column(String(50))  # "immediate", "3-6 months", "6-12 months"
    
    # External data sources
    data_sources = Column(JSON, default=list)  # List of data sources used
    last_data_update = Column(DateTime(timezone=True), server_default=func.now())
    data_quality_score = Column(Numeric(5, 2))  # 0-100
    
    # Tracking and status
    status = Column(String(50), default="identified")  # "identified", "analyzing", "qualified", "contacted", "engaged", "lost"
    stage = Column(String(50), default="prospect")  # "prospect", "lead", "opportunity", "deal"
    priority = Column(String(20), default="medium")  # "low", "medium", "high", "critical"
    
    # Contact and engagement
    primary_contact = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    last_contact_date = Column(DateTime(timezone=True))
    next_follow_up = Column(DateTime(timezone=True))
    
    # Additional metadata
    tags = Column(JSON, default=list)
    notes = Column(Text)
    website = Column(String(255))
    linkedin_url = Column(String(255))
    
    # Analysis metadata
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    analysis_version = Column(String(20), default="1.0")
    requires_reanalysis = Column(Boolean, default=False)
    
    # Relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    organization = relationship("Organization", back_populates="prospects")
    created_by = relationship("User", foreign_keys=[created_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    analyses = relationship("ProspectAnalysis", back_populates="prospect")


class ProspectAnalysis(BaseModel):
    """Detailed analysis results for prospects"""
    
    __tablename__ = "prospect_analyses"
    
    # Reference to prospect
    prospect_id = Column(UUID(as_uuid=True), ForeignKey("prospects.id"), nullable=False)
    
    # Analysis metadata
    analysis_type = Column(String(50), nullable=False)  # "full", "financial", "market", "competitive"
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    analysis_version = Column(String(20), default="1.0")
    
    # Analysis results
    overall_score = Column(Numeric(5, 2))  # 0-100
    confidence_score = Column(Numeric(5, 2))  # 0-100
    
    # Detailed scoring breakdown
    financial_score = Column(Numeric(5, 2))
    growth_score = Column(Numeric(5, 2))
    market_score = Column(Numeric(5, 2))
    strategic_score = Column(Numeric(5, 2))
    risk_score = Column(Numeric(5, 2))
    
    # Analysis details
    key_findings = Column(JSON, default=list)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    opportunities = Column(JSON, default=list)
    threats = Column(JSON, default=list)
    
    # Recommendations
    recommendations = Column(JSON, default=list)
    next_steps = Column(JSON, default=list)
    deal_structure_suggestions = Column(JSON, default=list)
    
    # Market context
    industry_trends = Column(JSON, default=list)
    competitive_landscape = Column(JSON, default=list)
    market_conditions = Column(JSON, default=dict)
    
    # Processing metadata
    processing_time_seconds = Column(Numeric(8, 2))
    data_sources_used = Column(JSON, default=list)
    model_version = Column(String(50))
    
    # Relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    prospect = relationship("Prospect", back_populates="analyses")
    organization = relationship("Organization")
    created_by = relationship("User")


class MarketIntelligence(BaseModel):
    """Market intelligence and trend data"""
    
    __tablename__ = "market_intelligence"
    
    # Market segment information
    industry = Column(String(100), nullable=False, index=True)
    sub_industry = Column(String(100))
    region = Column(String(100))
    market_segment = Column(String(100))
    
    # Time period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20))  # "monthly", "quarterly", "yearly"
    
    # Market metrics
    total_deal_volume = Column(Numeric(15, 2))
    deal_count = Column(Integer)
    average_deal_size = Column(Numeric(15, 2))
    median_deal_size = Column(Numeric(15, 2))
    
    # Market sentiment and trends
    market_sentiment = Column(String(20))  # "bullish", "bearish", "neutral"
    growth_rate = Column(Numeric(5, 2))  # Percentage
    volatility_index = Column(Numeric(5, 2))
    
    # Deal activity breakdown
    deal_types = Column(JSON, default=dict)  # {"M&A": 45, "IPO": 12, "Debt": 23}
    deal_stages = Column(JSON, default=dict)  # Distribution by stage
    
    # Key trends and drivers
    key_trends = Column(JSON, default=list)
    growth_drivers = Column(JSON, default=list)
    risk_factors = Column(JSON, default=list)
    
    # Notable transactions
    notable_transactions = Column(JSON, default=list)
    
    # Outlook and predictions
    outlook = Column(String(20))  # "positive", "negative", "stable"
    outlook_timeframe = Column(String(50))  # "3 months", "6 months", "1 year"
    predicted_trends = Column(JSON, default=list)
    
    # Data sources and quality
    data_sources = Column(JSON, default=list)
    data_quality_score = Column(Numeric(5, 2))
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    organization = relationship("Organization")
    created_by = relationship("User")


# Add relationships to existing models
def add_prospect_relationships():
    """Add prospect relationships to existing models"""
    from app.models.organization import Organization
    from app.models.user import User
    
    # Add to Organization model
    if not hasattr(Organization, 'prospects'):
        Organization.prospects = relationship("Prospect", back_populates="organization")
    
    # Add to Prospect model
    if not hasattr(Prospect, 'analyses'):
        Prospect.analyses = relationship("ProspectAnalysis", back_populates="prospect")
