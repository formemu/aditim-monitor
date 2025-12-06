"""API routes for profile tool"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profiletool import ModelProfileTool , ModelProfileToolComponent, ModelProfileToolComponentHistory
from ..schemas.profiletool import (
    SchemaProfileToolCreate,
    SchemaProfileToolResponse,
    SchemaProfileToolComponentCreate,
    SchemaProfileToolUpdate,
    SchemaProfileToolComponentResponse,
    SchemaProfileToolComponentHistoryCreate,
    SchemaProfileToolComponentHistoryResponse
)
from ..events import notify_clients

router = APIRouter(prefix="/api", tags=["profile-tool"])

# =============================================================================
# ROUTER.GET
# =============================================================================
@router.get("/profile-tool", response_model=List[SchemaProfileToolResponse])
def get_profiletool(db: Session = Depends(get_db)):
    """Получить все инструменты профиля"""
    return db.query(ModelProfileTool).all()


@router.get("/profile-tool/{profiletool_id}/component", response_model=List[SchemaProfileToolComponentResponse])
def get_profiletool_component(profiletool_id: int, db: Session = Depends(get_db)):
    """Получить все компоненты инструмента профиля"""
    return db.query(ModelProfileToolComponent).filter(ModelProfileToolComponent.profiletool_id == profiletool_id).all()


# =============================================================================
# ROUTER.POST
# =============================================================================

@router.post("/profile-tool", response_model=SchemaProfileToolResponse)
def create_profiletool(profiletool: SchemaProfileToolCreate, db: Session = Depends(get_db)):
    """Создать новый инструмент профиля"""
    try:
        tool = ModelProfileTool(
            profile_id=profiletool.profile_id,
            dimension_id=profiletool.dimension_id,
            description=profiletool.description
        )
        db.add(tool)
        db.commit()
        db.refresh(tool)

        notify_clients("table", "profiletool", "created")
        notify_clients("table", "profile", "updated")
        return tool
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Не удалось создать инструмент: " + str(e))

@router.post("/profile-tool/{profiletool_id}/component", response_model=SchemaProfileToolComponentResponse)
def create_profiletool_component(profiletool_id: int, component: SchemaProfileToolComponentCreate, db: Session = Depends(get_db)):
    """Создать новый компонент инструмента профиля"""
    try:
        db_component = ModelProfileToolComponent(
            profiletool_id=profiletool_id,
            type_id=component.type_id,
            variant=component.variant,
            description=component.description
        )
        db.add(db_component)
        db.commit()
        db.refresh(db_component)
        return db_component
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Не удалось создать компонент: " + str(e))

@router.post("/profile-tool-component/{profiletool_component_id}/history", response_model=SchemaProfileToolComponentHistoryResponse)
def create_profiletool_component_history(profiletool_component_id: int, history_data: SchemaProfileToolComponentHistoryCreate, db: Session = Depends(get_db)):
    """Создание истории изменений компонента инструмента профиля"""
    try:
        db_history = ModelProfileToolComponentHistory(
            profiletool_component_id=profiletool_component_id,
            date=history_data.date,
            status_id=history_data.status_id,
            description=history_data.description
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)


        notify_clients("table", "task", "updated") 
        notify_clients("table", "taskdev", "updated")
        notify_clients("table", "profiletool", "updated")
        return db_history
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Не удалось создать историю изменений: " + str(e))

# =============================================================================
# ROUTER.PATCH
# =============================================================================
@router.patch("/profile-tool/{profiletool_id}", response_model=SchemaProfileToolResponse)
def update_profiletool(profiletool_id: int, tool: SchemaProfileToolUpdate, db: Session = Depends(get_db)):
    """обновить инструмент профиля"""
    db_tool = db.get(ModelProfileTool, profiletool_id)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    update_data = tool.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tool, field, value)
    db.commit()
    db.refresh(db_tool)
    notify_clients("table", "profiletool", "updated")
    return db_tool

# =============================================================================
# ROUTER.DELETE
# =============================================================================
@router.delete("/profile-tool/{profiletool_id}", response_model=dict)
def delete_profiletool(profiletool_id: int, db: Session = Depends(get_db)):
    """Удалить инструмент профиля по ID"""
    tool = db.get(ModelProfileTool, profiletool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    db.delete(tool)
    db.commit()

    notify_clients("table", "profiletool", "deleted")
    notify_clients("table", "task", "deleted")
    notify_clients("table", "queue", "deleted")

    return {"detail": "Инструмент и его компоненты удалены успешно"}

@router.delete("/profile/{profile_id}/profile-tool")
def delete_profiletool_by_profile(profile_id: int, db: Session = Depends(get_db)):
    """Удалить все инструменты профиля (и их компоненты) по ID профиля"""
    deleted_count = db.query(ModelProfileTool).filter(ModelProfileTool.profile_id == profile_id).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Инструменты не найдены")
    db.commit()

    notify_clients("table", "profiletool", "deleted")
    notify_clients("table", "task", "deleted")
    notify_clients("table", "queue", "deleted")

    return {"detail": f"Удалены все инструменты и компоненты профиля {profile_id}"}

@router.delete("/profile-tool/{profiletool_id}/component", response_model=dict)
def delete_all_profiletool_components(profiletool_id: int, db: Session = Depends(get_db)):
    """Удалить все компоненты инструмента (без удаления инструмента)"""
    deleted_count = db.query(ModelProfileToolComponent).filter(ModelProfileToolComponent.profiletool_id == profiletool_id).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Компоненты не найдены")
    db.commit()


    return {"detail": f"Удалены все компоненты инструмента {profiletool_id}"}

@router.delete("/profile-tool/component/{component_id}", response_model=dict)
def delete_profiletool_component_by_id(component_id: int, db: Session = Depends(get_db)):
    """Удалить компонент инструмента по ID"""
    component = db.get(ModelProfileToolComponent, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Компонент не найден")
    db.delete(component)
    db.commit()

    return {"detail": "Компонент удален успешно"}