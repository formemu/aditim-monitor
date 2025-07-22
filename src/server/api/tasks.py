"""
API routes for tasks
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.tasks import Task
from ..models.products import Product, Profile
from ..models.directories import DirDepartment, DirTaskStatus
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
        query = query.join(DirTaskStatus).filter(DirTaskStatus.name == status)
    
    tasks = query.order_by(Task.position).limit(limit).all()
    return tasks


@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    task_data = task.dict()
    
    # Handle product creation/lookup
    if task.product_id and isinstance(task.product_id, str):
        # If product_id is a string, treat it as product name and create/find product
        product_name = task.product_id
        product = db.query(Product).filter(Product.name == product_name).first()
        if not product:
            # Create new product
            product = Product(name=product_name, department_id=task.department_id)
            db.add(product)
            db.commit()
            db.refresh(product)
        task_data["product_id"] = product.id
    elif task.product_id:
        # If it's an integer, validate it exists
        product = db.query(Product).filter(Product.id == task.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    # Handle profile creation/lookup
    if task.profile_id and isinstance(task.profile_id, str):
        # If profile_id is a string, treat it as profile article and create/find profile
        profile_article = task.profile_id
        profile = db.query(Profile).filter(Profile.article == profile_article).first()
        if not profile:
            # Create new profile
            profile = Profile(article=profile_article)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        task_data["profile_id"] = profile.id
    elif task.profile_id:
        # If it's an integer, validate it exists
        profile = db.query(Profile).filter(Profile.id == task.profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
    
    # Create task
    db_task = Task(**task_data)
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
