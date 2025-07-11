"""
Task management endpoints
"""
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_task import crud_task
from app.db.database import get_db
from app.models.user import User
from app.schemas.task import Task, TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = Query(None, description="Filter by task status"),
    priority: str = Query(None, description="Filter by priority"),
    assignee_id: UUID = Query(None, description="Filter by assignee"),
    deal_id: UUID = Query(None, description="Filter by deal"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve tasks for the current user's organization
    """
    tasks = crud_task.get_by_organization(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        deal_id=deal_id
    )
    return tasks


@router.post("/", response_model=TaskResponse)
def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: User = Depends(deps.check_permission("tasks:create")),
) -> Any:
    """
    Create new task
    """
    # Add organization info
    task_data = task_in.dict()
    task_data["organization_id"] = current_user.organization_id
    
    task = crud_task.create(db=db, obj_in=task_data)
    return task


@router.get("/my", response_model=List[TaskResponse])
def read_my_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = Query(None, description="Filter by task status"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get tasks assigned to current user
    """
    tasks = crud_task.get_by_assignee(
        db,
        assignee_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def read_task(
    *,
    db: Session = Depends(get_db),
    task_id: UUID,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task by ID
    """
    task = crud_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user has access to this task's organization
    if task.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    *,
    db: Session = Depends(get_db),
    task_id: UUID,
    task_in: TaskUpdate,
    current_user: User = Depends(deps.check_permission("tasks:edit")),
) -> Any:
    """
    Update task
    """
    task = crud_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user has access to this task's organization
    if task.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    task = crud_task.update(db=db, db_obj=task, obj_in=task_in)
    return task


@router.delete("/{task_id}")
def delete_task(
    *,
    db: Session = Depends(get_db),
    task_id: UUID,
    current_user: User = Depends(deps.check_permission("tasks:delete")),
) -> Any:
    """
    Delete task
    """
    task = crud_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user has access to this task's organization
    if task.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    task = crud_task.remove(db=db, id=task_id)
    return {"message": "Task deleted successfully"}


@router.put("/{task_id}/status")
def update_task_status(
    *,
    db: Session = Depends(get_db),
    task_id: UUID,
    status: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update task status
    """
    task = crud_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user has access to this task's organization or is assigned to it
    if (task.organization_id != current_user.organization_id and 
        task.assignee_id != current_user.id and 
        not current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update status and completion date if marking as done
    update_data = {"status": status}
    if status == "done":
        from datetime import datetime
        update_data["completed_date"] = datetime.utcnow()
    
    task = crud_task.update(db=db, db_obj=task, obj_in=update_data)
    return task


@router.get("/stats/summary")
def get_tasks_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get tasks summary statistics
    """
    stats = crud_task.get_organization_stats(db, organization_id=current_user.organization_id)
    return stats
