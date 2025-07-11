"""
Prospect AI API endpoints
"""
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_prospect import crud_prospect, crud_prospect_analysis
from app.models.user import User
from app.db.database import get_db
from app.schemas.prospect import (
    ProspectCreate,
    ProspectUpdate,
    ProspectResponse,
    ProspectListResponse,
    ProspectSearchRequest,
    ProspectAnalysisRequest,
    ProspectAnalysisResponse,
    ProspectScoringRequest,
    ProspectScoringResponse,
    MarketIntelligenceRequest,
    MarketIntelligenceResponse
)
from app.services.prospect_ai import prospect_ai_service

router = APIRouter()


@router.get("/", response_model=ProspectListResponse)
def get_prospects(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    query: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    min_revenue: Optional[float] = Query(None),
    max_revenue: Optional[float] = Query(None),
    min_ai_score: Optional[float] = Query(None),
    status: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to_id: Optional[UUID] = Query(None),
    sort_by: str = Query("ai_score"),
    sort_order: str = Query("desc")
) -> Any:
    """
    Get prospects for the current user's organization
    """
    # Create search filters
    filters = ProspectSearchRequest(
        query=query,
        industry=industry,
        location=location,
        min_revenue=min_revenue,
        max_revenue=max_revenue,
        min_ai_score=min_ai_score,
        status=status,
        stage=stage,
        priority=priority,
        assigned_to_id=assigned_to_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Get prospects
    prospects = crud_prospect.get_by_organization(
        db=db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    # Get total count
    total = crud_prospect.count_by_organization(
        db=db,
        organization_id=current_user.organization_id,
        filters=filters
    )
    
    return ProspectListResponse(
        prospects=prospects,
        total=total,
        skip=skip,
        limit=limit,
        has_more=total > skip + len(prospects)
    )


@router.post("/", response_model=ProspectResponse)
def create_prospect(
    *,
    db: Session = Depends(get_db),
    prospect_in: ProspectCreate,
    current_user: User = Depends(deps.check_permission("prospects:create")),
) -> Any:
    """
    Create new prospect
    """
    # Check if prospect already exists
    existing_prospect = crud_prospect.get_by_company_name(
        db=db,
        company_name=prospect_in.company_name,
        organization_id=current_user.organization_id
    )
    
    if existing_prospect:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prospect with this company name already exists"
        )
    
    # Add organization and creator info
    prospect_data = prospect_in.dict()
    prospect_data["organization_id"] = current_user.organization_id
    prospect_data["created_by_id"] = current_user.id
    
    prospect = crud_prospect.create(db=db, obj_in=prospect_data)
    return prospect


@router.get("/{prospect_id}", response_model=ProspectResponse)
def get_prospect(
    *,
    db: Session = Depends(get_db),
    prospect_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get prospect by ID
    """
    prospect = crud_prospect.get(db=db, id=prospect_id)
    
    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found"
        )
    
    # Check organization access
    if prospect.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return prospect


@router.put("/{prospect_id}", response_model=ProspectResponse)
def update_prospect(
    *,
    db: Session = Depends(get_db),
    prospect_id: UUID,
    prospect_in: ProspectUpdate,
    current_user: User = Depends(deps.check_permission("prospects:edit")),
) -> Any:
    """
    Update prospect
    """
    prospect = crud_prospect.get(db=db, id=prospect_id)
    
    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found"
        )
    
    # Check organization access
    if prospect.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    prospect = crud_prospect.update(db=db, db_obj=prospect, obj_in=prospect_in)
    return prospect


@router.delete("/{prospect_id}")
def delete_prospect(
    *,
    db: Session = Depends(get_db),
    prospect_id: UUID,
    current_user: User = Depends(deps.check_permission("prospects:delete")),
) -> Any:
    """
    Delete prospect
    """
    prospect = crud_prospect.get(db=db, id=prospect_id)
    
    if not prospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prospect not found"
        )
    
    # Check organization access
    if prospect.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    crud_prospect.remove(db=db, id=prospect_id)
    return {"message": "Prospect deleted successfully"}


@router.post("/analyze", response_model=ProspectAnalysisResponse)
async def analyze_prospect(
    *,
    db: Session = Depends(get_db),
    analysis_request: ProspectAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Analyze company prospects using AI scoring algorithms
    """
    try:
        # Perform AI analysis
        analysis_result = await prospect_ai_service.analyze_prospect(analysis_request)
        
        # Store analysis results in background
        background_tasks.add_task(
            store_analysis_results,
            db,
            analysis_request,
            analysis_result,
            current_user.organization_id,
            current_user.id
        )
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/score", response_model=ProspectScoringResponse)
async def score_prospects(
    *,
    scoring_request: ProspectScoringRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Score individual prospects based on custom criteria
    """
    try:
        scoring_result = await prospect_ai_service.score_prospects(scoring_request)
        return scoring_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scoring failed: {str(e)}"
        )


@router.get("/market-intelligence", response_model=MarketIntelligenceResponse)
async def get_market_intelligence(
    *,
    industry: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    time_period: str = Query("3M"),
    deal_type: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Provide real-time market data and trends
    """
    try:
        intelligence_result = await prospect_ai_service.get_market_intelligence(
            industry=industry,
            region=region,
            time_period=time_period,
            deal_type=deal_type
        )
        return intelligence_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market intelligence failed: {str(e)}"
        )


@router.get("/statistics", response_model=dict)
def get_prospect_statistics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    industry: Optional[str] = Query(None),
) -> Any:
    """
    Get prospect statistics for the organization
    """
    statistics = crud_prospect.get_industry_statistics(
        db=db,
        organization_id=current_user.organization_id,
        industry=industry
    )
    return statistics


@router.get("/high-priority", response_model=List[ProspectResponse])
def get_high_priority_prospects(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    limit: int = Query(10, ge=1, le=50),
) -> Any:
    """
    Get high priority prospects for the organization
    """
    prospects = crud_prospect.get_high_priority_prospects(
        db=db,
        organization_id=current_user.organization_id,
        limit=limit
    )
    return prospects


@router.get("/follow-up", response_model=List[ProspectResponse])
def get_prospects_requiring_follow_up(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    days_ahead: int = Query(7, ge=1, le=30),
) -> Any:
    """
    Get prospects requiring follow-up within specified days
    """
    prospects = crud_prospect.get_prospects_requiring_follow_up(
        db=db,
        organization_id=current_user.organization_id,
        days_ahead=days_ahead
    )
    return prospects


# Background task functions
def store_analysis_results(
    db: Session,
    request: ProspectAnalysisRequest,
    result: ProspectAnalysisResponse,
    organization_id: UUID,
    user_id: UUID
):
    """Store analysis results in the database"""
    try:
        # Check if prospect exists, create if not
        prospect = crud_prospect.get_by_company_name(
            db=db,
            company_name=request.company_name,
            organization_id=organization_id
        )
        
        if not prospect:
            # Create new prospect from analysis request
            prospect_data = {
                "company_name": request.company_name,
                "industry": request.industry,
                "location": request.location,
                "revenue": request.revenue,
                "employees": request.employees,
                "market_cap": request.market_cap,
                "organization_id": organization_id,
                "created_by_id": user_id,
                "status": "analyzing"
            }
            prospect = crud_prospect.create(db=db, obj_in=prospect_data)
        
        # Update prospect with AI analysis results
        crud_prospect.update_ai_scores(
            db=db,
            prospect_id=prospect.id,
            ai_score=result.ai_score,
            confidence_level=result.confidence_level,
            deal_probability=result.deal_probability,
            estimated_deal_size=result.estimated_deal_size,
            risk_factors=result.risk_factors,
            opportunities=result.opportunities,
            recommended_approach=result.recommended_approach
        )
        
        # Store detailed analysis
        analysis_data = {
            "analysis_type": request.analysis_type,
            "overall_score": result.ai_score,
            "confidence_score": float(result.ai_score),
            "key_findings": ["AI analysis completed"],
            "recommendations": [result.recommended_approach],
            "processing_time_seconds": float(result.processing_time) if result.processing_time else 0,
            "model_version": "1.0.0"
        }
        
        crud_prospect_analysis.create_analysis(
            db=db,
            prospect_id=prospect.id,
            analysis_type=request.analysis_type,
            results=analysis_data,
            organization_id=organization_id,
            created_by_id=user_id
        )
        
    except Exception as e:
        # Log error but don't fail the main request
        print(f"Error storing analysis results: {str(e)}")
