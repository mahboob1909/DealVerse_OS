"""
Client model for managing client relationships
"""
from sqlalchemy import Column, String, Text, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Client(BaseModel):
    """Client model for CRM functionality"""
    
    __tablename__ = "clients"
    
    # Basic client information
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    title = Column(String(100))
    department = Column(String(100))
    
    # Contact information
    email = Column(String(255))
    phone = Column(String(50))
    mobile = Column(String(50))
    website = Column(String(255))
    
    # Address information
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Company information
    industry = Column(String(100))
    company_size = Column(String(50))  # startup, small, medium, large, enterprise
    annual_revenue = Column(String(50))
    
    # Relationship information
    client_type = Column(String(50), default="prospect")  # prospect, active, inactive, former
    relationship_status = Column(String(50), default="cold")  # cold, warm, hot, client
    source = Column(String(100))  # referral, website, event, cold_outreach, etc.
    
    # Preferences and notes
    communication_preference = Column(String(50), default="email")  # email, phone, in_person
    timezone = Column(String(50))
    notes = Column(Text)
    tags = Column(JSON, default=list)
    
    # Social and professional links
    linkedin_url = Column(String(255))
    twitter_url = Column(String(255))
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="clients")
    
    # Relationships
    deals = relationship("Deal", back_populates="client")
    documents = relationship("Document", back_populates="client")
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', company='{self.company}', type='{self.client_type}')>"

    # Database indexes for performance optimization
    __table_args__ = (
        # Single column indexes for frequently queried fields
        Index('idx_clients_organization_id', 'organization_id'),
        Index('idx_clients_client_type', 'client_type'),
        Index('idx_clients_relationship_status', 'relationship_status'),
        Index('idx_clients_industry', 'industry'),
        Index('idx_clients_company_size', 'company_size'),
        Index('idx_clients_created_at', 'created_at'),
        Index('idx_clients_updated_at', 'updated_at'),
        Index('idx_clients_email', 'email'),
        Index('idx_clients_company', 'company'),
        Index('idx_clients_name', 'name'),

        # Composite indexes for common query patterns
        Index('idx_clients_org_type', 'organization_id', 'client_type'),
        Index('idx_clients_org_status', 'organization_id', 'relationship_status'),
        Index('idx_clients_org_industry', 'organization_id', 'industry'),
        Index('idx_clients_org_created', 'organization_id', 'created_at'),
        Index('idx_clients_type_status', 'client_type', 'relationship_status'),
        Index('idx_clients_org_type_status', 'organization_id', 'client_type', 'relationship_status'),

        # Indexes for search functionality
        Index('idx_clients_name_company', 'name', 'company'),
        Index('idx_clients_email_company', 'email', 'company'),

        # Indexes for filtering and sorting
        Index('idx_clients_industry_size', 'industry', 'company_size'),
        Index('idx_clients_org_name', 'organization_id', 'name'),
    )
