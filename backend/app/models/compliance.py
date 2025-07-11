"""
Compliance models for regulatory tracking and audit management
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Boolean, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import BaseModel


class ComplianceStatus(str, enum.Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"


class ComplianceCategory(BaseModel):
    """Compliance categories (SEC, FINRA, AML, etc.)"""
    
    __tablename__ = "compliance_categories"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    code = Column(String(50), unique=True, nullable=False)  # SEC, FINRA, AML, etc.
    
    # Category configuration
    is_active = Column(Boolean, default=True)
    priority_level = Column(Integer, default=1)  # 1=High, 2=Medium, 3=Low
    review_frequency_days = Column(Integer, default=30)  # How often to review
    
    # Regulatory information
    regulatory_body = Column(String(255))  # SEC, FINRA, etc.
    regulation_url = Column(String(500))
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")
    
    # Relationships
    requirements = relationship("ComplianceRequirement", back_populates="category", cascade="all, delete-orphan")
    assessments = relationship("ComplianceAssessment", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ComplianceCategory(id={self.id}, name='{self.name}', code='{self.code}')>"


class ComplianceRequirement(BaseModel):
    """Individual compliance requirements within a category"""
    
    __tablename__ = "compliance_requirements"
    
    # Basic information
    title = Column(String(500), nullable=False)
    description = Column(Text)
    requirement_code = Column(String(100))  # Internal reference code
    
    # Requirement details
    is_mandatory = Column(Boolean, default=True)
    risk_level = Column(String(20), default="medium")  # high, medium, low
    
    # Documentation and evidence
    required_documents = Column(JSON, default=list)  # List of required document types
    evidence_requirements = Column(Text)
    
    # Timing and frequency
    due_date = Column(DateTime)
    review_frequency_days = Column(Integer, default=90)
    last_review_date = Column(DateTime)
    next_review_date = Column(DateTime)
    
    # Status tracking
    status = Column(Enum(ComplianceStatus), default=ComplianceStatus.PENDING)
    completion_percentage = Column(Float, default=0.0)
    
    # Category relationship
    category_id = Column(UUID(as_uuid=True), ForeignKey("compliance_categories.id"), nullable=False)
    category = relationship("ComplianceCategory", back_populates="requirements")
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")
    
    # Relationships
    assessments = relationship("ComplianceAssessment", back_populates="requirement")
    audit_logs = relationship("ComplianceAuditLog", back_populates="requirement")
    
    def __repr__(self):
        return f"<ComplianceRequirement(id={self.id}, title='{self.title}', status='{self.status}')>"


class ComplianceAssessment(BaseModel):
    """Compliance assessments and reviews"""
    
    __tablename__ = "compliance_assessments"
    
    # Assessment information
    assessment_date = Column(DateTime, default=datetime.utcnow)
    assessment_type = Column(String(50), default="regular")  # regular, audit, spot_check, annual
    
    # Results
    status = Column(Enum(ComplianceStatus), nullable=False)
    score = Column(Float)  # 0-100 compliance score
    findings = Column(Text)
    recommendations = Column(Text)
    
    # Risk assessment
    risk_level = Column(String(20), default="low")  # critical, high, medium, low
    impact_assessment = Column(Text)
    
    # Evidence and documentation
    evidence_provided = Column(JSON, default=list)  # List of document IDs or references
    supporting_documents = Column(JSON, default=list)
    
    # Follow-up actions
    action_items = Column(JSON, default=list)
    remediation_plan = Column(Text)
    target_completion_date = Column(DateTime)
    
    # Relationships
    category_id = Column(UUID(as_uuid=True), ForeignKey("compliance_categories.id"))
    category = relationship("ComplianceCategory", back_populates="assessments")
    
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("compliance_requirements.id"))
    requirement = relationship("ComplianceRequirement", back_populates="assessments")
    
    # User who conducted the assessment
    assessed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assessed_by = relationship("User")
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")
    
    def __repr__(self):
        return f"<ComplianceAssessment(id={self.id}, status='{self.status}', score={self.score})>"


class ComplianceAuditLog(BaseModel):
    """Audit trail for compliance activities"""
    
    __tablename__ = "compliance_audit_logs"
    
    # Event information
    event_type = Column(String(100), nullable=False)  # assessment_created, status_changed, etc.
    event_description = Column(Text)
    event_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Event details
    old_values = Column(JSON, default=dict)  # Previous state
    new_values = Column(JSON, default=dict)  # New state
    event_metadata = Column(JSON, default=dict)  # Additional context
    
    # User and system information
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User")
    
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    
    # Related entities
    requirement_id = Column(UUID(as_uuid=True), ForeignKey("compliance_requirements.id"))
    requirement = relationship("ComplianceRequirement", back_populates="audit_logs")
    
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("compliance_assessments.id"))
    assessment = relationship("ComplianceAssessment")
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")
    
    def __repr__(self):
        return f"<ComplianceAuditLog(id={self.id}, event_type='{self.event_type}', timestamp={self.event_timestamp})>"


class RegulatoryUpdate(BaseModel):
    """Track regulatory updates and changes"""
    
    __tablename__ = "regulatory_updates"
    
    # Update information
    title = Column(String(500), nullable=False)
    description = Column(Text)
    update_type = Column(String(50), default="regulation_change")  # new_regulation, amendment, guidance, etc.
    
    # Source and timing
    source = Column(String(255))  # SEC, FINRA, etc.
    publication_date = Column(DateTime)
    effective_date = Column(DateTime)
    
    # Impact assessment
    impact_level = Column(String(20), default="medium")  # critical, high, medium, low
    affected_categories = Column(JSON, default=list)  # List of compliance category IDs
    
    # Content and links
    content = Column(Text)
    source_url = Column(String(500))
    document_references = Column(JSON, default=list)
    
    # Status tracking
    is_reviewed = Column(Boolean, default=False)
    review_notes = Column(Text)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_by = relationship("User")
    reviewed_at = Column(DateTime)
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")
    
    def __repr__(self):
        return f"<RegulatoryUpdate(id={self.id}, title='{self.title}', impact='{self.impact_level}')>"


# Compliance models are ready for use
