"""
CRUD operations for FinancialModel model
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.financial_model import FinancialModel
from app.schemas.financial_model import FinancialModelCreate, FinancialModelUpdate


class CRUDFinancialModel(CRUDBase[FinancialModel, FinancialModelCreate, FinancialModelUpdate]):
    """CRUD operations for FinancialModel model"""
    
    def get_by_organization(
        self,
        db: Session,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        model_type: Optional[str] = None,
        deal_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[FinancialModel]:
        """Get financial models by organization with optional filters"""
        query = (
            db.query(self.model)
            .filter(FinancialModel.organization_id == organization_id)
        )

        # Apply optional filters
        if model_type:
            query = query.filter(FinancialModel.model_type == model_type)
        if deal_id:
            query = query.filter(FinancialModel.deal_id == deal_id)
        if status:
            query = query.filter(FinancialModel.status == status)

        return query.offset(skip).limit(limit).all()
    
    def get_by_deal(
        self, 
        db: Session, 
        deal_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[FinancialModel]:
        """Get financial models by deal"""
        return (
            db.query(self.model)
            .filter(FinancialModel.deal_id == deal_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_type(
        self, 
        db: Session, 
        model_type: str,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FinancialModel]:
        """Get financial models by type"""
        query = db.query(self.model).filter(FinancialModel.model_type == model_type)
        
        if organization_id:
            query = query.filter(FinancialModel.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_current_models(
        self, 
        db: Session,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FinancialModel]:
        """Get current version financial models"""
        query = db.query(self.model).filter(FinancialModel.is_current == True)
        
        if organization_id:
            query = query.filter(FinancialModel.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_templates(
        self, 
        db: Session,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FinancialModel]:
        """Get template financial models"""
        query = db.query(self.model).filter(FinancialModel.is_template == True)
        
        if organization_id:
            query = query.filter(FinancialModel.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_by_status(
        self, 
        db: Session, 
        status: str,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FinancialModel]:
        """Get financial models by status"""
        query = db.query(self.model).filter(FinancialModel.status == status)
        
        if organization_id:
            query = query.filter(FinancialModel.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_model_versions(
        self, 
        db: Session, 
        parent_model_id: UUID
    ) -> List[FinancialModel]:
        """Get all versions of a financial model"""
        return (
            db.query(self.model)
            .filter(
                (FinancialModel.parent_model_id == parent_model_id) |
                (FinancialModel.id == parent_model_id)
            )
            .order_by(FinancialModel.version.desc())
            .all()
        )
    
    def create_new_version(
        self, 
        db: Session, 
        model_id: UUID,
        obj_in: FinancialModelUpdate
    ) -> Optional[FinancialModel]:
        """Create a new version of an existing model"""
        original_model = self.get(db, id=model_id)
        if not original_model:
            return None
        
        # Mark current model as not current
        original_model.is_current = False
        
        # Create new version
        new_version_data = original_model.__dict__.copy()
        new_version_data.pop('id', None)
        new_version_data.pop('created_at', None)
        new_version_data.pop('updated_at', None)
        new_version_data['version'] = original_model.version + 1
        new_version_data['is_current'] = True
        new_version_data['parent_model_id'] = original_model.parent_model_id or original_model.id
        
        # Update with new data
        for field, value in obj_in.dict(exclude_unset=True).items():
            new_version_data[field] = value
        
        new_model = FinancialModel(**new_version_data)
        db.add(new_model)
        db.commit()
        db.refresh(new_model)
        
        return new_model

    def get_model_statistics(
        self,
        db: Session,
        organization_id: UUID
    ) -> dict:
        """Get statistics for financial models"""
        total_models = (
            db.query(self.model)
            .filter(FinancialModel.organization_id == organization_id)
            .filter(FinancialModel.is_current == True)
            .count()
        )

        active_models = (
            db.query(self.model)
            .filter(FinancialModel.organization_id == organization_id)
            .filter(FinancialModel.status == "approved")
            .filter(FinancialModel.is_current == True)
            .count()
        )

        models_in_review = (
            db.query(self.model)
            .filter(FinancialModel.organization_id == organization_id)
            .filter(FinancialModel.status == "review")
            .filter(FinancialModel.is_current == True)
            .count()
        )

        draft_models = (
            db.query(self.model)
            .filter(FinancialModel.organization_id == organization_id)
            .filter(FinancialModel.status == "draft")
            .filter(FinancialModel.is_current == True)
            .count()
        )

        return {
            "total_models": total_models,
            "active_models": active_models,
            "models_in_review": models_in_review,
            "draft_models": draft_models
        }


crud_financial_model = CRUDFinancialModel(FinancialModel)
