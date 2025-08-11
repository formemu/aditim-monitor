"""
API роутеры для задач
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.task import Task, TaskComponent
from ..models.directory import DirTaskStatus
from ..schemas.task import TaskCreate, TaskResponse, TaskStatusUpdate, TaskComponentCreate

router = APIRouter(prefix="/api", tags=["task"])

# =============================================================================
# ROUTER.GET
# =============================================================================
@router.get("/task")
def get_task(status: Optional[str] = None, limit: int = 20, db: Session = Depends(get_db)):
    """Получить список задач с необязательным фильтром по статусу"""
    query = db.query(Task)
    if status:
        query = query.join(DirTaskStatus).filter(DirTaskStatus.name == status).order_by(Task.position).limit(limit)
    else:
        query = query.order_by(Task.position).limit(limit)
    return query

@router.get("/task/{task_id}")
def get_task_by_id( task_id: int, db: Session = Depends(get_db)):
    """Получить задачу по ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        return task
    raise HTTPException(status_code=404, detail="Задача не найдена")

@router.get("/task/{task_id}/component")
def get_task_component_list(task_id: int, db: Session = Depends(get_db)):
    """Получить компоненты задачи по ID задачи"""
    return db.query(TaskComponent).filter(TaskComponent.task_id == task_id).all()

# =============================================================================
# ROUTER.POST
# =============================================================================
@router.post("/task", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.post("/task_component")
def create_task_component(task_id: int, component: TaskComponentCreate, db: Session = Depends(get_db)):
    """Создать новый компонент задачи"""
    component = TaskComponent(**component.model_dump())
    component.task_id = task_id
    db.add(component)
    db.commit()
    db.refresh(component)

# =============================================================================
# ROUTER.POST
# =============================================================================
@router.patch("/task/{task_id}/status")
def update_task_status(task_id: int, request: TaskStatusUpdate, db: Session = Depends(get_db)):
    """Обновить статус задачи"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status_id = request.status_id
        db.commit()
        db.refresh(task)
    else: raise HTTPException(status_code=404, detail="Задача не найдена")

@router.patch("/task/{task_id}/position")
def update_task_position(task_id: int, position: int, db: Session = Depends(get_db)):
    """Обновить позицию"""

    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.position = position
        db.commit()
        db.refresh(task)
    else: 
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
# =============================================================================
# ROUTER.DELETE
# =============================================================================
@router.delete("/task/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Удалить задачу"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Задача не найдена")
