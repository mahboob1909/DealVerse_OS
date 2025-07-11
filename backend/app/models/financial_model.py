"""
Financial Model for valuation and modeling hub
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class FinancialModel(BaseModel):
    """Financial model for valuation and scenario analysis"""
    
    __tablename__ = "financial_models"
    
    # Basic model information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    model_type = Column(String(100), nullable=False)  # DCF, LBO, Comps, Precedent, etc.
    
    # Version control
    version = Column(Integer, default=1)
    is_current = Column(Boolean, default=True)
    parent_model_id = Column(UUID(as_uuid=True), ForeignKey("financial_models.id"))
    
    # Model data and structure
    model_data = Column(JSON, nullable=False)  # The actual model data/spreadsheet
    assumptions = Column(JSON, default=dict)  # Key assumptions
    inputs = Column(JSON, default=dict)  # Input parameters
    outputs = Column(JSON, default=dict)  # Calculated outputs
    
    # Scenarios and sensitivity analysis
    base_case = Column(JSON, default=dict)
    upside_case = Column(JSON, default=dict)
    downside_case = Column(JSON, default=dict)
    sensitivity_analysis = Column(JSON, default=dict)
    
    # Valuation results
    enterprise_value = Column(String(20))
    equity_value = Column(String(20))
    share_price = Column(String(20))
    valuation_multiple = Column(String(10))
    
    # Model status and approval
    status = Column(String(50), default="draft")  # draft, review, approved, archived
    approval_status = Column(String(50), default="pending")  # pending, approved, rejected
    reviewer_notes = Column(Text)
    
    # Collaboration and access
    is_shared = Column(Boolean, default=False)
    access_level = Column(String(50), default="deal_team")  # private, deal_team, organization
    collaborators = Column(JSON, default=list)  # List of user IDs with access
    
    # Metadata
    tags = Column(JSON, default=list)
    notes = Column(Text)
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="financial_models")
    
    # Deal relationship
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)
    deal = relationship("Deal", back_populates="financial_models")
    
    # User relationship (creator)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", back_populates="created_models")
    
    # Version relationships
    parent_model = relationship("FinancialModel", remote_side="FinancialModel.id")
    child_models = relationship("FinancialModel", back_populates="parent_model")
    
    def __repr__(self):
        return f"<FinancialModel(id={self.id}, name='{self.name}', type='{self.model_type}', version={self.version})>"
