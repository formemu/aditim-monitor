"""
ADITIM Monitor Server - FastAPI application for task management
"""

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import get_db
from .models import (
    DirDepartament, DirTypeWork, DirQueueStatus, Profile, Product,
    Task, ProfileComponent, ProductComponent
)

app = FastAPI(
    title="ADITIM Monitor API",
    description="Task management system for metalworking workshop",
    version="1.0.0"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Pydantic схемы ===
class TaskCreate(BaseModel):
    """Schema for creating new task"""
    id_product: Optional[int] = None
    id_profile: Optional[int] = None
    id_departament: int
    equipment: str
    deadline: str
    position: int
    id_type_work: int
    id_status: Optional[int] = 1  # Default to "Новая"

class TaskUpdate(BaseModel):
    """Schema for updating task"""
    id_product: Optional[int] = None
    id_profile: Optional[int] = None
    id_departament: Optional[int] = None
    equipment: Optional[str] = None
    deadline: Optional[str] = None
    position: Optional[int] = None
    id_type_work: Optional[int] = None
    id_status: Optional[int] = None

class ProductCreate(BaseModel):
    """Schema for creating new product"""
    name: str
    id_departament: int
    sketch: Optional[str] = None

class ProfileCreate(BaseModel):
    """Schema for creating new profile"""
    article: str
    sketch: Optional[str] = None

# === API Endpoints ===

# Task endpoints
@app.get("/api/tasks/", response_model=List[dict])
async def get_tasks(
    status_id: Optional[int] = Query(None, description="Filter by status ID"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"), 
    limit: Optional[int] = Query(None, description="Limit number of results"),
    db: Session = Depends(get_db)
):
    """Get tasks with optional filtering"""
    query = db.query(Task).join(Task.departament).join(Task.type_work).join(Task.status)
    
    if status_id:
        query = query.filter(Task.id_status == status_id)
    if department_id:
        query = query.filter(Task.id_departament == department_id)
    
    query = query.order_by(Task.position)
    
    if limit:
        query = query.limit(limit)
    
    tasks = query.all()
    
    result = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "id_product": task.id_product,
            "id_profile": task.id_profile,
            "id_departament": task.id_departament,
            "equipment": task.equipment,
            "deadline": task.deadline,
            "position": task.position,
            "id_type_work": task.id_type_work,
            "id_status": task.id_status,
            "departament": {"id": task.departament.id, "name": task.departament.name},
            "type_work": {"id": task.type_work.id, "name": task.type_work.name},
            "status": {"id": task.status.id, "name": task.status.name} if task.status else None,
        }
        
        # Add profile/product info
        if task.id_profile and task.profile:
            task_dict["profile"] = {"id": task.profile.id, "article": task.profile.article}
        if task.id_product and task.product:
            task_dict["product"] = {"id": task.product.id, "name": task.product.name}
            
        result.append(task_dict)
    
    return result

@app.post("/api/tasks/", response_model=dict)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create new task"""
    # Get max position for auto-increment
    max_position = db.query(func.max(Task.position)).scalar() or 0
    
    db_task = Task(
        id_product=task.id_product,
        id_profile=task.id_profile,
        id_departament=task.id_departament,
        equipment=task.equipment,
        deadline=task.deadline,
        position=max_position + 1,
        id_type_work=task.id_type_work,
        id_status=task.id_status or 1
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return {"id": db_task.id, "message": "Task created successfully"}

@app.put("/api/tasks/{task_id}", response_model=dict)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """Update task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update only provided fields
    for field, value in task.dict(exclude_unset=True).items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    
    return {"id": db_task.id, "message": "Task updated successfully"}

@app.delete("/api/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    
    return {"message": "Task deleted successfully"}

@app.put("/api/tasks/{task_id}/position", response_model=dict)
async def update_task_position(task_id: int, position_data: dict, db: Session = Depends(get_db)):
    """Update task position in queue"""
    new_position = position_data.get("position")
    if new_position is None:
        raise HTTPException(status_code=400, detail="Position is required")
    
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    old_position = db_task.position
    db_task.position = new_position
    
    # Reorder other tasks
    if new_position > old_position:
        # Moving down: shift tasks up
        db.query(Task).filter(
            Task.position > old_position,
            Task.position <= new_position,
            Task.id != task_id
        ).update({Task.position: Task.position - 1})
    else:
        # Moving up: shift tasks down
        db.query(Task).filter(
            Task.position >= new_position,
            Task.position < old_position,
            Task.id != task_id
        ).update({Task.position: Task.position + 1})
    
    db.commit()
    return {"message": "Task position updated successfully"}

# Directory endpoints
@app.get("/api/directories/statuses/", response_model=List[dict])
async def get_statuses(db: Session = Depends(get_db)):
    """Get all task statuses"""
    statuses = db.query(DirQueueStatus).all()
    return [{"id": s.id, "name": s.name} for s in statuses]

@app.get("/api/directories/departments/", response_model=List[dict])
async def get_departments(db: Session = Depends(get_db)):
    """Get all departments"""
    departments = db.query(DirDepartament).all()
    return [{"id": d.id, "name": d.name} for d in departments]

@app.get("/api/directories/type_works/", response_model=List[dict])
async def get_type_works(db: Session = Depends(get_db)):
    """Get all work types"""
    type_works = db.query(DirTypeWork).all()
    return [{"id": t.id, "name": t.name} for t in type_works]

# Profile endpoints
@app.get("/api/profiles/", response_model=List[dict])
async def get_profiles(db: Session = Depends(get_db)):
    """Get all profiles"""
    profiles = db.query(Profile).all()
    return [{"id": p.id, "article": p.article, "sketch": p.sketch} for p in profiles]

@app.post("/api/profiles/", response_model=dict)
async def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """Create new profile"""
    db_profile = Profile(article=profile.article, sketch=profile.sketch)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return {"id": db_profile.id, "article": db_profile.article}

# Product endpoints  
@app.get("/api/products/", response_model=List[dict])
async def get_products(db: Session = Depends(get_db)):
    """Get all products"""
    products = db.query(Product).all()
    return [{"id": p.id, "name": p.name, "id_departament": p.id_departament} for p in products]

@app.post("/api/products/", response_model=dict)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create new product"""
    db_product = Product(
        name=product.name,
        id_departament=product.id_departament,
        sketch=product.sketch
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return {"id": db_product.id, "name": db_product.name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
