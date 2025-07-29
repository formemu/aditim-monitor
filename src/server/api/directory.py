"""
API routes for directories
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directory import DirDepartment, DirTaskStatus, DirToolDimension, DirComponentType, DirComponentStatus
from ..schemas.directory import (
    DirDepartmentResponse, 
    DirTaskStatusResponse, 
    DirComponentTypeResponse, 
    DirComponentStatusResponse, 
    DirToolDimensionResponse
)

router = APIRouter(prefix="/api/directories", tags=["directories"], redirect_slashes=False)


@router.get("/dir_department", response_model=List[DirDepartmentResponse])
def get_department(db: Session = Depends(get_db)):
    """Получить все отделы"""
    return db.query(DirDepartment).all()


@router.get("/dir_task_status", response_model=List[DirTaskStatusResponse])
def get_task_status(db: Session = Depends(get_db)):
    """Получить все статусы задач"""
    return db.query(DirTaskStatus).all()


@router.get("/dir_component_type", response_model=List[DirComponentTypeResponse])
def get_component_type(db: Session = Depends(get_db)):
    """Получить все типы компонентов"""
    return db.query(DirComponentType).all()


@router.get("/dir_tool_dimension", response_model=List[DirToolDimensionResponse])
def get_tool_dimension(db: Session = Depends(get_db)):
    """Получить все размерности инструмента"""
    return db.query(DirToolDimension).all()


@router.get("/dir_component_status", response_model=List[DirComponentStatusResponse])
def get_component_status(db: Session = Depends(get_db)):
    """Получить все статусы компонентов"""
    return db.query(DirComponentStatus).all()