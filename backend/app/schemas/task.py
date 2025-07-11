"""
Task schemas for API serialization
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    """Base task schema"""
    title: str
    description: Optional[str] = None
    task_type: str = "general"
    priority: str = "medium"
    category: Optional[str] = None
    status: str = "todo"
    progress: str = "0"
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[str] = None
    tags: List[str] = []
    checklist: List[dict] = []
    attachments: List[dict] = []


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    organization_id: UUID
    assignee_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[str] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    estimated_hours: Optional[str] = None
    actual_hours: Optional[str] = None
    tags: Optional[List[str]] = None
    checklist: Optional[List[dict]] = None
    attachments: Optional[List[dict]] = None
    assignee_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None


class Task(TaskBase):
    """Schema for task response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    completed_date: Optional[datetime] = None
    actual_hours: Optional[str] = None
    organization_id: UUID
    assignee_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(Task):
    """Extended task response with relationships"""
    assignee: Optional[dict] = None
    deal: Optional[dict] = None
    organization: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
