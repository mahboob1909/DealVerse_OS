"""
Organization model
"""
from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Organization(BaseModel):
    """Organization model for multi-tenancy"""
    
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    image_url = Column(String(500))
    
    # Subscription and billing
    subscription_tier = Column(String(50), default="basic")
    subscription_status = Column(String(50), default="active")
    
    # Organization settings
    settings = Column(JSON, default=dict)
    
    # Contact information
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    website = Column(String(255))
    
    # Address information
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="organization", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="organization", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="organization", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="organization", cascade="all, delete-orphan")
    financial_models = relationship("FinancialModel", back_populates="organization", cascade="all, delete-orphan")
    prospects = relationship("Prospect", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', slug='{self.slug}')>"
