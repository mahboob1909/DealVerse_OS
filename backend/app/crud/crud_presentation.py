"""
CRUD operations for Presentation models
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.crud.base import CRUDBase
from app.models.presentation import (
    Presentation,
    PresentationSlide,
    PresentationTemplate,
    PresentationComment,
    PresentationCollaboration,
    PresentationStatus,
    PresentationType
)
from app.schemas.presentation import (
    PresentationCreate,
    PresentationUpdate,
    PresentationSlideCreate,
    PresentationSlideUpdate,
    PresentationTemplateCreate,
    PresentationTemplateUpdate,
    PresentationCommentCreate,
    PresentationCommentUpdate
)


class CRUDPresentation(CRUDBase[Presentation, PresentationCreate, PresentationUpdate]):
    """CRUD operations for Presentation"""
    
    def get_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        presentation_type: Optional[str] = None,
        created_by_id: Optional[UUID] = None,
        deal_id: Optional[UUID] = None
    ) -> List[Presentation]:
        """Get presentations by organization with optional filters"""
        query = db.query(Presentation).filter(
            Presentation.organization_id == organization_id,
            Presentation.is_current == True  # Only get current versions
        )
        
        if status:
            query = query.filter(Presentation.status == status)
        if presentation_type:
            query = query.filter(Presentation.presentation_type == presentation_type)
        if created_by_id:
            query = query.filter(Presentation.created_by_id == created_by_id)
        if deal_id:
            query = query.filter(Presentation.deal_id == deal_id)
        
        return query.order_by(desc(Presentation.updated_at)).offset(skip).limit(limit).all()
    
    def get_by_deal(
        self,
        db: Session,
        *,
        deal_id: UUID,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Presentation]:
        """Get presentations by deal"""
        return db.query(Presentation).filter(
            and_(
                Presentation.deal_id == deal_id,
                Presentation.organization_id == organization_id,
                Presentation.is_current == True
            )
        ).order_by(desc(Presentation.updated_at)).offset(skip).limit(limit).all()
    
    def get_shared_presentations(
        self,
        db: Session,
        *,
        user_id: UUID,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Presentation]:
        """Get presentations shared with user"""
        return db.query(Presentation).filter(
            and_(
                Presentation.organization_id == organization_id,
                Presentation.is_shared == True,
                Presentation.is_current == True,
                or_(
                    Presentation.collaborators.contains([str(user_id)]),
                    Presentation.access_level.in_(["team", "organization", "public"])
                )
            )
        ).order_by(desc(Presentation.updated_at)).offset(skip).limit(limit).all()
    
    def create_with_user(
        self,
        db: Session,
        *,
        obj_in: PresentationCreate,
        created_by_id: UUID
    ) -> Presentation:
        """Create presentation with user context"""
        obj_in_data = obj_in.dict()
        obj_in_data["created_by_id"] = created_by_id
        obj_in_data["last_modified_by_id"] = created_by_id
        
        db_obj = Presentation(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_with_user(
        self,
        db: Session,
        *,
        db_obj: Presentation,
        obj_in: PresentationUpdate,
        updated_by_id: UUID
    ) -> Presentation:
        """Update presentation with user context"""
        update_data = obj_in.dict(exclude_unset=True)
        update_data["last_modified_by_id"] = updated_by_id
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_version(
        self,
        db: Session,
        *,
        presentation_id: UUID,
        created_by_id: UUID
    ) -> Presentation:
        """Create a new version of an existing presentation"""
        # Get the current presentation
        current_presentation = db.query(Presentation).filter(
            Presentation.id == presentation_id
        ).first()
        
        if not current_presentation:
            return None
        
        # Mark current presentation as not current
        current_presentation.is_current = False
        
        # Create new version
        new_version_data = {
            "title": current_presentation.title,
            "description": current_presentation.description,
            "presentation_type": current_presentation.presentation_type,
            "content_data": current_presentation.content_data,
            "theme_settings": current_presentation.theme_settings,
            "layout_settings": current_presentation.layout_settings,
            "is_shared": current_presentation.is_shared,
            "access_level": current_presentation.access_level,
            "collaborators": current_presentation.collaborators,
            "tags": current_presentation.tags,
            "notes": current_presentation.notes,
            "deal_value": current_presentation.deal_value,
            "client_name": current_presentation.client_name,
            "target_audience": current_presentation.target_audience,
            "presentation_date": current_presentation.presentation_date,
            "organization_id": current_presentation.organization_id,
            "deal_id": current_presentation.deal_id,
            "created_by_id": created_by_id,
            "last_modified_by_id": created_by_id,
            "parent_presentation_id": current_presentation.id,
            "version": current_presentation.version + 1,
            "status": PresentationStatus.DRAFT
        }
        
        new_presentation = Presentation(**new_version_data)
        db.add(new_presentation)
        db.commit()
        db.refresh(new_presentation)
        
        return new_presentation


class CRUDPresentationSlide(CRUDBase[PresentationSlide, PresentationSlideCreate, PresentationSlideUpdate]):
    """CRUD operations for PresentationSlide"""
    
    def get_by_presentation(
        self,
        db: Session,
        *,
        presentation_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PresentationSlide]:
        """Get slides by presentation"""
        return db.query(PresentationSlide).filter(
            PresentationSlide.presentation_id == presentation_id
        ).order_by(PresentationSlide.slide_number).offset(skip).limit(limit).all()
    
    def reorder_slides(
        self,
        db: Session,
        *,
        presentation_id: UUID,
        slide_orders: List[Dict[str, Any]]
    ) -> List[PresentationSlide]:
        """Reorder slides in a presentation"""
        slides = []
        for order_data in slide_orders:
            slide = db.query(PresentationSlide).filter(
                and_(
                    PresentationSlide.id == order_data["slide_id"],
                    PresentationSlide.presentation_id == presentation_id
                )
            ).first()
            
            if slide:
                slide.slide_number = order_data["slide_number"]
                slides.append(slide)
        
        db.commit()
        for slide in slides:
            db.refresh(slide)
        
        return slides
    
    def duplicate_slide(
        self,
        db: Session,
        *,
        slide_id: UUID,
        new_slide_number: int
    ) -> Optional[PresentationSlide]:
        """Duplicate a slide"""
        original_slide = db.query(PresentationSlide).filter(
            PresentationSlide.id == slide_id
        ).first()
        
        if not original_slide:
            return None
        
        # Shift existing slides
        db.query(PresentationSlide).filter(
            and_(
                PresentationSlide.presentation_id == original_slide.presentation_id,
                PresentationSlide.slide_number >= new_slide_number
            )
        ).update({"slide_number": PresentationSlide.slide_number + 1})
        
        # Create duplicate
        duplicate_data = {
            "title": f"{original_slide.title} (Copy)",
            "slide_number": new_slide_number,
            "slide_type": original_slide.slide_type,
            "content_data": original_slide.content_data,
            "layout_type": original_slide.layout_type,
            "background_settings": original_slide.background_settings,
            "elements": original_slide.elements,
            "animations": original_slide.animations,
            "transitions": original_slide.transitions,
            "notes": original_slide.notes,
            "duration_seconds": original_slide.duration_seconds,
            "presentation_id": original_slide.presentation_id
        }
        
        duplicate_slide = PresentationSlide(**duplicate_data)
        db.add(duplicate_slide)
        db.commit()
        db.refresh(duplicate_slide)
        
        return duplicate_slide



class CRUDPresentationTemplate(CRUDBase[PresentationTemplate, PresentationTemplateCreate, PresentationTemplateUpdate]):
    """CRUD operations for PresentationTemplate"""

    def get_public_templates(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        featured_only: bool = False
    ) -> List[PresentationTemplate]:
        """Get public templates"""
        query = db.query(PresentationTemplate).filter(
            PresentationTemplate.is_public == True
        )

        if category:
            query = query.filter(PresentationTemplate.category == category)
        if featured_only:
            query = query.filter(PresentationTemplate.is_featured == True)

        return query.order_by(
            desc(PresentationTemplate.is_featured),
            desc(PresentationTemplate.usage_count)
        ).offset(skip).limit(limit).all()

    def get_by_organization(
        self,
        db: Session,
        *,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None
    ) -> List[PresentationTemplate]:
        """Get templates by organization"""
        query = db.query(PresentationTemplate).filter(
            or_(
                PresentationTemplate.organization_id == organization_id,
                PresentationTemplate.is_public == True
            )
        )

        if category:
            query = query.filter(PresentationTemplate.category == category)

        return query.order_by(
            desc(PresentationTemplate.is_featured),
            desc(PresentationTemplate.usage_count)
        ).offset(skip).limit(limit).all()

    def increment_usage(
        self,
        db: Session,
        *,
        template_id: UUID
    ) -> Optional[PresentationTemplate]:
        """Increment template usage count"""
        template = db.query(PresentationTemplate).filter(
            PresentationTemplate.id == template_id
        ).first()

        if template:
            template.usage_count += 1
            db.commit()
            db.refresh(template)

        return template


class CRUDPresentationComment(CRUDBase[PresentationComment, PresentationCommentCreate, PresentationCommentUpdate]):
    """CRUD operations for PresentationComment"""

    def get_by_presentation(
        self,
        db: Session,
        *,
        presentation_id: UUID,
        skip: int = 0,
        limit: int = 100,
        resolved_only: Optional[bool] = None
    ) -> List[PresentationComment]:
        """Get comments by presentation"""
        query = db.query(PresentationComment).filter(
            PresentationComment.presentation_id == presentation_id,
            PresentationComment.parent_comment_id.is_(None)  # Only top-level comments
        )

        if resolved_only is not None:
            query = query.filter(PresentationComment.is_resolved == resolved_only)

        return query.order_by(desc(PresentationComment.created_at)).offset(skip).limit(limit).all()

    def get_by_slide(
        self,
        db: Session,
        *,
        slide_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PresentationComment]:
        """Get comments by slide"""
        return db.query(PresentationComment).filter(
            PresentationComment.slide_id == slide_id,
            PresentationComment.parent_comment_id.is_(None)
        ).order_by(desc(PresentationComment.created_at)).offset(skip).limit(limit).all()

    def resolve_comment(
        self,
        db: Session,
        *,
        comment_id: UUID,
        resolved_by_id: UUID
    ) -> Optional[PresentationComment]:
        """Resolve a comment"""
        from datetime import datetime

        comment = db.query(PresentationComment).filter(
            PresentationComment.id == comment_id
        ).first()

        if comment:
            comment.is_resolved = True
            comment.resolved_by_id = resolved_by_id
            comment.resolved_at = datetime.utcnow()
            db.commit()
            db.refresh(comment)

        return comment


class CRUDPresentationCollaboration(CRUDBase[PresentationCollaboration, dict, dict]):
    """CRUD operations for PresentationCollaboration"""

    def log_activity(
        self,
        db: Session,
        *,
        presentation_id: UUID,
        user_id: UUID,
        activity_type: str,
        description: str = None,
        activity_data: dict = None
    ) -> PresentationCollaboration:
        """Log collaboration activity"""
        activity = PresentationCollaboration(
            presentation_id=presentation_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            activity_data=activity_data or {}
        )

        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    def get_recent_activities(
        self,
        db: Session,
        *,
        presentation_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[PresentationCollaboration]:
        """Get recent activities for a presentation"""
        return db.query(PresentationCollaboration).filter(
            PresentationCollaboration.presentation_id == presentation_id
        ).order_by(desc(PresentationCollaboration.created_at)).offset(skip).limit(limit).all()

    def get_active_users(
        self,
        db: Session,
        *,
        presentation_id: UUID
    ) -> List[PresentationCollaboration]:
        """Get currently active users on a presentation"""
        return db.query(PresentationCollaboration).filter(
            and_(
                PresentationCollaboration.presentation_id == presentation_id,
                PresentationCollaboration.is_active == True
            )
        ).all()


# Create CRUD instances
crud_presentation = CRUDPresentation(Presentation)
crud_presentation_slide = CRUDPresentationSlide(PresentationSlide)
crud_presentation_template = CRUDPresentationTemplate(PresentationTemplate)
crud_presentation_comment = CRUDPresentationComment(PresentationComment)
crud_presentation_collaboration = CRUDPresentationCollaboration(PresentationCollaboration)
