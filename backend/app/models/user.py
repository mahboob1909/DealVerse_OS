"""
User model
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    # Basic information
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Profile information
    image_url = Column(String(500))
    phone = Column(String(50))
    title = Column(String(100))
    department = Column(String(100))
    
    # Role and permissions
    role = Column(String(50), default="analyst")  # admin, manager, analyst, associate, vp
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Authentication tracking
    last_login = Column(DateTime)
    login_count = Column(String(10), default="0")
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="users")
    
    # Relationships
    assigned_tasks = relationship("Task", back_populates="assignee")
    created_deals = relationship("Deal", back_populates="created_by")
    created_documents = relationship("Document", back_populates="uploaded_by")
    created_models = relationship("FinancialModel", back_populates="created_by")
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def initials(self) -> str:
        """Get user's initials"""
        return f"{self.first_name[0]}{self.last_name[0]}".upper()
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    # Database indexes for performance optimization
    __table_args__ = (
        # Single column indexes for frequently queried fields
        Index('idx_users_organization_id', 'organization_id'),
        Index('idx_users_role', 'role'),
        Index('idx_users_is_active', 'is_active'),
        Index('idx_users_is_superuser', 'is_superuser'),
        Index('idx_users_is_verified', 'is_verified'),
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_updated_at', 'updated_at'),
        Index('idx_users_last_login', 'last_login'),
        Index('idx_users_department', 'department'),
        Index('idx_users_title', 'title'),

        # Composite indexes for common query patterns
        Index('idx_users_org_role', 'organization_id', 'role'),
        Index('idx_users_org_active', 'organization_id', 'is_active'),
        Index('idx_users_org_verified', 'organization_id', 'is_verified'),
        Index('idx_users_role_active', 'role', 'is_active'),
        Index('idx_users_org_role_active', 'organization_id', 'role', 'is_active'),
        Index('idx_users_org_department', 'organization_id', 'department'),

        # Indexes for authentication and session management
        Index('idx_users_active_verified', 'is_active', 'is_verified'),
        Index('idx_users_org_last_login', 'organization_id', 'last_login'),

        # Indexes for user search and filtering
        Index('idx_users_first_last_name', 'first_name', 'last_name'),
        Index('idx_users_org_name', 'organization_id', 'first_name', 'last_name'),
    )
