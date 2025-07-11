"""
Client schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID


class ClientBase(BaseModel):
    """Base client schema"""
    name: str
    company: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    client_type: str = "prospect"
    relationship_status: str = "cold"
    source: Optional[str] = None
    communication_preference: str = "email"
    timezone: Optional[str] = None
    notes: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None


class ClientCreate(ClientBase):
    """Client creation schema"""
    tags: Optional[List[str]] = []


class ClientUpdate(BaseModel):
    """Client update schema"""
    name: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    client_type: Optional[str] = None
    relationship_status: Optional[str] = None
    source: Optional[str] = None
    communication_preference: Optional[str] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    tags: Optional[List[str]] = None


class ClientInDBBase(ClientBase):
    """Base client schema with database fields"""
    id: UUID
    organization_id: UUID
    tags: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class Client(ClientInDBBase):
    """Client schema for API responses"""
    pass


class ClientResponse(ClientInDBBase):
    """Client response schema with additional computed fields"""
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


class ClientSummary(BaseModel):
    """Client summary statistics"""
    total_clients: int
    prospects: int
    active_clients: int
    inactive_clients: int
    clients_by_type: dict
    clients_by_industry: dict
    clients_by_source: dict
    recent_clients: List[ClientResponse]
