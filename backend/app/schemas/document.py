"""
Document schemas for API serialization
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """Base document schema"""
    title: str
    filename: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_extension: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    status: str = "uploaded"
    description: Optional[str] = None
    tags: List[str] = []
    is_confidential: bool = False
    is_archived: bool = False


class DocumentCreate(DocumentBase):
    """Schema for creating a new document"""
    organization_id: UUID
    uploaded_by_id: UUID
    deal_id: Optional[UUID] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_confidential: Optional[bool] = None
    is_archived: Optional[bool] = None
    deal_id: Optional[UUID] = None


class Document(DocumentBase):
    """Schema for document response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    organization_id: UUID
    uploaded_by_id: UUID
    deal_id: Optional[UUID] = None
    download_count: int = 0
    last_accessed: Optional[datetime] = None
    version: str = "1.0"
    is_latest_version: bool = True
    ai_analysis: Optional[dict] = None
    risk_score: Optional[str] = None
    key_findings: List[str] = []
    extracted_data: Optional[dict] = None
    compliance_status: str = "pending"
    review_status: str = "pending"
    reviewer_notes: Optional[str] = None
    keywords: List[str] = []
    access_level: str = "organization"
    allowed_roles: List[str] = []

    model_config = ConfigDict(from_attributes=True)


# Simple schemas for relationships to avoid circular imports
class UserSimple(BaseModel):
    """Simple user schema for relationships"""
    id: UUID
    first_name: str
    last_name: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class DealSimple(BaseModel):
    """Simple deal schema for relationships"""
    id: UUID
    title: str
    deal_type: Optional[str] = None
    stage: Optional[str] = None
    status: str
    deal_value: Optional[float] = None
    currency: str = "USD"

    model_config = ConfigDict(from_attributes=True)


class OrganizationSimple(BaseModel):
    """Simple organization schema for relationships"""
    id: UUID
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(Document):
    """Extended document response with relationships"""
    uploaded_by: Optional[UserSimple] = None
    deal: Optional[DealSimple] = None
    organization: Optional[OrganizationSimple] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentUpload(BaseModel):
    """Schema for document upload"""
    title: str
    document_type: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []
    is_confidential: bool = False
    deal_id: Optional[UUID] = None
