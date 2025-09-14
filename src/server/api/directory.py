"""API routes for directory"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directory import ( ModelDirDepartment, ModelDirTaskStatus, ModelDirProfileToolComponentType,
                                 ModelDirProfileToolComponentStatus, ModelDirProfileToolDimension, ModelDirMachine,
                                 ModelDirWorkType, ModelDirTaskComponentStageName)

from ..schemas.directory import ( SchemaDirDepartment, SchemaDirTaskStatus, SchemaDirProfiletoolComponentType,
                                  SchemaDirComponentStatus, SchemaDirToolDimension, SchemaDirMachine,
                                  SchemaDirWorkType, SchemaDirTaskComponentStageName)

router = APIRouter(prefix="/api/directory", tags=["directory"], redirect_slashes=False)


@router.get("/dir_department", response_model=List[SchemaDirDepartment])
def get_department(db: Session = Depends(get_db)):
    """Получить все отделы"""
    return db.query(ModelDirDepartment).all()


@router.get("/dir_task_status", response_model=List[SchemaDirTaskStatus])
def get_task_status(db: Session = Depends(get_db)):
    """Получить все статусы задач"""
    return db.query(ModelDirTaskStatus).all()


@router.get("/dir_component_type", response_model=List[SchemaDirProfiletoolComponentType])
def get_component_type(db: Session = Depends(get_db)):
    """Получить все типы компонентов"""
    return db.query(ModelDirProfileToolComponentType).all()


@router.get("/dir_component_status", response_model=List[SchemaDirComponentStatus])
def get_component_status(db: Session = Depends(get_db)):
    """Получить все статусы компонентов"""
    return db.query(ModelDirProfileToolComponentStatus).all()


@router.get("/dir_tool_dimension", response_model=List[SchemaDirToolDimension])
def get_tool_dimension(db: Session = Depends(get_db)):
    """Получить все размерности инструмента"""
    return db.query(ModelDirProfileToolDimension).all()

@router.get("/dir_machine", response_model=List[SchemaDirMachine])
def get_machine(db: Session = Depends(get_db)):
    """Получить все станки"""
    return db.query(ModelDirMachine).all()

@router.get("/dir_work_type", response_model=List[SchemaDirWorkType])
def get_work_type(db: Session = Depends(get_db)):
    """Получить все типы работ"""
    return db.query(ModelDirWorkType).all()

@router.get("/dir_task_component_stage", response_model=List[SchemaDirTaskComponentStageName])
def get_task_component_stage(db: Session = Depends(get_db)):
    """Получить все стадии задач компонентов"""
    return db.query(ModelDirTaskComponentStageName).all()