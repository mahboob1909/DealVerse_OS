"""
Financial Model schemas for API serialization
"""
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from app.schemas.user import UserResponse
    from app.schemas.deal import DealResponse
    from app.schemas.organization import OrganizationResponse


class FinancialModelBase(BaseModel):
    """Base financial model schema"""
    name: str
    description: Optional[str] = None
    model_type: str
    version: int = 1
    is_current: bool = True
    model_data: dict
    assumptions: dict = {}
    inputs: dict = {}
    outputs: dict = {}
    scenarios: List[dict] = []
    sensitivity_analysis: dict = {}
    status: str = "draft"
    tags: List[str] = []
    is_template: bool = False

    # Valuation results
    enterprise_value: Optional[str] = None
    equity_value: Optional[str] = None
    share_price: Optional[str] = None
    valuation_multiple: Optional[str] = None


class FinancialModelCreate(FinancialModelBase):
    """Schema for creating a new financial model"""
    organization_id: UUID
    created_by_id: UUID
    deal_id: Optional[UUID] = None
    parent_model_id: Optional[UUID] = None


class FinancialModelUpdate(BaseModel):
    """Schema for updating a financial model"""
    name: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = None
    model_data: Optional[dict] = None
    assumptions: Optional[dict] = None
    inputs: Optional[dict] = None
    outputs: Optional[dict] = None
    scenarios: Optional[List[dict]] = None
    sensitivity_analysis: Optional[dict] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    is_template: Optional[bool] = None
    is_current: Optional[bool] = None
    deal_id: Optional[UUID] = None


class FinancialModel(FinancialModelBase):
    """Schema for financial model response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    organization_id: UUID
    created_by_id: UUID
    deal_id: Optional[UUID] = None
    parent_model_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class FinancialModelResponse(FinancialModel):
    """Financial model response schema"""
    pass


class FinancialModelSummary(BaseModel):
    """Summary schema for financial model listing"""
    id: UUID
    name: str
    model_type: str
    version: int
    status: str
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID
    deal_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
