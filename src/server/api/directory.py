"""API routes for directory"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directory import ( ModelDirDepartment, ModelDirTaskStatus, ModelDirProfileToolComponentType,
                                 ModelDirProfileToolComponentStatus, ModelDirProfileToolDimension, ModelDirMachine,
                                 ModelDirWorkType, ModelDirWorkSubtype, ModelDirTaskType, ModelDirTaskLocation,
                                 ModelDirBlankMaterial, ModelDirBlankType)

from ..schemas.directory import ( SchemaDirDepartment, SchemaDirTaskStatus, SchemaDirProfiletoolComponentType,
                                  SchemaDirComponentStatus, SchemaDirToolDimension,
                                  SchemaDirWorkType, WorkSubtype, SchemaDirTaskType, SchemaDirTaskLocation,
                                  SchemaDirBlankMaterial, SchemaDirBlankTypeResponse)

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

@router.get("/dir_machine")
def get_machine(
        db: Session = Depends(get_db),
        work_type_id: int = Query(None, description="Фильтр по типу работ")
    ):
        query = db.query(ModelDirMachine)
        if work_type_id is not None:
            query = query.filter(ModelDirMachine.work_type_id == work_type_id)
        return query.all()

@router.get("/dir_work_type", response_model=List[SchemaDirWorkType])
def get_work_type(db: Session = Depends(get_db)):
    """Получить все типы работ"""
    return db.query(ModelDirWorkType).all()

@router.get("/dir_work_subtype", response_model=List[WorkSubtype])
def get_task_component_stage(db: Session = Depends(get_db)):
    """Получить все стадии задач компонентов"""
    return db.query(ModelDirWorkSubtype).all()

@router.get("/dir_task_type", response_model=List[SchemaDirTaskType])
def get_task_type(db: Session = Depends(get_db)):
    """Получить все типы задач"""
    return db.query(ModelDirTaskType).all()

@router.get("/dir_task_location", response_model=List[SchemaDirTaskLocation])
def get_task_location(db: Session = Depends(get_db)):
    """Получить все местоположения задач"""
    return db.query(ModelDirTaskLocation).all()

@router.get("/dir_blank_material", response_model=List[SchemaDirBlankMaterial])
def get_blank_material(db: Session = Depends(get_db)):
    """Получить все материалы заготовок"""
    return db.query(ModelDirBlankMaterial).all()

@router.get("/dir_blank_type", response_model=List[SchemaDirBlankTypeResponse])
def get_blank_type(
    db: Session = Depends(get_db),
    material_id: int = Query(None, description="Фильтр по материалу")
):
    """Получить все типы заготовок с опциональным фильтром по материалу"""
    query = db.query(ModelDirBlankType)
    if material_id is not None:
        query = query.filter(ModelDirBlankType.material_id == material_id)
    return query.all()

