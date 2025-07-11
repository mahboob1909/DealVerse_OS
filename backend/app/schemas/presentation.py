"""
Presentation schemas for API serialization
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# Presentation Schemas
class PresentationBase(BaseModel):
    """Base presentation schema"""
    title: str
    description: Optional[str] = None
    presentation_type: str = "custom"
    slide_count: int = 0
    content_data: dict = {}
    theme_settings: dict = {}
    layout_settings: dict = {}
    is_shared: bool = False
    access_level: str = "team"
    collaborators: List[str] = []
    tags: List[str] = []
    notes: Optional[str] = None
    thumbnail_url: Optional[str] = None
    deal_value: Optional[str] = None
    client_name: Optional[str] = None
    target_audience: Optional[str] = None
    is_template: bool = False
    template_category: Optional[str] = None
    template_description: Optional[str] = None


class PresentationCreate(PresentationBase):
    """Schema for creating a presentation"""
    organization_id: UUID
    deal_id: Optional[UUID] = None
    presentation_date: Optional[datetime] = None


class PresentationUpdate(BaseModel):
    """Schema for updating a presentation"""
    title: Optional[str] = None
    description: Optional[str] = None
    presentation_type: Optional[str] = None
    status: Optional[str] = None
    content_data: Optional[dict] = None
    theme_settings: Optional[dict] = None
    layout_settings: Optional[dict] = None
    is_shared: Optional[bool] = None
    access_level: Optional[str] = None
    collaborators: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    thumbnail_url: Optional[str] = None
    deal_value: Optional[str] = None
    client_name: Optional[str] = None
    target_audience: Optional[str] = None
    presentation_date: Optional[datetime] = None


class Presentation(PresentationBase):
    """Schema for presentation response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    status: str
    version: int
    is_current: bool
    organization_id: UUID
    deal_id: Optional[UUID] = None
    created_by_id: UUID
    last_modified_by_id: Optional[UUID] = None
    parent_presentation_id: Optional[UUID] = None
    presentation_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Slide Schemas
class PresentationSlideBase(BaseModel):
    """Base slide schema"""
    title: Optional[str] = None
    slide_number: int
    slide_type: str = "content"
    content_data: dict = {}
    layout_type: str = "default"
    background_settings: dict = {}
    elements: List[dict] = []
    animations: List[dict] = []
    transitions: dict = {}
    notes: Optional[str] = None
    duration_seconds: Optional[int] = None
    is_hidden: bool = False


class PresentationSlideCreate(PresentationSlideBase):
    """Schema for creating a slide"""
    presentation_id: UUID


class PresentationSlideUpdate(BaseModel):
    """Schema for updating a slide"""
    title: Optional[str] = None
    slide_number: Optional[int] = None
    slide_type: Optional[str] = None
    content_data: Optional[dict] = None
    layout_type: Optional[str] = None
    background_settings: Optional[dict] = None
    elements: Optional[List[dict]] = None
    animations: Optional[List[dict]] = None
    transitions: Optional[dict] = None
    notes: Optional[str] = None
    duration_seconds: Optional[int] = None
    is_hidden: Optional[bool] = None


class PresentationSlide(PresentationSlideBase):
    """Schema for slide response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    presentation_id: UUID

    model_config = ConfigDict(from_attributes=True)


# Template Schemas
class PresentationTemplateBase(BaseModel):
    """Base template schema"""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    template_data: dict = {}
    default_slides: List[dict] = []
    theme_settings: dict = {}
    is_featured: bool = False
    is_public: bool = True
    thumbnail_url: Optional[str] = None
    preview_images: List[str] = []


class PresentationTemplateCreate(PresentationTemplateBase):
    """Schema for creating a template"""
    organization_id: Optional[UUID] = None


class PresentationTemplateUpdate(BaseModel):
    """Schema for updating a template"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    template_data: Optional[dict] = None
    default_slides: Optional[List[dict]] = None
    theme_settings: Optional[dict] = None
    is_featured: Optional[bool] = None
    is_public: Optional[bool] = None
    thumbnail_url: Optional[str] = None
    preview_images: Optional[List[str]] = None


class PresentationTemplate(PresentationTemplateBase):
    """Schema for template response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    usage_count: int
    organization_id: Optional[UUID] = None
    created_by_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


# Comment Schemas
class PresentationCommentBase(BaseModel):
    """Base comment schema"""
    content: str
    comment_type: str = "general"
    element_id: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None


class PresentationCommentCreate(PresentationCommentBase):
    """Schema for creating a comment"""
    presentation_id: UUID
    slide_id: Optional[UUID] = None
    parent_comment_id: Optional[UUID] = None


class PresentationCommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: Optional[str] = None
    comment_type: Optional[str] = None
    is_resolved: Optional[bool] = None


class PresentationComment(PresentationCommentBase):
    """Schema for comment response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    presentation_id: UUID
    slide_id: Optional[UUID] = None
    author_id: UUID
    parent_comment_id: Optional[UUID] = None
    is_resolved: bool
    resolved_by_id: Optional[UUID] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Dashboard and Summary Schemas
class PresentationDashboardSummary(BaseModel):
    """Summary data for presentation dashboard"""
    total_presentations: int
    active_presentations: int
    draft_presentations: int
    shared_presentations: int
    recent_presentations: List[dict]
    popular_templates: List[dict]
    collaboration_stats: dict
    upcoming_presentations: List[dict]


class PresentationWithSlides(Presentation):
    """Presentation with its slides"""
    slides: List[PresentationSlide] = []
    comments: List[PresentationComment] = []
    collaborator_count: int = 0
    last_activity: Optional[datetime] = None


class PresentationCollaborationSummary(BaseModel):
    """Collaboration summary for a presentation"""
    presentation_id: UUID
    total_collaborators: int
    active_collaborators: int
    recent_activities: List[dict]
    comments_count: int
    unresolved_comments: int
