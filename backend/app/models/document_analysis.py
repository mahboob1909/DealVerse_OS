"""
Enhanced document analysis models for Diligence Navigator
"""
from sqlalchemy import Column, String, Text, Numeric, JSON, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.models.base import BaseModel


class DocumentAnalysis(BaseModel):
    """Detailed AI analysis results for documents"""
    
    __tablename__ = "document_analyses"
    
    # Reference to document
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    
    # Analysis metadata
    analysis_type = Column(String(50), nullable=False)  # "full", "risk_only", "financial_only", "legal_only"
    analysis_version = Column(String(20), default="1.0")
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    processing_time_seconds = Column(Numeric(8, 2))
    
    # Overall analysis results
    overall_risk_score = Column(Numeric(5, 2))  # 0-100
    confidence_score = Column(Numeric(5, 2))  # 0-100
    analysis_status = Column(String(50), default="completed")  # "processing", "completed", "failed"
    
    # Risk assessment
    risk_level = Column(String(20))  # "low", "medium", "high", "critical"
    risk_categories = Column(JSON, default=list)  # List of risk category objects
    critical_issues = Column(JSON, default=list)  # List of critical issues found
    
    # Document content analysis
    summary = Column(Text)
    key_findings = Column(JSON, default=list)
    extracted_entities = Column(JSON, default=dict)  # People, companies, dates, amounts
    extracted_clauses = Column(JSON, default=list)  # Important contract clauses
    
    # Financial data extraction
    financial_figures = Column(JSON, default=list)  # Revenue, costs, valuations, etc.
    key_dates = Column(JSON, default=list)  # Important dates and deadlines
    parties_involved = Column(JSON, default=list)  # Companies, individuals mentioned
    
    # Contract and legal analysis
    contract_terms = Column(JSON, default=list)  # Key contract terms
    legal_risks = Column(JSON, default=list)  # Legal risk factors
    compliance_flags = Column(JSON, default=list)  # Compliance issues
    
    # Anomaly detection
    anomalies = Column(JSON, default=list)  # Unusual patterns or data points
    inconsistencies = Column(JSON, default=list)  # Data inconsistencies
    missing_information = Column(JSON, default=list)  # Expected but missing info
    
    # Quality assessment
    document_quality_score = Column(Numeric(5, 2))  # 0-100
    completeness_score = Column(Numeric(5, 2))  # 0-100
    readability_score = Column(Numeric(5, 2))  # 0-100
    
    # AI model information
    model_version = Column(String(50))
    model_confidence = Column(Numeric(5, 2))
    processing_notes = Column(Text)
    
    # Relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    document = relationship("Document", back_populates="analyses")
    organization = relationship("Organization")
    created_by = relationship("User")


class RiskAssessment(BaseModel):
    """Comprehensive risk assessment for deals or document sets"""
    
    __tablename__ = "risk_assessments"
    
    # Assessment metadata
    assessment_name = Column(String(255), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # "deal", "document_set", "compliance"
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Scope of assessment
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"))
    document_ids = Column(JSON, default=list)  # List of document IDs included
    
    # Overall risk metrics
    overall_risk_score = Column(Numeric(5, 2), nullable=False)  # 0-100
    risk_level = Column(String(20), nullable=False)  # "low", "medium", "high", "critical"
    confidence_level = Column(Numeric(5, 2))  # 0-100
    
    # Risk category breakdown
    financial_risk_score = Column(Numeric(5, 2))
    legal_risk_score = Column(Numeric(5, 2))
    operational_risk_score = Column(Numeric(5, 2))
    compliance_risk_score = Column(Numeric(5, 2))
    market_risk_score = Column(Numeric(5, 2))
    
    # Detailed risk analysis
    risk_categories = Column(JSON, default=list)  # Detailed risk category analysis
    critical_issues = Column(JSON, default=list)  # High-priority issues requiring attention
    medium_issues = Column(JSON, default=list)  # Medium-priority issues
    low_issues = Column(JSON, default=list)  # Low-priority issues for monitoring
    
    # Recommendations and mitigation
    recommendations = Column(JSON, default=list)  # Risk mitigation recommendations
    action_items = Column(JSON, default=list)  # Specific actions to take
    timeline_recommendations = Column(JSON, default=list)  # Timeline for addressing risks
    
    # Missing documents and information
    missing_documents = Column(JSON, default=list)  # Documents that should be provided
    information_gaps = Column(JSON, default=list)  # Missing information that affects assessment
    
    # Compliance status
    compliance_status = Column(String(50), default="pending")  # "compliant", "non_compliant", "review_required"
    regulatory_issues = Column(JSON, default=list)  # Regulatory compliance issues
    required_actions = Column(JSON, default=list)  # Actions required for compliance
    
    # Assessment quality and completeness
    assessment_completeness = Column(Numeric(5, 2))  # 0-100
    data_quality_score = Column(Numeric(5, 2))  # 0-100
    assessment_notes = Column(Text)
    
    # Relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    deal = relationship("Deal")
    organization = relationship("Organization")
    created_by = relationship("User")


class DocumentCategory(BaseModel):
    """Document categorization and classification"""
    
    __tablename__ = "document_categories"
    
    # Category information
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category_type = Column(String(50))  # "financial", "legal", "operational", "marketing"
    
    # Classification rules
    keywords = Column(JSON, default=list)  # Keywords for auto-classification
    file_patterns = Column(JSON, default=list)  # Filename patterns
    required_fields = Column(JSON, default=list)  # Required data fields for this category
    
    # Risk and compliance settings
    default_risk_level = Column(String(20), default="medium")
    compliance_requirements = Column(JSON, default=list)  # Compliance checks for this category
    review_requirements = Column(JSON, default=dict)  # Review process requirements
    
    # Analysis settings
    analysis_priority = Column(String(20), default="medium")  # "low", "medium", "high"
    auto_analysis_enabled = Column(Boolean, default=True)
    analysis_templates = Column(JSON, default=list)  # Analysis templates to apply
    
    # Relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    organization = relationship("Organization")
    created_by = relationship("User")


class DocumentReview(BaseModel):
    """Document review and approval workflow"""
    
    __tablename__ = "document_reviews"
    
    # Review metadata
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    review_type = Column(String(50), nullable=False)  # "initial", "compliance", "legal", "final"
    review_status = Column(String(50), default="pending")  # "pending", "in_progress", "approved", "rejected", "needs_revision"
    
    # Reviewer information
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    review_date = Column(DateTime(timezone=True))
    review_deadline = Column(DateTime(timezone=True))
    
    # Review results
    approval_status = Column(String(50))  # "approved", "rejected", "conditional"
    review_score = Column(Numeric(5, 2))  # 0-100
    review_notes = Column(Text)
    
    # Issues and recommendations
    issues_found = Column(JSON, default=list)  # Issues identified during review
    recommendations = Column(JSON, default=list)  # Reviewer recommendations
    required_changes = Column(JSON, default=list)  # Changes required before approval
    
    # Review checklist
    checklist_items = Column(JSON, default=list)  # Review checklist with completion status
    checklist_completion = Column(Numeric(5, 2), default=0)  # 0-100
    
    # Escalation and workflow
    escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text)
    escalated_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    
    # Relationships
    document = relationship("Document")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    escalated_to = relationship("User", foreign_keys=[escalated_to_id])
    organization = relationship("Organization")


class DocumentComparison(BaseModel):
    """Document comparison and version analysis"""
    
    __tablename__ = "document_comparisons"
    
    # Comparison metadata
    comparison_name = Column(String(255), nullable=False)
    comparison_type = Column(String(50))  # "version", "similar_docs", "template_match"
    comparison_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Documents being compared
    primary_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    secondary_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    
    # Comparison results
    similarity_score = Column(Numeric(5, 2))  # 0-100
    differences_found = Column(JSON, default=list)  # List of differences
    similarities = Column(JSON, default=list)  # List of similarities
    
    # Change analysis
    additions = Column(JSON, default=list)  # Content added in secondary doc
    deletions = Column(JSON, default=list)  # Content removed from primary doc
    modifications = Column(JSON, default=list)  # Content modified between docs
    
    # Risk impact of changes
    risk_impact_score = Column(Numeric(5, 2))  # 0-100
    high_risk_changes = Column(JSON, default=list)  # Changes that increase risk
    compliance_impact = Column(JSON, default=list)  # Changes affecting compliance
    
    # Analysis notes
    comparison_summary = Column(Text)
    analyst_notes = Column(Text)
    
    # Relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    primary_document = relationship("Document", foreign_keys=[primary_document_id])
    secondary_document = relationship("Document", foreign_keys=[secondary_document_id])
    organization = relationship("Organization")
    created_by = relationship("User")


# Add relationships to existing Document model
def add_document_analysis_relationships():
    """Add document analysis relationships to existing models"""
    from app.models.document import Document
    
    # Add to Document model
    if not hasattr(Document, 'analyses'):
        Document.analyses = relationship("DocumentAnalysis", back_populates="document")
    
    if not hasattr(Document, 'reviews'):
        Document.reviews = relationship("DocumentReview", back_populates="document")
