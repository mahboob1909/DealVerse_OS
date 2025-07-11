"""
Pydantic schemas for Document Analysis and Diligence Navigator
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Document Analysis Schemas
class DocumentAnalysisRequest(BaseModel):
    """Request schema for document analysis"""
    document_id: UUID
    analysis_type: str = "full"  # "full", "risk_only", "financial_only", "legal_only"
    priority: str = "medium"  # "low", "medium", "high"
    custom_parameters: Optional[Dict[str, Any]] = {}
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed = ["full", "risk_only", "financial_only", "legal_only", "compliance_only"]
        if v not in allowed:
            raise ValueError(f"Analysis type must be one of: {allowed}")
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed = ["low", "medium", "high"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of: {allowed}")
        return v


class ExtractedEntity(BaseModel):
    """Extracted entity from document"""
    entity_type: str  # "person", "company", "date", "amount", "location"
    entity_value: str
    confidence: Decimal
    context: Optional[str] = None
    position: Optional[Dict[str, int]] = None  # Page, line, character position


class ExtractedClause(BaseModel):
    """Extracted contract clause"""
    clause_type: str  # "termination", "liability", "payment", "confidentiality"
    clause_text: str
    importance: str  # "low", "medium", "high", "critical"
    risk_level: str  # "low", "medium", "high"
    recommendations: List[str] = []


class FinancialFigure(BaseModel):
    """Extracted financial figure"""
    metric: str  # "revenue", "ebitda", "valuation", "debt"
    value: Decimal
    currency: str = "USD"
    period: Optional[str] = None  # "Q1 2023", "FY 2022"
    confidence: Decimal
    context: Optional[str] = None


class KeyDate(BaseModel):
    """Important date extracted from document"""
    event: str  # "contract_expiry", "payment_due", "milestone"
    date: str  # ISO date string
    importance: str  # "low", "medium", "high", "critical"
    description: Optional[str] = None


class RiskCategory(BaseModel):
    """Risk category analysis"""
    category: str  # "financial", "legal", "operational", "compliance", "market"
    score: Decimal  # 0-100
    level: str  # "low", "medium", "high", "critical"
    findings: List[str] = []
    recommendations: List[str] = []
    supporting_evidence: List[str] = []


class CriticalIssue(BaseModel):
    """Critical issue requiring attention"""
    issue_type: str  # "legal_risk", "financial_concern", "compliance_violation"
    severity: str  # "medium", "high", "critical"
    description: str
    impact: str  # Description of potential impact
    mitigation: Optional[str] = None  # Suggested mitigation
    timeline: Optional[str] = None  # Timeline for resolution
    supporting_documents: List[str] = []


class Anomaly(BaseModel):
    """Detected anomaly in document"""
    anomaly_type: str  # "data_inconsistency", "unusual_pattern", "missing_info"
    description: str
    severity: str  # "low", "medium", "high"
    location: Optional[str] = None  # Where in document
    confidence: Decimal


class ComplianceFlag(BaseModel):
    """Compliance issue flag"""
    regulation: str  # "SOX", "GDPR", "SEC", "FINRA"
    issue_type: str  # "violation", "risk", "requirement"
    description: str
    severity: str  # "low", "medium", "high", "critical"
    recommendation: str
    deadline: Optional[str] = None


class DocumentAnalysisResponse(BaseModel):
    """Response schema for document analysis"""
    analysis_id: UUID
    document_id: UUID
    analysis_type: str
    status: str  # "processing", "completed", "failed"
    
    # Overall results
    overall_risk_score: Decimal
    confidence_score: Decimal
    risk_level: str
    
    # Analysis results
    summary: str
    key_findings: List[str]
    
    # Extracted data
    extracted_entities: Dict[str, List[ExtractedEntity]] = {}
    extracted_clauses: List[ExtractedClause] = []
    financial_figures: List[FinancialFigure] = []
    key_dates: List[KeyDate] = []
    parties_involved: List[str] = []
    
    # Risk assessment
    risk_categories: List[RiskCategory] = []
    critical_issues: List[CriticalIssue] = []
    anomalies: List[Anomaly] = []
    compliance_flags: List[ComplianceFlag] = []
    
    # Quality metrics
    document_quality_score: Decimal
    completeness_score: Decimal
    processing_time: Decimal
    
    # Metadata
    analysis_date: datetime
    model_version: str


# Risk Assessment Schemas
class RiskAssessmentRequest(BaseModel):
    """Request schema for risk assessment"""
    assessment_name: str
    assessment_type: str = "deal"  # "deal", "document_set", "compliance"
    deal_id: Optional[UUID] = None
    document_ids: List[UUID] = []
    include_missing_docs: bool = True
    
    @validator('assessment_type')
    def validate_assessment_type(cls, v):
        allowed = ["deal", "document_set", "compliance"]
        if v not in allowed:
            raise ValueError(f"Assessment type must be one of: {allowed}")
        return v


class MissingDocument(BaseModel):
    """Missing document information"""
    document_type: str
    importance: str  # "low", "medium", "high", "critical"
    deadline: Optional[str] = None
    impact_if_missing: str
    alternatives: List[str] = []


class RiskAssessmentResponse(BaseModel):
    """Response schema for risk assessment"""
    assessment_id: UUID
    assessment_name: str
    assessment_type: str
    
    # Overall risk metrics
    overall_risk_score: Decimal
    risk_level: str  # "low", "medium", "high", "critical"
    confidence_level: Decimal
    
    # Risk category breakdown
    risk_categories: List[RiskCategory]
    
    # Issues by severity
    critical_issues: List[CriticalIssue]
    medium_issues: List[Dict[str, Any]] = []
    low_issues: List[Dict[str, Any]] = []
    
    # Recommendations
    recommendations: List[str]
    action_items: List[Dict[str, Any]] = []
    
    # Missing information
    missing_documents: List[MissingDocument]
    information_gaps: List[str] = []
    
    # Compliance status
    compliance_status: str
    regulatory_issues: List[str] = []
    required_actions: List[str] = []
    
    # Assessment metadata
    assessment_date: datetime
    assessment_completeness: Decimal
    data_quality_score: Decimal


# Document Categorization Schemas
class DocumentCategorizationRequest(BaseModel):
    """Request schema for document categorization"""
    document_id: UUID
    suggested_category: Optional[str] = None
    force_recategorization: bool = False


class DocumentCategorizationResponse(BaseModel):
    """Response schema for document categorization"""
    document_id: UUID
    predicted_category: str
    confidence: Decimal
    alternative_categories: List[Dict[str, Any]] = []
    reasoning: str
    keywords_matched: List[str] = []


# Document Comparison Schemas
class DocumentComparisonRequest(BaseModel):
    """Request schema for document comparison"""
    primary_document_id: UUID
    secondary_document_id: UUID
    comparison_type: str = "version"  # "version", "similar_docs", "template_match"
    focus_areas: List[str] = []  # Specific areas to focus comparison on
    
    @validator('comparison_type')
    def validate_comparison_type(cls, v):
        allowed = ["version", "similar_docs", "template_match"]
        if v not in allowed:
            raise ValueError(f"Comparison type must be one of: {allowed}")
        return v


class DocumentDifference(BaseModel):
    """Document difference information"""
    difference_type: str  # "addition", "deletion", "modification"
    section: str
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    risk_impact: str  # "low", "medium", "high"
    description: str


class DocumentComparisonResponse(BaseModel):
    """Response schema for document comparison"""
    comparison_id: UUID
    primary_document_id: UUID
    secondary_document_id: UUID
    
    # Comparison results
    similarity_score: Decimal
    differences_count: int
    
    # Detailed differences
    differences: List[DocumentDifference]
    high_risk_changes: List[DocumentDifference]
    
    # Summary
    comparison_summary: str
    risk_impact_score: Decimal
    compliance_impact: List[str] = []
    
    # Metadata
    comparison_date: datetime


# Search and Filtering Schemas
class DocumentSearchRequest(BaseModel):
    """Request schema for document search"""
    query: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    risk_level: Optional[str] = None
    analysis_status: Optional[str] = None
    deal_id: Optional[UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    # Advanced filters
    min_risk_score: Optional[Decimal] = None
    max_risk_score: Optional[Decimal] = None
    has_critical_issues: Optional[bool] = None
    compliance_status: Optional[str] = None
    
    # Pagination and sorting
    skip: int = 0
    limit: int = 100
    sort_by: str = "created_at"
    sort_order: str = "desc"
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed = ["created_at", "risk_score", "title", "analysis_date"]
        if v not in allowed:
            raise ValueError(f"Sort by must be one of: {allowed}")
        return v


class DocumentListResponse(BaseModel):
    """Response schema for document lists"""
    documents: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int
    has_more: bool
    
    # Aggregated statistics
    statistics: Optional[Dict[str, Any]] = None


# Batch Processing Schemas
class BatchAnalysisRequest(BaseModel):
    """Request schema for batch document analysis"""
    document_ids: List[UUID]
    analysis_type: str = "full"
    priority: str = "medium"
    notification_email: Optional[str] = None
    
    @validator('document_ids')
    def validate_document_ids(cls, v):
        if len(v) == 0:
            raise ValueError("At least one document ID is required")
        if len(v) > 100:
            raise ValueError("Maximum 100 documents can be processed in a batch")
        return v


class BatchAnalysisResponse(BaseModel):
    """Response schema for batch analysis"""
    batch_id: UUID
    total_documents: int
    estimated_completion_time: str
    status: str  # "queued", "processing", "completed", "failed"
    
    # Progress tracking
    processed_count: int = 0
    failed_count: int = 0
    success_count: int = 0
    
    # Results summary
    results_summary: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
