"""API routes for directory"""
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directory import ( ModelDirDepartment, ModelDirTaskStatus, ModelDirProfileToolComponentType,
                                 ModelDirProfileToolComponentStatus, ModelDirProfileToolDimension, ModelDirMachine,
                                 ModelDirWorkType, ModelDirWorkSubtype, ModelDirTaskType,
                                 ModelDirBlankMaterial, ModelDirBlankType)

from ..schemas.directory import ( SchemaDirDepartment, SchemaDirTaskStatus, SchemaDirProfiletoolComponentType,
                                  SchemaDirComponentStatus, SchemaDirToolDimension, SchemaDirToolDimensionCreate,
                                  SchemaDirToolDimensionUpdate, SchemaDirProfiletoolComponentTypeCreate,
                                  SchemaDirProfiletoolComponentTypeUpdate,
                                  SchemaDirWorkType, WorkSubtype, SchemaDirTaskType,
                                  SchemaDirBlankMaterial, SchemaDirBlankTypeResponse)

from ..events import notify_clients

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


# =============================================================================
# CRUD для размерностей инструментов (dir_profiletool_dimension)
# =============================================================================
@router.post("/dir_profiletool_dimension", response_model=SchemaDirToolDimension)
def create_profiletool_dimension(
    dimension: SchemaDirToolDimensionCreate,
    db: Session = Depends(get_db)
):
    """Создание новой размерности инструмента"""
    db_dimension = ModelDirProfileToolDimension(**dimension.model_dump())
    db.add(db_dimension)
    db.commit()
    db.refresh(db_dimension)
    
    # Отправляем сигнал об изменении данных
    notify_clients("directory", "profiletool_dimension", "create")

    return db_dimension


@router.put("/dir_profiletool_dimension/{dimension_id}", response_model=SchemaDirToolDimension)
def update_profiletool_dimension(
    dimension_id: int,
    dimension: SchemaDirToolDimensionUpdate,
    db: Session = Depends(get_db)
):
    """Обновление размерности инструмента"""
    db_dimension = db.query(ModelDirProfileToolDimension).filter(
        ModelDirProfileToolDimension.id == dimension_id
    ).first()
    
    if not db_dimension:
        raise HTTPException(status_code=404, detail="Размерность не найдена")
    
    # Обновляем только переданные поля
    update_data = dimension.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_dimension, key, value)
    
    db.commit()
    db.refresh(db_dimension)
    
    # Отправляем сигнал об изменении данных
    notify_clients("directory", "profiletool_dimension", "update")

    return db_dimension


@router.delete("/dir_profiletool_dimension/{dimension_id}")
def delete_profiletool_dimension(
    dimension_id: int,
    db: Session = Depends(get_db)
):
    """Удаление размерности инструмента"""
    db_dimension = db.query(ModelDirProfileToolDimension).filter(
        ModelDirProfileToolDimension.id == dimension_id
    ).first()
    
    if not db_dimension:
        raise HTTPException(status_code=404, detail="Размерность не найдена")
    
    db.delete(db_dimension)
    db.commit()
    
    # Отправляем сигнал об изменении данных
    notify_clients("directory", "profiletool_dimension", "delete")

    return {"status": "success", "message": "Размерность удалена"}


# =============================================================================
# CRUD для типов компонентов (dir_profiletool_component_type)
# =============================================================================
@router.post("/dir_component_type", response_model=SchemaDirProfiletoolComponentType)
def create_component_type(
    component_type: SchemaDirProfiletoolComponentTypeCreate,
    db: Session = Depends(get_db)
):
    """Создание нового типа компонента"""
    db_component_type = ModelDirProfileToolComponentType(**component_type.model_dump())
    db.add(db_component_type)
    db.commit()
    db.refresh(db_component_type)
    
    # Отправляем сигнал об изменении данных
    notify_clients("directory", "component_type", "create")

    return db_component_type


@router.put("/dir_component_type/{component_type_id}", response_model=SchemaDirProfiletoolComponentType)
def update_component_type(
    component_type_id: int,
    component_type: SchemaDirProfiletoolComponentTypeUpdate,
    db: Session = Depends(get_db)
):
    """Обновление типа компонента"""
    db_component_type = db.query(ModelDirProfileToolComponentType).filter(
        ModelDirProfileToolComponentType.id == component_type_id
    ).first()
    
    if not db_component_type:
        raise HTTPException(status_code=404, detail="Тип компонента не найден")
    
    # Обновляем только переданные поля
    update_data = component_type.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_component_type, key, value)
    
    db.commit()
    db.refresh(db_component_type)
    
    # Отправляем сигнал об изменении данных
    notify_clients("directory", "component_type", "update")

    return db_component_type


@router.delete("/dir_component_type/{component_type_id}")
def delete_component_type(
    component_type_id: int,
    db: Session = Depends(get_db)
):
    """Удаление типа компонента"""
    db_component_type = db.query(ModelDirProfileToolComponentType).filter(
        ModelDirProfileToolComponentType.id == component_type_id
    ).first()
    
    if not db_component_type:
        raise HTTPException(status_code=404, detail="Тип компонента не найден")
    
    db.delete(db_component_type)
    db.commit()
    
    # Отправляем сигнал об изменении данных
    notify_clients("directory", "component_type", "delete")

    return {"status": "success", "message": "Тип компонента удален"}


