"""
API routes for tasks
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.tasks import Task
from ..models.products import Product, Profile
from ..models.directories import DirDepartament, DirTypeWork, DirQueueStatus
from ..schemas.tasks import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all tasks with optional status filter"""
    query = db.query(Task)
    
    if status:
        query = query.join(DirQueueStatus).filter(DirQueueStatus.name == status)
    
    tasks = query.order_by(Task.position).limit(limit).all()
    return tasks


@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    # Validate foreign keys
    if task.id_product:
        product = db.query(Product).filter(Product.id == task.id_product).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    if task.id_profile:
        profile = db.query(Profile).filter(Profile.id == task.id_profile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
    
    # Create task
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


@router.put("/{task_id}/position")
def update_task_position(task_id: int, position: int, db: Session = Depends(get_db)):
    """Update task position in queue"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.position = position
    db.commit()
    return {"message": "Task position updated successfully"}
