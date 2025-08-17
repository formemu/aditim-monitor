"""
API роутеры для задач
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.task import Task, TaskComponent
from ..models.directory import DirTaskStatus
from ..schemas.task import (
    TaskCreate,
    TaskStatusUpdate,
    TaskComponentCreate,
    TaskResponse,
    TaskComponentResponse,
)

router = APIRouter(prefix="/api", tags=["task"])


# =============================================================================
# ROUTER.GET
# =============================================================================

@router.get("/task", response_model=List[TaskResponse])
def get_task(
    status: Optional[str] = Query(None, description="Фильтр по названию статуса"),
    limit: int = Query(20, ge=1, le=100, description="Ограничение количества результатов"),
    db: Session = Depends(get_db)
):
    """Получить список задач с необязательным фильтром по статусу"""
    query = db.query(Task)

    if status:
        query = query.join(DirTaskStatus).filter(DirTaskStatus.name == status)

    query = query.order_by(Task.position).limit(limit)
    return query.all()


@router.get("/task/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int = Path(..., description="ID задачи"), db: Session = Depends(get_db)):
    """Получить задачу по ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.get("/task/{task_id}/component", response_model=List[TaskComponentResponse])
def get_task_component_list(task_id: int, db: Session = Depends(get_db)):
    """Получить компоненты задачи по ID задачи"""
    return db.query(TaskComponent).filter(TaskComponent.task_id == task_id).all()


# =============================================================================
# ROUTER.POST
# =============================================================================

@router.post("/task", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Создать новую задачу"""
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.post("/task/{task_id}/component", response_model=TaskComponentResponse)
def create_task_component(
    task_id: int = Path(..., description="ID задачи"),
    component: TaskComponentCreate = Body(...),
    db: Session = Depends(get_db)
):
    """Создать новый компонент задачи"""
    # Проверяем, существует ли задача
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    db_component = TaskComponent(**component.model_dump())
    db_component.task_id = task_id
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component


# =============================================================================
# ROUTER.PATCH
# =============================================================================

@router.patch("/task/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    request: TaskStatusUpdate,
    db: Session = Depends(get_db)
):
    """Обновить статус задачи"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Проверяем, существует ли статус
    status_exists = db.query(DirTaskStatus).filter(DirTaskStatus.id == request.status_id).first()
    if not status_exists:
        raise HTTPException(status_code=400, detail="Invalid status_id")

    task.status_id = request.status_id
    db.commit()
    db.refresh(task)
    return task


@router.patch("/task/{task_id}/position", response_model=TaskResponse)
def update_task_position(
    task_id: int,
    position: int = Body(..., embed=True, description="Новая позиция"),
    db: Session = Depends(get_db)
):
    """Обновить позицию задачи"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task.position = position
    db.commit()
    db.refresh(task)
    return task


# =============================================================================
# ROUTER.DELETE
# =============================================================================

@router.delete("/task/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Удалить задачу по ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    db.delete(task)
    db.commit()
    return {"detail": "Задача удалена успешно"}