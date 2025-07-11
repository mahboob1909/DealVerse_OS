"""
Deal schemas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, validator
from uuid import UUID


class DealBase(BaseModel):
    """Base deal schema"""
    title: str
    description: Optional[str] = None
    deal_type: str
    deal_value: Optional[Decimal] = None
    currency: str = "USD"
    fee_amount: Optional[Decimal] = None
    fee_percentage: Optional[Decimal] = None
    stage: str = "prospecting"
    status: str = "active"
    probability: Optional[str] = None
    expected_close_date: Optional[date] = None
    target_company: Optional[str] = None
    target_industry: Optional[str] = None
    target_location: Optional[str] = None
    target_revenue: Optional[Decimal] = None
    target_employees: Optional[str] = None
    lead_banker: Optional[str] = None
    ai_score: Optional[str] = None
    notes: Optional[str] = None


class DealCreate(DealBase):
    """Deal creation schema"""
    client_id: Optional[UUID] = None
    tags: Optional[List[str]] = []
    risk_factors: Optional[List[str]] = []
    opportunities: Optional[List[str]] = []


class DealUpdate(BaseModel):
    """Deal update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    deal_type: Optional[str] = None
    deal_value: Optional[Decimal] = None
    currency: Optional[str] = None
    fee_amount: Optional[Decimal] = None
    fee_percentage: Optional[Decimal] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    probability: Optional[str] = None
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    pitch_date: Optional[date] = None
    target_company: Optional[str] = None
    target_industry: Optional[str] = None
    target_location: Optional[str] = None
    target_revenue: Optional[Decimal] = None
    target_employees: Optional[str] = None
    lead_banker: Optional[str] = None
    ai_score: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None
    opportunities: Optional[List[str]] = None


class DealInDBBase(DealBase):
    """Base deal schema with database fields"""
    id: UUID
    organization_id: UUID
    client_id: Optional[UUID] = None
    created_by_id: Optional[UUID] = None
    actual_close_date: Optional[date] = None
    pitch_date: Optional[date] = None
    deal_team: Optional[List[Dict[str, Any]]] = []
    tags: Optional[List[str]] = []
    risk_factors: Optional[List[str]] = []
    opportunities: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Deal(DealInDBBase):
    """Deal schema for API responses"""
    pass


class DealResponse(DealInDBBase):
    """Deal response schema with additional computed fields"""
    
    @validator('deal_value', pre=True)
    def convert_decimal_to_float(cls, v):
        if isinstance(v, Decimal):
            return float(v)
        return v
    
    @validator('fee_amount', pre=True)
    def convert_fee_amount_to_float(cls, v):
        if isinstance(v, Decimal):
            return float(v)
        return v
    
    @validator('target_revenue', pre=True)
    def convert_target_revenue_to_float(cls, v):
        if isinstance(v, Decimal):
            return float(v)
        return v


class DealSummary(BaseModel):
    """Deal summary statistics"""
    total_deals: int
    active_deals: int
    closed_deals: int
    total_value: float
    average_deal_size: float
    win_rate: float
    deals_by_stage: Dict[str, int]
    deals_by_type: Dict[str, int]
    monthly_revenue: List[Dict[str, Any]]
