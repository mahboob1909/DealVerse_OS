"""
Financial model management endpoints
"""
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_financial_model import crud_financial_model
from app.db.database import get_db
from app.models.user import User
from app.schemas.financial_model import FinancialModel, FinancialModelCreate, FinancialModelUpdate, FinancialModelResponse
from app.schemas.financial_ai import (
    FinancialAIAnalysisRequest,
    FinancialAIAnalysisResponse,
    ModelOptimizationRequest,
    ModelOptimizationResponse,
    ScenarioAnalysisRequest,
    ScenarioAnalysisResponse,
    ModelValidationRequest,
    ModelValidationResponse
)
from app.services.financial_model_ai import financial_model_ai_service
from app.services.export_service import export_service

router = APIRouter()


@router.get("/", response_model=List[FinancialModelResponse])
def read_financial_models(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    model_type: str = Query(None, description="Filter by model type"),
    deal_id: UUID = Query(None, description="Filter by deal"),
    status: str = Query(None, description="Filter by status"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve financial models for the current user's organization
    """
    models = crud_financial_model.get_by_organization(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        model_type=model_type,
        deal_id=deal_id,
        status=status
    )
    return models


@router.post("/", response_model=FinancialModelResponse)
def create_financial_model(
    *,
    db: Session = Depends(get_db),
    model_in: FinancialModelCreate,
    current_user: User = Depends(deps.check_permission("models:create")),
) -> Any:
    """
    Create new financial model
    """
    # Add organization and creator info
    model_data = model_in.dict()
    model_data["organization_id"] = current_user.organization_id
    model_data["created_by_id"] = current_user.id
    
    model = crud_financial_model.create(db=db, obj_in=model_data)
    return model


@router.get("/statistics", response_model=dict)
def get_model_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Get financial model statistics for the organization"""
    stats = crud_financial_model.get_model_statistics(db, organization_id=current_user.organization_id)
    return stats


@router.get("/{model_id}", response_model=FinancialModelResponse)
def read_financial_model(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get financial model by ID
    """
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")
    
    # Check if user has access to this model's organization
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check access level
    if not crud_financial_model.check_user_access(model, current_user):
        raise HTTPException(status_code=403, detail="Access denied to this model")
    
    return model


@router.put("/{model_id}", response_model=FinancialModelResponse)
def update_financial_model(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    model_in: FinancialModelUpdate,
    current_user: User = Depends(deps.check_permission("models:edit")),
) -> Any:
    """
    Update financial model
    """
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")
    
    # Check if user has access to this model's organization
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if user can edit this model
    if not crud_financial_model.check_user_access(model, current_user, action="edit"):
        raise HTTPException(status_code=403, detail="Cannot edit this model")
    
    model = crud_financial_model.update(db=db, db_obj=model, obj_in=model_in)
    return model


@router.delete("/{model_id}")
def delete_financial_model(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    current_user: User = Depends(deps.check_permission("models:delete")),
) -> Any:
    """
    Delete financial model
    """
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")
    
    # Check if user has access to this model's organization
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Only creator or admin can delete
    if model.created_by_id != current_user.id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Cannot delete this model")
    
    model = crud_financial_model.remove(db=db, id=model_id)
    return {"message": "Financial model deleted successfully"}


@router.post("/{model_id}/share")
def share_financial_model(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    user_ids: List[UUID],
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Share financial model with other users
    """
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")
    
    # Check if user has access to this model's organization
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Only creator or admin can share
    if model.created_by_id != current_user.id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Cannot share this model")
    
    # Add users to collaborators list
    collaborators = model.collaborators or []
    for user_id in user_ids:
        if str(user_id) not in collaborators:
            collaborators.append(str(user_id))
    
    model.collaborators = collaborators
    model.is_shared = True
    db.add(model)
    db.commit()
    db.refresh(model)
    
    return {"message": "Model shared successfully", "collaborators": collaborators}


@router.post("/{model_id}/version")
def create_model_version(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    current_user: User = Depends(deps.check_permission("models:create")),
) -> Any:
    """
    Create a new version of the financial model
    """
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")
    
    # Check if user has access to this model's organization
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Create new version
    new_version = crud_financial_model.create_version(db, model=model, user=current_user)
    return new_version


@router.get("/{model_id}/versions")
def get_model_versions(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all versions of a financial model
    """
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")
    
    # Check if user has access to this model's organization
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    versions = crud_financial_model.get_model_versions(db, model_id=model_id)
    return versions


# AI Analysis Endpoints

@router.post("/analyze", response_model=FinancialAIAnalysisResponse)
async def analyze_financial_model_ai(
    *,
    analysis_request: FinancialAIAnalysisRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    AI-powered analysis of financial models

    Provides comprehensive analysis including:
    - Model structure validation
    - Assumption reasonableness assessment
    - Optimization recommendations
    - Scenario suggestions
    - Risk assessment
    """
    try:
        # Perform AI analysis
        analysis_result = await financial_model_ai_service.analyze_financial_model(analysis_request)
        return analysis_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )


@router.post("/{model_id}/analyze", response_model=FinancialAIAnalysisResponse)
async def analyze_specific_model(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    analysis_type: str = Query("comprehensive", description="Type of analysis to perform"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    AI analysis of a specific financial model by ID
    """
    # Get the model
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")

    # Check permissions
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Create analysis request
        analysis_request = FinancialAIAnalysisRequest(
            model_id=model_id,
            model_data={
                "model_type": model.model_type,
                "model_data": model.model_data,
                "assumptions": model.assumptions,
                "inputs": model.inputs,
                "outputs": model.outputs,
                "scenarios": model.scenarios if hasattr(model, 'scenarios') else [],
                "sensitivity_analysis": model.sensitivity_analysis
            },
            analysis_type=analysis_type,
            include_suggestions=True,
            include_validation=True,
            include_scenarios=True
        )

        # Perform AI analysis
        analysis_result = await financial_model_ai_service.analyze_financial_model(analysis_request)
        return analysis_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )


@router.post("/{model_id}/optimize", response_model=ModelOptimizationResponse)
async def optimize_financial_model(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    optimization_request: ModelOptimizationRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get AI-powered optimization suggestions for a financial model
    """
    # Get the model
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")

    # Check permissions
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Ensure model_id matches
        optimization_request.model_id = model_id

        # Get optimization suggestions
        optimization_result = await financial_model_ai_service.optimize_model(optimization_request)
        return optimization_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model optimization failed: {str(e)}"
        )


@router.get("/ai/status")
async def get_ai_service_status(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the status of the financial model AI service
    """
    try:
        status_info = financial_model_ai_service.get_service_status()
        return status_info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI service status: {str(e)}"
        )


@router.get("/{model_id}/export/excel")
async def export_financial_model_excel(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Export financial model to Excel format
    """
    # Get the financial model
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")

    # Check permissions
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Prepare model data for export
        model_data = {
            "name": model.name,
            "created_at": model.created_at.strftime('%Y-%m-%d') if model.created_at else None,
            "updated_at": model.updated_at.strftime('%Y-%m-%d') if model.updated_at else None,
            "model_type": model.model_type,
            "key_metrics": model.key_metrics or {},
            "projections": model.projections or {},
            "assumptions": model.assumptions or {}
        }

        # Get organization name
        organization_name = current_user.organization.name if current_user.organization else "DealVerse Organization"

        # Export to Excel
        excel_data = await export_service.export_financial_model_to_excel(
            model_data=model_data,
            model_id=model_id,
            organization_name=organization_name
        )

        from fastapi.responses import Response

        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={model.name}_financial_model.xlsx"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export financial model to Excel: {str(e)}"
        )


@router.get("/{model_id}/export/pdf")
async def export_financial_model_pdf(
    *,
    db: Session = Depends(get_db),
    model_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Export financial model to PDF format
    """
    # Get the financial model
    model = crud_financial_model.get(db=db, id=model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Financial model not found")

    # Check permissions
    if model.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        # Prepare model data for export
        model_data = {
            "name": model.name,
            "created_at": model.created_at.strftime('%Y-%m-%d') if model.created_at else None,
            "updated_at": model.updated_at.strftime('%Y-%m-%d') if model.updated_at else None,
            "model_type": model.model_type,
            "key_metrics": model.key_metrics or {},
            "projections": model.projections or {},
            "assumptions": model.assumptions or {}
        }

        # Get organization name
        organization_name = current_user.organization.name if current_user.organization else "DealVerse Organization"

        # Export to PDF
        pdf_data = await export_service.export_financial_model_to_pdf(
            model_data=model_data,
            model_id=model_id,
            organization_name=organization_name
        )

        from fastapi.responses import Response

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={model.name}_financial_model.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export financial model to PDF: {str(e)}"
        )
