"""
Document model for file management and due diligence
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Document(BaseModel):
    """Document model for file storage and management"""
    
    __tablename__ = "documents"
    
    # Basic document information
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # S3 path or local path
    file_size = Column(Integer)  # Size in bytes
    file_type = Column(String(100))  # MIME type
    file_extension = Column(String(10))
    
    # Document categorization
    document_type = Column(String(100))  # financial, legal, operational, marketing, etc.
    category = Column(String(100))
    subcategory = Column(String(100))
    
    # Document status
    status = Column(String(50), default="uploaded")  # uploaded, processing, analyzed, approved, rejected
    is_confidential = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    
    # Version control
    version = Column(String(20), default="1.0")
    is_latest_version = Column(Boolean, default=True)
    parent_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    
    # AI Analysis results
    ai_analysis = Column(JSON, default=dict)  # AI analysis results
    risk_score = Column(String(3))  # 0-100 risk score
    key_findings = Column(JSON, default=list)
    extracted_data = Column(JSON, default=dict)

    # Enhanced processing results
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    document_metadata = Column(JSON, default=dict)  # Enhanced metadata from processing
    text_analysis = Column(JSON, default=dict)  # Text analysis results
    search_keywords = Column(JSON, default=list)  # Extracted keywords for search

    # Processing artifacts paths
    thumbnail_path = Column(String(500))  # S3 path to thumbnail
    extracted_text_path = Column(String(500))  # S3 path to extracted text
    search_index_path = Column(String(500))  # S3 path to search index
    
    # Compliance and review
    compliance_status = Column(String(50), default="pending")  # pending, compliant, non_compliant, review_required
    review_status = Column(String(50), default="pending")  # pending, approved, rejected, needs_revision
    reviewer_notes = Column(Text)
    
    # Metadata
    description = Column(Text)
    tags = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    
    # Access control
    access_level = Column(String(50), default="organization")  # public, organization, deal_team, restricted
    allowed_roles = Column(JSON, default=list)
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="documents")
    
    # Deal relationship (optional)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"))
    deal = relationship("Deal", back_populates="documents")
    
    # Client relationship (optional)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    client = relationship("Client", back_populates="documents")
    
    # User relationship (uploader)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploaded_by = relationship("User", back_populates="created_documents")
    
    # Version relationships
    parent_document = relationship("Document", remote_side="Document.id")
    child_documents = relationship("Document", back_populates="parent_document")

    # Analysis relationships
    analyses = relationship("DocumentAnalysis", back_populates="document")
    reviews = relationship("DocumentReview", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', type='{self.document_type}', status='{self.status}')>"

    # Database indexes for performance optimization
    __table_args__ = (
        # Single column indexes for frequently queried fields
        Index('idx_documents_organization_id', 'organization_id'),
        Index('idx_documents_deal_id', 'deal_id'),
        Index('idx_documents_client_id', 'client_id'),
        Index('idx_documents_uploaded_by_id', 'uploaded_by_id'),
        Index('idx_documents_document_type', 'document_type'),
        Index('idx_documents_category', 'category'),
        Index('idx_documents_status', 'status'),
        Index('idx_documents_processing_status', 'processing_status'),
        Index('idx_documents_compliance_status', 'compliance_status'),
        Index('idx_documents_review_status', 'review_status'),
        Index('idx_documents_is_confidential', 'is_confidential'),
        Index('idx_documents_is_archived', 'is_archived'),
        Index('idx_documents_is_latest_version', 'is_latest_version'),
        Index('idx_documents_created_at', 'created_at'),
        Index('idx_documents_updated_at', 'updated_at'),
        Index('idx_documents_file_type', 'file_type'),
        Index('idx_documents_file_extension', 'file_extension'),

        # Composite indexes for common query patterns
        Index('idx_documents_org_type', 'organization_id', 'document_type'),
        Index('idx_documents_org_status', 'organization_id', 'status'),
        Index('idx_documents_org_archived', 'organization_id', 'is_archived'),
        Index('idx_documents_org_created', 'organization_id', 'created_at'),
        Index('idx_documents_deal_type', 'deal_id', 'document_type'),
        Index('idx_documents_deal_status', 'deal_id', 'status'),
        Index('idx_documents_client_type', 'client_id', 'document_type'),
        Index('idx_documents_type_status', 'document_type', 'status'),
        Index('idx_documents_org_type_status', 'organization_id', 'document_type', 'status'),

        # Indexes for search and filtering
        Index('idx_documents_title', 'title'),
        Index('idx_documents_filename', 'filename'),
        Index('idx_documents_org_title', 'organization_id', 'title'),
        Index('idx_documents_category_subcategory', 'category', 'subcategory'),

        # Indexes for compliance and review workflows
        Index('idx_documents_compliance_review', 'compliance_status', 'review_status'),
        Index('idx_documents_org_compliance', 'organization_id', 'compliance_status'),
        Index('idx_documents_processing_compliance', 'processing_status', 'compliance_status'),

        # Indexes for version control
        Index('idx_documents_parent_version', 'parent_document_id', 'is_latest_version'),
        Index('idx_documents_version_latest', 'version', 'is_latest_version'),

        # Indexes for file management
        Index('idx_documents_file_size', 'file_size'),
        Index('idx_documents_type_size', 'file_type', 'file_size'),
    )
