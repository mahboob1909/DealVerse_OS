"""
Deal model for investment banking deals
"""
from sqlalchemy import Column, String, Text, Numeric, Date, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Deal(BaseModel):
    """Deal model for tracking investment banking deals"""
    
    __tablename__ = "deals"
    
    # Basic deal information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    deal_type = Column(String(50), nullable=False)  # M&A, IPO, Debt, Equity, etc.
    
    # Financial information
    deal_value = Column(Numeric(15, 2))
    currency = Column(String(3), default="USD")
    fee_amount = Column(Numeric(15, 2))
    fee_percentage = Column(Numeric(5, 2))
    
    # Deal status and progress
    stage = Column(String(50), default="prospecting")  # prospecting, pitch, negotiation, due_diligence, closing, closed, lost
    status = Column(String(50), default="active")  # active, on_hold, cancelled, completed
    probability = Column(String(3))  # 0-100 percentage
    
    # Important dates
    expected_close_date = Column(Date)
    actual_close_date = Column(Date)
    pitch_date = Column(Date)
    
    # Target company information
    target_company = Column(String(255))
    target_industry = Column(String(100))
    target_location = Column(String(255))
    target_revenue = Column(Numeric(15, 2))
    target_employees = Column(String(20))
    
    # Deal team and relationships
    lead_banker = Column(String(255))
    deal_team = Column(JSON, default=list)  # List of team member IDs and roles
    
    # AI and analytics
    ai_score = Column(String(3))  # AI confidence score 0-100
    risk_factors = Column(JSON, default=list)
    opportunities = Column(JSON, default=list)
    
    # Additional metadata
    tags = Column(JSON, default=list)
    notes = Column(Text)
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="deals")
    
    # Client relationship
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    client = relationship("Client", back_populates="deals")
    
    # User relationship (deal creator)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_by = relationship("User", back_populates="created_deals")
    
    # Related entities
    tasks = relationship("Task", back_populates="deal", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="deal", cascade="all, delete-orphan")
    financial_models = relationship("FinancialModel", back_populates="deal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Deal(id={self.id}, title='{self.title}', stage='{self.stage}', value={self.deal_value})>"

    # Database indexes for performance optimization
    __table_args__ = (
        # Single column indexes for frequently queried fields
        Index('idx_deals_organization_id', 'organization_id'),
        Index('idx_deals_client_id', 'client_id'),
        Index('idx_deals_created_by_id', 'created_by_id'),
        Index('idx_deals_stage', 'stage'),
        Index('idx_deals_status', 'status'),
        Index('idx_deals_deal_type', 'deal_type'),
        Index('idx_deals_target_industry', 'target_industry'),
        Index('idx_deals_created_at', 'created_at'),
        Index('idx_deals_updated_at', 'updated_at'),
        Index('idx_deals_expected_close_date', 'expected_close_date'),
        Index('idx_deals_actual_close_date', 'actual_close_date'),

        # Composite indexes for common query patterns
        Index('idx_deals_org_stage', 'organization_id', 'stage'),
        Index('idx_deals_org_status', 'organization_id', 'status'),
        Index('idx_deals_org_type', 'organization_id', 'deal_type'),
        Index('idx_deals_org_created', 'organization_id', 'created_at'),
        Index('idx_deals_stage_status', 'stage', 'status'),
        Index('idx_deals_org_stage_status', 'organization_id', 'stage', 'status'),
        Index('idx_deals_client_stage', 'client_id', 'stage'),
        Index('idx_deals_created_by_stage', 'created_by_id', 'stage'),

        # Indexes for date-based queries
        Index('idx_deals_org_close_date', 'organization_id', 'expected_close_date'),
        Index('idx_deals_stage_close_date', 'stage', 'expected_close_date'),

        # Indexes for value-based queries and sorting
        Index('idx_deals_org_value', 'organization_id', 'deal_value'),
        Index('idx_deals_stage_value', 'stage', 'deal_value'),
    )
