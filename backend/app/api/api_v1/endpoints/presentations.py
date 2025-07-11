"""
PitchCraft Suite API endpoints for presentations
"""
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_presentation import (
    crud_presentation,
    crud_presentation_slide,
    crud_presentation_template,
    crud_presentation_comment,
    crud_presentation_collaboration
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.presentation import (
    Presentation,
    PresentationCreate,
    PresentationUpdate,
    PresentationSlide,
    PresentationSlideCreate,
    PresentationSlideUpdate,
    PresentationTemplate,
    PresentationTemplateCreate,
    PresentationTemplateUpdate,
    PresentationComment,
    PresentationCommentCreate,
    PresentationCommentUpdate
)
from app.services.export_service import export_service

router = APIRouter()


# Presentation endpoints
@router.get("/", response_model=List[Presentation])
def get_presentations(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    presentation_type: Optional[str] = Query(None),
    deal_id: Optional[UUID] = Query(None),
    created_by_me: bool = Query(False)
) -> Any:
    """
    Get presentations for the current user's organization
    """
    created_by_id = current_user.id if created_by_me else None
    
    presentations = crud_presentation.get_by_organization(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        status=status,
        presentation_type=presentation_type,
        created_by_id=created_by_id,
        deal_id=deal_id
    )
    return presentations


@router.post("/", response_model=Presentation)
def create_presentation(
    *,
    db: Session = Depends(get_db),
    presentation_in: PresentationCreate,
    current_user: User = Depends(deps.check_permission("presentations:create")),
) -> Any:
    """
    Create new presentation
    """
    # Ensure organization_id matches current user
    if presentation_in.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create presentation for different organization"
        )
    
    presentation = crud_presentation.create_with_user(
        db=db,
        obj_in=presentation_in,
        created_by_id=current_user.id
    )
    
    # Log creation activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation.id,
        user_id=current_user.id,
        activity_type="created",
        description=f"Created presentation '{presentation.title}'"
    )
    
    return presentation


@router.get("/{presentation_id}", response_model=Presentation)
def get_presentation(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get presentation by ID
    """
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check access permissions
    if (presentation.organization_id != current_user.organization_id and 
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return presentation


@router.put("/{presentation_id}", response_model=Presentation)
def update_presentation(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    presentation_in: PresentationUpdate,
    current_user: User = Depends(deps.check_permission("presentations:edit")),
) -> Any:
    """
    Update presentation
    """
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check access permissions
    if (presentation.organization_id != current_user.organization_id and 
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    presentation = crud_presentation.update_with_user(
        db=db,
        db_obj=presentation,
        obj_in=presentation_in,
        updated_by_id=current_user.id
    )
    
    # Log update activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation.id,
        user_id=current_user.id,
        activity_type="updated",
        description=f"Updated presentation '{presentation.title}'"
    )
    
    return presentation


@router.delete("/{presentation_id}")
def delete_presentation(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    current_user: User = Depends(deps.check_permission("presentations:delete")),
) -> Any:
    """
    Delete presentation
    """
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check access permissions
    if (presentation.organization_id != current_user.organization_id and 
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    crud_presentation.remove(db=db, id=presentation_id)
    
    # Log deletion activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation_id,
        user_id=current_user.id,
        activity_type="deleted",
        description=f"Deleted presentation '{presentation.title}'"
    )
    
    return {"message": "Presentation deleted successfully"}


@router.post("/{presentation_id}/version", response_model=Presentation)
def create_presentation_version(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    current_user: User = Depends(deps.check_permission("presentations:edit")),
) -> Any:
    """
    Create a new version of an existing presentation
    """
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check access permissions
    if (presentation.organization_id != current_user.organization_id and 
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    new_version = crud_presentation.create_version(
        db=db,
        presentation_id=presentation_id,
        created_by_id=current_user.id
    )
    
    if not new_version:
        raise HTTPException(status_code=400, detail="Failed to create new version")
    
    # Log version creation activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=new_version.id,
        user_id=current_user.id,
        activity_type="version_created",
        description=f"Created version {new_version.version} of presentation '{new_version.title}'"
    )
    
    return new_version


@router.get("/deals/{deal_id}", response_model=List[Presentation])
def get_presentations_by_deal(
    *,
    db: Session = Depends(get_db),
    deal_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Get presentations for a specific deal
    """
    presentations = crud_presentation.get_by_deal(
        db=db,
        deal_id=deal_id,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )
    return presentations


@router.get("/shared/", response_model=List[Presentation])
def get_shared_presentations(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Get presentations shared with the current user
    """
    presentations = crud_presentation.get_shared_presentations(
        db=db,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit
    )
    return presentations


# Slide endpoints
@router.get("/{presentation_id}/slides", response_model=List[PresentationSlide])
def get_presentation_slides(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Get slides for a presentation
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    slides = crud_presentation_slide.get_by_presentation(
        db=db,
        presentation_id=presentation_id,
        skip=skip,
        limit=limit
    )
    return slides


@router.post("/{presentation_id}/slides", response_model=PresentationSlide)
def create_slide(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    slide_in: PresentationSlideCreate,
    current_user: User = Depends(deps.check_permission("presentations:edit")),
) -> Any:
    """
    Create new slide in presentation
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Add presentation_id to slide data
    slide_data = slide_in.dict()
    slide_data["presentation_id"] = presentation_id

    slide = crud_presentation_slide.create(db=db, obj_in=slide_data)

    # Update presentation slide count
    presentation.slide_count = len(crud_presentation_slide.get_by_presentation(
        db=db, presentation_id=presentation_id
    ))
    db.commit()

    # Log activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation_id,
        user_id=current_user.id,
        activity_type="slide_created",
        description=f"Created slide '{slide.title}'"
    )

    return slide


@router.get("/{presentation_id}/slides/{slide_id}", response_model=PresentationSlide)
def get_slide(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    slide_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get specific slide
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    slide = crud_presentation_slide.get(db=db, id=slide_id)
    if not slide or slide.presentation_id != presentation_id:
        raise HTTPException(status_code=404, detail="Slide not found")

    return slide


@router.put("/{presentation_id}/slides/{slide_id}", response_model=PresentationSlide)
def update_slide(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    slide_id: UUID,
    slide_in: PresentationSlideUpdate,
    current_user: User = Depends(deps.check_permission("presentations:edit")),
) -> Any:
    """
    Update slide
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    slide = crud_presentation_slide.get(db=db, id=slide_id)
    if not slide or slide.presentation_id != presentation_id:
        raise HTTPException(status_code=404, detail="Slide not found")

    slide = crud_presentation_slide.update(db=db, db_obj=slide, obj_in=slide_in)

    # Log activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation_id,
        user_id=current_user.id,
        activity_type="slide_updated",
        description=f"Updated slide '{slide.title}'"
    )

    return slide


@router.delete("/{presentation_id}/slides/{slide_id}")
def delete_slide(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    slide_id: UUID,
    current_user: User = Depends(deps.check_permission("presentations:edit")),
) -> Any:
    """
    Delete slide
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    slide = crud_presentation_slide.get(db=db, id=slide_id)
    if not slide or slide.presentation_id != presentation_id:
        raise HTTPException(status_code=404, detail="Slide not found")

    slide_title = slide.title
    crud_presentation_slide.remove(db=db, id=slide_id)

    # Update presentation slide count
    presentation.slide_count = len(crud_presentation_slide.get_by_presentation(
        db=db, presentation_id=presentation_id
    ))
    db.commit()

    # Log activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation_id,
        user_id=current_user.id,
        activity_type="slide_deleted",
        description=f"Deleted slide '{slide_title}'"
    )

    return {"message": "Slide deleted successfully"}


@router.post("/{presentation_id}/slides/{slide_id}/duplicate", response_model=PresentationSlide)
def duplicate_slide(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    slide_id: UUID,
    new_slide_number: int = Query(..., ge=1),
    current_user: User = Depends(deps.check_permission("presentations:edit")),
) -> Any:
    """
    Duplicate a slide
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    slide = crud_presentation_slide.get(db=db, id=slide_id)
    if not slide or slide.presentation_id != presentation_id:
        raise HTTPException(status_code=404, detail="Slide not found")

    duplicate = crud_presentation_slide.duplicate_slide(
        db=db,
        slide_id=slide_id,
        new_slide_number=new_slide_number
    )

    if not duplicate:
        raise HTTPException(status_code=400, detail="Failed to duplicate slide")

    # Update presentation slide count
    presentation.slide_count = len(crud_presentation_slide.get_by_presentation(
        db=db, presentation_id=presentation_id
    ))
    db.commit()

    # Log activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation_id,
        user_id=current_user.id,
        activity_type="slide_duplicated",
        description=f"Duplicated slide '{slide.title}'"
    )

    return duplicate


# Template endpoints
@router.get("/templates/", response_model=List[PresentationTemplate])
def get_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    featured_only: bool = Query(False),
    public_only: bool = Query(False)
) -> Any:
    """
    Get presentation templates
    """
    if public_only:
        templates = crud_presentation_template.get_public_templates(
            db=db,
            skip=skip,
            limit=limit,
            category=category,
            featured_only=featured_only
        )
    else:
        templates = crud_presentation_template.get_by_organization(
            db=db,
            organization_id=current_user.organization_id,
            skip=skip,
            limit=limit,
            category=category
        )
    return templates


@router.post("/templates/", response_model=PresentationTemplate)
def create_template(
    *,
    db: Session = Depends(get_db),
    template_in: PresentationTemplateCreate,
    current_user: User = Depends(deps.check_permission("presentations:create")),
) -> Any:
    """
    Create new presentation template
    """
    # Add creator info
    template_data = template_in.dict()
    template_data["created_by_id"] = current_user.id
    if not template_data.get("organization_id"):
        template_data["organization_id"] = current_user.organization_id

    template = crud_presentation_template.create(db=db, obj_in=template_data)
    return template


@router.get("/templates/{template_id}", response_model=PresentationTemplate)
def get_template(
    *,
    db: Session = Depends(get_db),
    template_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get template by ID
    """
    template = crud_presentation_template.get(db=db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check access permissions
    if (not template.is_public and
        template.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return template


@router.post("/templates/{template_id}/use", response_model=Presentation)
def create_from_template(
    *,
    db: Session = Depends(get_db),
    template_id: UUID,
    presentation_data: dict,
    current_user: User = Depends(deps.check_permission("presentations:create")),
) -> Any:
    """
    Create presentation from template
    """
    template = crud_presentation_template.get(db=db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Check access permissions
    if (not template.is_public and
        template.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Create presentation from template
    presentation_create_data = {
        "title": presentation_data.get("title", template.name),
        "description": presentation_data.get("description", template.description),
        "presentation_type": presentation_data.get("presentation_type", "custom"),
        "content_data": template.template_data,
        "theme_settings": template.theme_settings,
        "organization_id": current_user.organization_id,
        "deal_id": presentation_data.get("deal_id")
    }

    presentation = crud_presentation.create_with_user(
        db=db,
        obj_in=PresentationCreate(**presentation_create_data),
        created_by_id=current_user.id
    )

    # Create slides from template
    for slide_template in template.default_slides:
        slide_data = {
            "title": slide_template.get("title", "Untitled Slide"),
            "slide_number": slide_template.get("slide_number", 1),
            "slide_type": slide_template.get("slide_type", "content"),
            "content_data": slide_template.get("content_data", {}),
            "layout_type": slide_template.get("layout_type", "default"),
            "presentation_id": presentation.id
        }
        crud_presentation_slide.create(db=db, obj_in=slide_data)

    # Update slide count
    presentation.slide_count = len(template.default_slides)
    db.commit()

    # Increment template usage
    crud_presentation_template.increment_usage(db=db, template_id=template_id)

    # Log activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation.id,
        user_id=current_user.id,
        activity_type="created_from_template",
        description=f"Created presentation from template '{template.name}'"
    )

    return presentation


# Comment endpoints
@router.get("/{presentation_id}/comments", response_model=List[PresentationComment])
def get_presentation_comments(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    resolved_only: Optional[bool] = Query(None)
) -> Any:
    """
    Get comments for a presentation
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    comments = crud_presentation_comment.get_by_presentation(
        db=db,
        presentation_id=presentation_id,
        skip=skip,
        limit=limit,
        resolved_only=resolved_only
    )
    return comments


@router.post("/{presentation_id}/comments", response_model=PresentationComment)
def create_comment(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    comment_in: PresentationCommentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create comment on presentation
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Add comment data
    comment_data = comment_in.dict()
    comment_data["presentation_id"] = presentation_id
    comment_data["author_id"] = current_user.id

    comment = crud_presentation_comment.create(db=db, obj_in=comment_data)

    # Log activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation_id,
        user_id=current_user.id,
        activity_type="commented",
        description=f"Added comment: {comment.content[:50]}..."
    )

    return comment


@router.put("/{presentation_id}/comments/{comment_id}/resolve")
def resolve_comment(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    comment_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Resolve a comment
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    comment = crud_presentation_comment.resolve_comment(
        db=db,
        comment_id=comment_id,
        resolved_by_id=current_user.id
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Log activity
    crud_presentation_collaboration.log_activity(
        db=db,
        presentation_id=presentation_id,
        user_id=current_user.id,
        activity_type="comment_resolved",
        description="Resolved comment"
    )

    return {"message": "Comment resolved successfully"}


# Collaboration endpoints
@router.get("/{presentation_id}/activities")
def get_presentation_activities(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> Any:
    """
    Get recent activities for a presentation
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    activities = crud_presentation_collaboration.get_recent_activities(
        db=db,
        presentation_id=presentation_id,
        skip=skip,
        limit=limit
    )
    return activities


@router.get("/{presentation_id}/active-users")
def get_active_users(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get currently active users on a presentation
    """
    # Verify presentation access
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    if (presentation.organization_id != current_user.organization_id and
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    active_users = crud_presentation_collaboration.get_active_users(
        db=db,
        presentation_id=presentation_id
    )
    return active_users


@router.get("/{presentation_id}/export/pptx")
async def export_presentation_pptx(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Export presentation to PowerPoint format
    """
    # Get the presentation
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    # Check permissions
    if presentation.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Get presentation slides
        slides = crud_presentation_slide.get_by_presentation(db=db, presentation_id=presentation_id)

        # Prepare presentation data for export
        slides_data = []
        for slide in slides:
            slide_data = {
                "title": slide.title or "",
                "content": slide.content or "",
                "type": slide.slide_type or "content",
                "charts": slide.charts or [],
                "order": slide.order_index
            }
            slides_data.append(slide_data)

        # Sort slides by order
        slides_data.sort(key=lambda x: x.get("order", 0))

        presentation_data = {
            "title": presentation.title,
            "description": presentation.description,
            "slides": slides_data,
            "created_at": presentation.created_at.strftime('%Y-%m-%d') if presentation.created_at else None,
            "updated_at": presentation.updated_at.strftime('%Y-%m-%d') if presentation.updated_at else None
        }

        # Get organization name
        organization_name = current_user.organization.name if current_user.organization else "DealVerse Organization"

        # Export to PowerPoint
        pptx_data = await export_service.export_presentation_to_pptx(
            presentation_data=presentation_data,
            presentation_id=presentation_id,
            organization_name=organization_name
        )

        from fastapi.responses import Response

        return Response(
            content=pptx_data,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": f"attachment; filename={presentation.title}_presentation.pptx"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export presentation to PowerPoint: {str(e)}"
        )


@router.get("/{presentation_id}/export/pdf")
async def export_presentation_pdf(
    *,
    db: Session = Depends(get_db),
    presentation_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Export presentation to PDF format
    """
    # Get the presentation
    presentation = crud_presentation.get(db=db, id=presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    # Check permissions
    if presentation.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Get presentation slides
        slides = crud_presentation_slide.get_by_presentation(db=db, presentation_id=presentation_id)

        # Prepare presentation data for export (reuse the financial model PDF export logic)
        slides_data = []
        for slide in slides:
            slide_data = {
                "title": slide.title or "",
                "content": slide.content or "",
                "type": slide.slide_type or "content",
                "order": slide.order_index
            }
            slides_data.append(slide_data)

        # Sort slides by order
        slides_data.sort(key=lambda x: x.get("order", 0))

        # Convert to a format similar to financial model for PDF export
        presentation_data = {
            "name": presentation.title,
            "created_at": presentation.created_at.strftime('%Y-%m-%d') if presentation.created_at else None,
            "updated_at": presentation.updated_at.strftime('%Y-%m-%d') if presentation.updated_at else None,
            "model_type": "Presentation",
            "key_metrics": {"total_slides": len(slides_data)},
            "projections": {"slides": slides_data},
            "assumptions": {"presentation_type": "PitchCraft Suite"}
        }

        # Get organization name
        organization_name = current_user.organization.name if current_user.organization else "DealVerse Organization"

        # Export to PDF using the financial model PDF export (adapted)
        pdf_data = await export_service.export_financial_model_to_pdf(
            model_data=presentation_data,
            model_id=presentation_id,
            organization_name=organization_name
        )

        from fastapi.responses import Response

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={presentation.title}_presentation.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export presentation to PDF: {str(e)}"
        )
