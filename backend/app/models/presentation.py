"""
Presentation models for PitchCraft Suite
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Boolean, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import BaseModel


class PresentationStatus(str, enum.Enum):
    """Presentation status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    REVIEW = "review"
    APPROVED = "approved"
    ARCHIVED = "archived"


class PresentationType(str, enum.Enum):
    """Presentation type enumeration"""
    INVESTMENT_PITCH = "investment_pitch"
    MARKET_RESEARCH = "market_research"
    FINANCIAL_ANALYSIS = "financial_analysis"
    DUE_DILIGENCE = "due_diligence"
    COMPLIANCE_REPORT = "compliance_report"
    CUSTOM = "custom"


class Presentation(BaseModel):
    """Main presentation model"""
    
    __tablename__ = "presentations"
    
    # Basic information
    title = Column(String(500), nullable=False)
    description = Column(Text)
    presentation_type = Column(Enum(PresentationType), default=PresentationType.CUSTOM)
    
    # Status and versioning
    status = Column(Enum(PresentationStatus), default=PresentationStatus.DRAFT)
    version = Column(Integer, default=1)
    is_current = Column(Boolean, default=True)
    parent_presentation_id = Column(UUID(as_uuid=True), ForeignKey("presentations.id"))
    
    # Content and structure
    slide_count = Column(Integer, default=0)
    content_data = Column(JSON, default=dict)  # Presentation structure and content
    theme_settings = Column(JSON, default=dict)  # Theme, colors, fonts
    layout_settings = Column(JSON, default=dict)  # Layout preferences
    
    # Collaboration and sharing
    is_shared = Column(Boolean, default=False)
    access_level = Column(String(50), default="team")  # private, team, organization, public
    collaborators = Column(JSON, default=list)  # List of user IDs with access
    
    # Presentation metadata
    tags = Column(JSON, default=list)
    notes = Column(Text)
    thumbnail_url = Column(String(500))
    
    # Business context
    deal_value = Column(String(100))  # e.g., "$45M"
    client_name = Column(String(255))
    target_audience = Column(String(255))
    presentation_date = Column(DateTime)
    
    # Template information
    is_template = Column(Boolean, default=False)
    template_category = Column(String(100))
    template_description = Column(Text)
    
    # Organization and relationships
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="presentations")
    
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"))
    deal = relationship("Deal", back_populates="presentations")
    
    # User relationships
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_presentations")
    
    last_modified_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    last_modified_by = relationship("User", foreign_keys=[last_modified_by_id])
    
    # Version relationships
    parent_presentation = relationship("Presentation", remote_side="Presentation.id")
    child_presentations = relationship("Presentation", back_populates="parent_presentation")
    
    # Related entities
    slides = relationship("PresentationSlide", back_populates="presentation", cascade="all, delete-orphan")
    comments = relationship("PresentationComment", back_populates="presentation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Presentation(id={self.id}, title='{self.title}', type='{self.presentation_type}', status='{self.status}')>"


class PresentationSlide(BaseModel):
    """Individual slides within a presentation"""
    
    __tablename__ = "presentation_slides"
    
    # Basic information
    title = Column(String(500))
    slide_number = Column(Integer, nullable=False)
    slide_type = Column(String(50), default="content")  # title, content, chart, image, etc.
    
    # Content
    content_data = Column(JSON, default=dict)  # Slide content structure
    layout_type = Column(String(50), default="default")  # Layout template
    background_settings = Column(JSON, default=dict)  # Background, colors, etc.
    
    # Positioning and styling
    elements = Column(JSON, default=list)  # Text boxes, images, charts, etc.
    animations = Column(JSON, default=list)  # Slide animations
    transitions = Column(JSON, default=dict)  # Transition effects
    
    # Metadata
    notes = Column(Text)  # Speaker notes
    duration_seconds = Column(Integer)  # Expected slide duration
    is_hidden = Column(Boolean, default=False)
    
    # Relationships
    presentation_id = Column(UUID(as_uuid=True), ForeignKey("presentations.id"), nullable=False)
    presentation = relationship("Presentation", back_populates="slides")
    
    def __repr__(self):
        return f"<PresentationSlide(id={self.id}, number={self.slide_number}, title='{self.title}')>"


class PresentationTemplate(BaseModel):
    """Presentation templates for quick creation"""
    
    __tablename__ = "presentation_templates"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # Investment, Research, Analysis, etc.
    
    # Template content
    template_data = Column(JSON, default=dict)  # Template structure
    default_slides = Column(JSON, default=list)  # Default slide templates
    theme_settings = Column(JSON, default=dict)  # Default theme
    
    # Usage and popularity
    usage_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Preview
    thumbnail_url = Column(String(500))
    preview_images = Column(JSON, default=list)  # Preview slide images
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    organization = relationship("Organization")
    
    # Creator
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<PresentationTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"


class PresentationComment(BaseModel):
    """Comments and feedback on presentations"""
    
    __tablename__ = "presentation_comments"
    
    # Comment content
    content = Column(Text, nullable=False)
    comment_type = Column(String(50), default="general")  # general, suggestion, approval, etc.
    
    # Context
    slide_id = Column(UUID(as_uuid=True), ForeignKey("presentation_slides.id"))
    slide = relationship("PresentationSlide")
    
    element_id = Column(String(100))  # Specific element on slide
    position_x = Column(Float)  # X coordinate for positioned comments
    position_y = Column(Float)  # Y coordinate for positioned comments
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    resolved_at = Column(DateTime)
    
    # Relationships
    presentation_id = Column(UUID(as_uuid=True), ForeignKey("presentations.id"), nullable=False)
    presentation = relationship("Presentation", back_populates="comments")
    
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    author = relationship("User", foreign_keys=[author_id])
    
    # Threading
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("presentation_comments.id"))
    parent_comment = relationship("PresentationComment", remote_side="PresentationComment.id")
    replies = relationship("PresentationComment", back_populates="parent_comment")
    
    def __repr__(self):
        return f"<PresentationComment(id={self.id}, type='{self.comment_type}', resolved={self.is_resolved})>"


class PresentationCollaboration(BaseModel):
    """Track collaboration activities on presentations"""
    
    __tablename__ = "presentation_collaborations"
    
    # Activity information
    activity_type = Column(String(50), nullable=False)  # created, edited, commented, shared, etc.
    description = Column(Text)
    activity_data = Column(JSON, default=dict)  # Specific activity details
    
    # Session information
    session_duration = Column(Integer)  # Duration in minutes
    is_active = Column(Boolean, default=False)  # Is user currently active
    
    # Relationships
    presentation_id = Column(UUID(as_uuid=True), ForeignKey("presentations.id"), nullable=False)
    presentation = relationship("Presentation")
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    def __repr__(self):
        return f"<PresentationCollaboration(id={self.id}, activity='{self.activity_type}', presentation_id={self.presentation_id})>"


# Add relationships to existing models
def add_presentation_relationships():
    """Add relationships to existing models"""
    from app.models.organization import Organization
    from app.models.deal import Deal
    from app.models.user import User
    
    # Add to Organization model
    if not hasattr(Organization, 'presentations'):
        Organization.presentations = relationship("Presentation", back_populates="organization")
    
    # Add to Deal model
    if not hasattr(Deal, 'presentations'):
        Deal.presentations = relationship("Presentation", back_populates="deal")
    
    # Add to User model
    if not hasattr(User, 'created_presentations'):
        User.created_presentations = relationship("Presentation", foreign_keys="Presentation.created_by_id", back_populates="created_by")
