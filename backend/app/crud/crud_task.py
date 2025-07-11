"""
CRUD operations for Task model
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    """CRUD operations for Task model"""
    
    def get_by_organization(
        self, 
        db: Session, 
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks by organization"""
        return (
            db.query(self.model)
            .filter(Task.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_assignee(
        self, 
        db: Session, 
        assignee_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks by assignee"""
        return (
            db.query(self.model)
            .filter(Task.assignee_id == assignee_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_deal(
        self, 
        db: Session, 
        deal_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks by deal"""
        return (
            db.query(self.model)
            .filter(Task.deal_id == deal_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_status(
        self, 
        db: Session, 
        status: str,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks by status"""
        query = db.query(self.model).filter(Task.status == status)
        
        if organization_id:
            query = query.filter(Task.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_by_priority(
        self, 
        db: Session, 
        priority: str,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks by priority"""
        query = db.query(self.model).filter(Task.priority == priority)
        
        if organization_id:
            query = query.filter(Task.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def get_overdue_tasks(
        self, 
        db: Session,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get overdue tasks"""
        now = datetime.utcnow()
        query = (
            db.query(self.model)
            .filter(Task.due_date < now)
            .filter(Task.status.in_(["todo", "in_progress"]))
        )
        
        if organization_id:
            query = query.filter(Task.organization_id == organization_id)
            
        return query.offset(skip).limit(limit).all()
    
    def update_status(
        self, 
        db: Session, 
        task_id: UUID, 
        status: str
    ) -> Optional[Task]:
        """Update task status"""
        task = self.get(db, id=task_id)
        if task:
            task.status = status
            if status == "done":
                task.completed_date = datetime.utcnow()
                task.progress = "100"
            db.commit()
            db.refresh(task)
        return task
    
    def update_progress(
        self, 
        db: Session, 
        task_id: UUID, 
        progress: str
    ) -> Optional[Task]:
        """Update task progress"""
        task = self.get(db, id=task_id)
        if task:
            task.progress = progress
            if progress == "100" and task.status != "done":
                task.status = "done"
                task.completed_date = datetime.utcnow()
            db.commit()
            db.refresh(task)
        return task


crud_task = CRUDTask(Task)
