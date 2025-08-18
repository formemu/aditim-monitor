"""API routes for profile tool"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile_tool import ModelProfileTool , ModelProfileToolComponent
from ..schemas.profile_tool import (
    SchemaProfileToolCreate,
    SchemaProfileToolResponse,
    SchemaProfileToolComponentCreate,
    SchemaProfileToolUpdate,
    SchemaProfileToolComponentResponse,
)

router = APIRouter(prefix="/api", tags=["profile-tool"])

# =============================================================================
# ROUTER.GET
# =============================================================================

@router.get("/profile-tool", response_model=List[SchemaProfileToolResponse])
def get_profile_tool(db: Session = Depends(get_db)):
    """Получить все инструменты профиля"""
    return db.query(ModelProfileTool).all()


@router.get("/profile-tool/{tool_id}/component", response_model=List[SchemaProfileToolComponentResponse])
def get_profile_tool_component(tool_id: int, db: Session = Depends(get_db)):
    """Получить все компоненты инструмента профиля"""
    return db.query(ModelProfileToolComponent).filter(ModelProfileToolComponent.tool_id == tool_id).all()


# =============================================================================
# ROUTER.POST
# =============================================================================

@router.post("/profile-tool", response_model=SchemaProfileToolResponse)
def create_profile_tool(profile_tool: SchemaProfileToolCreate, db: Session = Depends(get_db)):
    """Создать новый инструмент профиля"""
    try:
        tool = ModelProfileTool(
            profile_id=profile_tool.profile_id,
            dimension_id=profile_tool.dimension_id,
            description=profile_tool.description
        )
        db.add(tool)
        db.commit()
        db.refresh(tool)
        return tool
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Не удалось создать инструмент: " + str(e))


@router.post("/profile-tool/{tool_id}/component", response_model=SchemaProfileToolComponentResponse)
def create_profile_tool_component(tool_id: int, component: SchemaProfileToolComponentCreate, db: Session = Depends(get_db)):
    """Создать новый компонент инструмента профиля"""
    try:
        print(component)
        db_component = ModelProfileToolComponent(
            tool_id=tool_id,
            type_id=component.type_id,
            status_id=component.status_id,
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

# =============================================================================
# ROUTER.PATCH
# =============================================================================
@router.patch("/profile-tool/{tool_id}", response_model=SchemaProfileToolResponse)
def update_profile_tool( tool_id: int, tool: SchemaProfileToolUpdate, db: Session = Depends(get_db)):
    """обновить инструмент профиля"""
    db_tool = db.get(ModelProfileTool, tool_id)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
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
    """Удалить все инструменты профиля (и их компоненты) по ID профиля"""
    deleted_count = db.query(ModelProfileTool).filter(ModelProfileTool.profile_id == profile_id).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Инструменты не найдены")
    db.commit()
    return {"detail": f"Удалены все инструменты и компоненты профиля {profile_id}"}

@router.delete("/profile-tool/{tool_id}", response_model=dict)
def delete_profile_tool(tool_id: int, db: Session = Depends(get_db)):
    """Удалить инструмент профиля по ID"""
    tool = db.get(ModelProfileTool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Инструмент не найден")
    db.delete(tool)
    db.commit()
    return {"detail": "Инструмент и его компоненты удалены успешно"}

@router.delete("/profile-tool/{tool_id}/component", response_model=dict)
def delete_all_profile_tool_components(tool_id: int, db: Session = Depends(get_db)):
    """Удалить все компоненты инструмента (без удаления инструмента)"""
    deleted_count = db.query(ModelProfileToolComponent).filter(ModelProfileToolComponent.tool_id == tool_id).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Компоненты не найдены")
    db.commit()
    return {"detail": f"Удалены все компоненты инструмента {tool_id}"}

@router.delete("/profile-tool/component/{component_id}", response_model=dict)
def delete_profile_tool_component_by_id(component_id: int, db: Session = Depends(get_db)):
    """Удалить компонент инструмента по ID"""
    component = db.get(ModelProfileToolComponent, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Компонент не найден")
    db.delete(component)
    db.commit()
    return {"detail": "Компонент удален успешно"}