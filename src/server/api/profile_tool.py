"""API routes for profile tool"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile_tool import ProfileTool, ProfileToolComponent
from ..schemas.profile_tool import (
    ProfileToolCreate,
    ProfileToolUpdate,
    ProfileToolResponse,
    ProfileToolComponentCreate,
    ProfileToolComponentResponse,
)

router = APIRouter(prefix="/api", tags=["profile-tool"])


# =============================================================================
# ROUTER.GET
# =============================================================================

@router.get("/profile-tool", response_model=List[ProfileToolResponse])
def get_profile_tool(db: Session = Depends(get_db)):
    """Получить все инструменты профиля"""
    return db.query(ProfileTool).all()


@router.get("/profile-tool/{tool_id}/component", response_model=List[ProfileToolComponentResponse])
def get_profile_tool_component(tool_id: int, db: Session = Depends(get_db)):
    """Получить все компоненты инструмента профиля"""
    return db.query(ProfileToolComponent).filter(ProfileToolComponent.tool_id == tool_id).all()


# =============================================================================
# ROUTER.POST
# =============================================================================

@router.post("/profile-tool", response_model=ProfileToolResponse)
def create_profile_tool(profile_tool: ProfileToolCreate, db: Session = Depends(get_db)):
    """Создать новый инструмент профиля"""
    db_tool = ProfileTool(**profile_tool.model_dump())
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool  # Возвращаем созданный объект


@router.post("/profile-tool/{tool_id}/component", response_model=ProfileToolComponentResponse)
def create_profile_tool_component(
    tool_id: int,
    component: ProfileToolComponentCreate,
    db: Session = Depends(get_db)
):
    """Создать новый компонент инструмента профиля"""
    # Проверяем, существует ли инструмент
    db_tool = db.query(ProfileTool).filter(ProfileTool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Profile tool not found")

    db_component = ProfileToolComponent(**component.model_dump())
    db_component.tool_id = tool_id
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component


# =============================================================================
# ROUTER.PUT
# =============================================================================

@router.put("/profile-tool/{tool_id}", response_model=ProfileToolResponse)
def update_profile_tool(
    tool_id: int,
    tool: ProfileToolUpdate,
    db: Session = Depends(get_db)
):
    """Обновить инструмент профиля"""
    db_tool = db.query(ProfileTool).filter(ProfileTool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Profile tool not found")

    # Используем exclude_unset, чтобы обновить только переданные поля
    update_data = tool.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tool, field, value)

    db.commit()
    db.refresh(db_tool)
    return db_tool


# =============================================================================
# ROUTER.DELETE
# =============================================================================

@router.delete("/profile/{profile_id}/profile-tool")
def delete_profile_tool_by_profile(profile_id: int, db: Session = Depends(get_db)):
    """Удалить все инструменты профиля и их компоненты по ID профиля"""
    tools = db.query(ProfileTool).filter(ProfileTool.profile_id == profile_id).all()
    if not tools:
        raise HTTPException(status_code=404, detail="Инструменты не найдены")

    for tool in tools:
        # Удаляем сначала компоненты
        db.query(ProfileToolComponent).filter(ProfileToolComponent.tool_id == tool.id).delete()
        db.delete(tool)

    db.commit()
    return {"detail": f"Удалены все инструменты и компоненты профиля {profile_id}"}


@router.delete("/profile-tool/{tool_id}", response_model=dict)
def delete_profile_tool(tool_id: int, db: Session = Depends(get_db)):
    """Удалить инструмент профиля по ID"""
    tool = db.query(ProfileTool).filter(ProfileTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Инструмент не найден")

    db.delete(tool)
    db.commit()
    return {"detail": "Инструмент удален успешно"}


@router.delete("/profile-tool/{tool_id}/component", response_model=dict)
def delete_all_profile_tool_components(tool_id: int, db: Session = Depends(get_db)):
    """Удалить все компоненты инструмента профиля по ID инструмента"""
    components = db.query(ProfileToolComponent).filter(ProfileToolComponent.tool_id == tool_id).all()
    if not components:
        raise HTTPException(status_code=404, detail="Компоненты не найдены")

    for comp in components:
        db.delete(comp)
    db.commit()
    return {"detail": f"Удалены все компоненты инструмента {tool_id}"}


@router.delete("/profile-tool/component/{component_id}", response_model=dict)
def delete_profile_tool_component_by_id(component_id: int, db: Session = Depends(get_db)):
    """Удалить компонент инструмента профиля по ID"""
    component = db.query(ProfileToolComponent).filter(ProfileToolComponent.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Компонент не найден")

    db.delete(component)
    db.commit()
    return {"detail": "Компонент удален успешно"}