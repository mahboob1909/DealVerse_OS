"""
Task model for project and deal management
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Task(BaseModel):
    """Task model for tracking work items and todos"""
    
    __tablename__ = "tasks"
    
    # Basic task information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Task categorization
    task_type = Column(String(50), default="general")  # general, due_diligence, modeling, compliance, pitch
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    category = Column(String(100))
    
    # Status and progress
    status = Column(String(50), default="todo")  # todo, in_progress, review, done, cancelled
    progress = Column(String(3), default="0")  # 0-100 percentage
    
    # Dates and deadlines
    due_date = Column(DateTime)
    start_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Effort estimation
    estimated_hours = Column(String(10))
    actual_hours = Column(String(10))
    
    # Task metadata
    tags = Column(JSON, default=list)
    checklist = Column(JSON, default=list)  # List of subtasks/checklist items
    attachments = Column(JSON, default=list)  # File references
    
    # Organization relationship
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="tasks")
    
    # Assignee relationship
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assignee = relationship("User", back_populates="assigned_tasks")
    
    # Deal relationship (optional)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"))
    deal = relationship("Deal", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}', priority='{self.priority}')>"

    # Database indexes for performance optimization
    __table_args__ = (
        # Single column indexes for frequently queried fields
        Index('idx_tasks_organization_id', 'organization_id'),
        Index('idx_tasks_assignee_id', 'assignee_id'),
        Index('idx_tasks_deal_id', 'deal_id'),
        Index('idx_tasks_status', 'status'),
        Index('idx_tasks_priority', 'priority'),
        Index('idx_tasks_task_type', 'task_type'),
        Index('idx_tasks_category', 'category'),
        Index('idx_tasks_created_at', 'created_at'),
        Index('idx_tasks_updated_at', 'updated_at'),
        Index('idx_tasks_due_date', 'due_date'),
        Index('idx_tasks_start_date', 'start_date'),
        Index('idx_tasks_completed_date', 'completed_date'),

        # Composite indexes for common query patterns
        Index('idx_tasks_org_status', 'organization_id', 'status'),
        Index('idx_tasks_org_priority', 'organization_id', 'priority'),
        Index('idx_tasks_org_assignee', 'organization_id', 'assignee_id'),
        Index('idx_tasks_org_type', 'organization_id', 'task_type'),
        Index('idx_tasks_assignee_status', 'assignee_id', 'status'),
        Index('idx_tasks_assignee_priority', 'assignee_id', 'priority'),
        Index('idx_tasks_deal_status', 'deal_id', 'status'),
        Index('idx_tasks_status_priority', 'status', 'priority'),
        Index('idx_tasks_org_status_priority', 'organization_id', 'status', 'priority'),

        # Indexes for date-based queries
        Index('idx_tasks_org_due_date', 'organization_id', 'due_date'),
        Index('idx_tasks_assignee_due_date', 'assignee_id', 'due_date'),
        Index('idx_tasks_status_due_date', 'status', 'due_date'),
        Index('idx_tasks_priority_due_date', 'priority', 'due_date'),

        # Indexes for task management workflows
        Index('idx_tasks_type_status', 'task_type', 'status'),
        Index('idx_tasks_org_type_status', 'organization_id', 'task_type', 'status'),
        Index('idx_tasks_deal_type_status', 'deal_id', 'task_type', 'status'),
    )
