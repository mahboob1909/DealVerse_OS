"""
Organization schemas
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Organization creation schema"""
    slug: str
    subscription_tier: str = "basic"
    subscription_status: str = "active"
    settings: Optional[Dict[str, Any]] = {}


class OrganizationUpdate(BaseModel):
    """Organization update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationInDBBase(OrganizationBase):
    """Base organization schema with database fields"""
    id: UUID
    slug: str
    subscription_tier: str
    subscription_status: str
    settings: Optional[Dict[str, Any]] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Organization(OrganizationInDBBase):
    """Organization schema for API responses"""
    pass


class OrganizationResponse(OrganizationInDBBase):
    """Organization response schema with additional computed fields"""
    full_address: Optional[str] = None
    
    class Config:
        orm_mode = True
        
    def __init__(self, **data):
        super().__init__(**data)
        # Compute full address
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        self.full_address = ", ".join(filter(None, address_parts)) or None
