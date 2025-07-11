"""
Compliance schemas for API serialization
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# Compliance Category Schemas
class ComplianceCategoryBase(BaseModel):
    """Base compliance category schema"""
    name: str
    description: Optional[str] = None
    code: str
    is_active: bool = True
    priority_level: int = 1
    review_frequency_days: int = 30
    regulatory_body: Optional[str] = None
    regulation_url: Optional[str] = None


class ComplianceCategoryCreate(ComplianceCategoryBase):
    """Schema for creating a compliance category"""
    organization_id: UUID


class ComplianceCategoryUpdate(BaseModel):
    """Schema for updating a compliance category"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    priority_level: Optional[int] = None
    review_frequency_days: Optional[int] = None
    regulatory_body: Optional[str] = None
    regulation_url: Optional[str] = None


class ComplianceCategory(ComplianceCategoryBase):
    """Schema for compliance category response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    organization_id: UUID
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


# Compliance Requirement Schemas
class ComplianceRequirementBase(BaseModel):
    """Base compliance requirement schema"""
    title: str
    description: Optional[str] = None
    requirement_code: Optional[str] = None
    is_mandatory: bool = True
    risk_level: str = "medium"
    required_documents: List[str] = []
    evidence_requirements: Optional[str] = None
    review_frequency_days: int = 90


class ComplianceRequirementCreate(ComplianceRequirementBase):
    """Schema for creating a compliance requirement"""
    category_id: UUID
    organization_id: UUID
    due_date: Optional[datetime] = None


class ComplianceRequirementUpdate(BaseModel):
    """Schema for updating a compliance requirement"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirement_code: Optional[str] = None
    is_mandatory: Optional[bool] = None
    risk_level: Optional[str] = None
    required_documents: Optional[List[str]] = None
    evidence_requirements: Optional[str] = None
    due_date: Optional[datetime] = None
    review_frequency_days: Optional[int] = None
    status: Optional[str] = None
    completion_percentage: Optional[float] = None


class ComplianceRequirement(ComplianceRequirementBase):
    """Schema for compliance requirement response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    category_id: UUID
    organization_id: UUID
    due_date: Optional[datetime] = None
    last_review_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    status: str
    completion_percentage: float

    model_config = ConfigDict(from_attributes=True)


# Compliance Assessment Schemas
class ComplianceAssessmentBase(BaseModel):
    """Base compliance assessment schema"""
    assessment_type: str = "regular"
    status: str
    score: Optional[float] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    risk_level: str = "low"
    impact_assessment: Optional[str] = None
    evidence_provided: List[str] = []
    supporting_documents: List[str] = []
    action_items: List[dict] = []
    remediation_plan: Optional[str] = None


class ComplianceAssessmentCreate(ComplianceAssessmentBase):
    """Schema for creating a compliance assessment"""
    category_id: Optional[UUID] = None
    requirement_id: Optional[UUID] = None
    organization_id: UUID
    assessed_by_id: UUID
    target_completion_date: Optional[datetime] = None


class ComplianceAssessmentUpdate(BaseModel):
    """Schema for updating a compliance assessment"""
    assessment_type: Optional[str] = None
    status: Optional[str] = None
    score: Optional[float] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None
    risk_level: Optional[str] = None
    impact_assessment: Optional[str] = None
    evidence_provided: Optional[List[str]] = None
    supporting_documents: Optional[List[str]] = None
    action_items: Optional[List[dict]] = None
    remediation_plan: Optional[str] = None
    target_completion_date: Optional[datetime] = None


class ComplianceAssessment(ComplianceAssessmentBase):
    """Schema for compliance assessment response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    assessment_date: datetime
    category_id: Optional[UUID] = None
    requirement_id: Optional[UUID] = None
    organization_id: UUID
    assessed_by_id: UUID
    target_completion_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Regulatory Update Schemas
class RegulatoryUpdateBase(BaseModel):
    """Base regulatory update schema"""
    title: str
    description: Optional[str] = None
    update_type: str = "regulation_change"
    source: Optional[str] = None
    impact_level: str = "medium"
    affected_categories: List[str] = []
    content: Optional[str] = None
    source_url: Optional[str] = None
    document_references: List[str] = []


class RegulatoryUpdateCreate(RegulatoryUpdateBase):
    """Schema for creating a regulatory update"""
    organization_id: UUID
    publication_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None


class RegulatoryUpdateUpdate(BaseModel):
    """Schema for updating a regulatory update"""
    title: Optional[str] = None
    description: Optional[str] = None
    update_type: Optional[str] = None
    source: Optional[str] = None
    publication_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    impact_level: Optional[str] = None
    affected_categories: Optional[List[str]] = None
    content: Optional[str] = None
    source_url: Optional[str] = None
    document_references: Optional[List[str]] = None
    is_reviewed: Optional[bool] = None
    review_notes: Optional[str] = None


class RegulatoryUpdate(RegulatoryUpdateBase):
    """Schema for regulatory update response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    organization_id: UUID
    publication_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    is_reviewed: bool
    review_notes: Optional[str] = None
    reviewed_by_id: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Audit Log Schema
class ComplianceAuditLog(BaseModel):
    """Schema for compliance audit log response"""
    id: UUID
    created_at: datetime
    event_type: str
    event_description: Optional[str] = None
    event_timestamp: datetime
    old_values: dict
    new_values: dict
    event_metadata: dict
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    requirement_id: Optional[UUID] = None
    assessment_id: Optional[UUID] = None
    organization_id: UUID

    model_config = ConfigDict(from_attributes=True)


# Dashboard Summary Schemas
class ComplianceDashboardSummary(BaseModel):
    """Summary data for compliance dashboard"""
    total_requirements: int
    compliant_requirements: int
    warning_requirements: int
    non_compliant_requirements: int
    pending_requirements: int
    overall_compliance_score: float
    categories_summary: List[dict]
    recent_assessments: List[dict]
    upcoming_reviews: List[dict]
    regulatory_updates_count: int
    unreviewed_updates_count: int


class ComplianceCategoryWithRequirements(ComplianceCategory):
    """Compliance category with its requirements"""
    requirements: List[ComplianceRequirement] = []
    recent_assessments: List[ComplianceAssessment] = []
    compliance_score: Optional[float] = None
    requirements_count: int = 0
    compliant_count: int = 0
