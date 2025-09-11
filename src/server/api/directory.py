"""API routes for directory"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directory import (
    ModelDirDepartment as DirDepartmentModel,
    ModelDirTaskStatus as DirTaskStatusModel,
    ModelDirComponentType as DirComponentTypeModel,
    ModelDirComponentStatus as DirComponentStatusModel,
    ModelDirToolDimension as DirToolDimensionModel,
)
from ..schemas.directory import (
    SchemaDirDepartment,
    SchemaDirTaskStatus,
    SchemaDirComponentType,
    SchemaDirComponentStatus,
    SchemaDirToolDimension,
)

router = APIRouter(prefix="/api/directory", tags=["directory"], redirect_slashes=False)


@router.get("/dir_department", response_model=List[SchemaDirDepartment])
def get_department(db: Session = Depends(get_db)):
    """Получить все отделы"""
    return db.query(DirDepartmentModel).all()


@router.get("/dir_task_status", response_model=List[SchemaDirTaskStatus])
def get_task_status(db: Session = Depends(get_db)):
    """Получить все статусы задач"""
    return db.query(DirTaskStatusModel).all()


@router.get("/dir_component_type", response_model=List[SchemaDirComponentType])
def get_component_type(db: Session = Depends(get_db)):
    """Получить все типы компонентов"""
    return db.query(DirComponentTypeModel).all()


@router.get("/dir_component_status", response_model=List[SchemaDirComponentStatus])
def get_component_status(db: Session = Depends(get_db)):
    """Получить все статусы компонентов"""
    return db.query(DirComponentStatusModel).all()


@router.get("/dir_tool_dimension", response_model=List[SchemaDirToolDimension])
def get_tool_dimension(db: Session = Depends(get_db)):
    """Получить все размерности инструмента"""
    return db.query(DirToolDimensionModel).all()