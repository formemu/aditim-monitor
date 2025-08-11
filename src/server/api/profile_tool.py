"""API routes for profile tool"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile_tool import ProfileTool, ProfileToolComponent
from ..schemas.profile_tool import (ProfileToolCreate, ProfileToolUpdate, ProfileToolComponentCreate)

router = APIRouter(prefix="/api", tags=["profile-tool"])


# =============================================================================
# ROUTER.GET
# =============================================================================
@router.get("/profile-tool")
def get_profile_tool(db: Session = Depends(get_db)):
    """Получить все инструменты профиля"""
    return db.query(ProfileTool).all()

@router.get("/profile-tool/{tool_id}/component")
def get_profile_tool_component(tool_id: int, db: Session = Depends(get_db)):
    """Получить все компоненты инструмента профиля"""
    return db.query(ProfileToolComponent).filter(ProfileToolComponent.tool_id == tool_id).all()

# =============================================================================
# ROUTER.POST
# =============================================================================
@router.post("/profile-tool")
def create_profile_tool(profile_tool: ProfileToolCreate, db: Session = Depends(get_db)):
    """Создать новый инструмент профиля"""
    profile_tool = ProfileTool(**profile_tool.model_dump())
    db.add(profile_tool)
    db.commit()
    db.refresh(profile_tool)

@router.post("/profile-tool/{tool_id}/component")
def create_profile_tool_component(tool_id: int, component: ProfileToolComponentCreate, db: Session = Depends(get_db)):
    """Создать новый компонент инструмента профиля"""
    component = ProfileToolComponent(**component.model_dump())
    component.tool_id = tool_id
    db.add(component)
    db.commit()
    db.refresh(component)

# =============================================================================
# ROUTER.PUT
# =============================================================================
@router.put("/profile-tool/{tool_id}")
def update_profile_tool(tool_id: int, tool: ProfileToolUpdate, db: Session = Depends(get_db)):
    """Обновить инструмент профиля"""
    db_tool = db.query(ProfileTool).filter(ProfileTool.id == tool_id).first()
    if db_tool:
        tool_data = tool.model_dump()
        for field, value in tool_data.items():
            if value:  # Только обновляем поля, которые не None
                setattr(db_tool, field, value)
        db.commit()
        db.refresh(db_tool)
    else:
        raise HTTPException(status_code=404, detail="Инструмент профиля не найден")

# =============================================================================
# ROUTER.DELETE
# =============================================================================
@router.delete("profile/{profile_id}/profile-tool/")
def delete_profile_tool_by_profile(profile_id: int, db: Session = Depends(get_db)):
    """Удалить все инструменты профиля и их компоненты по ID профиля"""
    tool = db.query(ProfileTool).filter(ProfileTool.profile_id == profile_id).all()
    if tool:
        for t in tool:
            component = db.query(ProfileToolComponent).filter(ProfileToolComponent.tool_id == tool.id).all()
            for comp in component:
                db.delete(comp)
            db.delete(t)
        db.commit()
        return {"detail": f"Удалены все инструменты и компоненты"}
    else:
        raise HTTPException(status_code=404, detail="Инструменты не найдены")

@router.delete("/profile-tool/{tool_id}")
def delete_profile_tool(tool_id: int, db: Session = Depends(get_db)):
    """Удалить инструмент профиля по ID"""
    tool = db.query(ProfileTool).filter(ProfileTool.id == tool_id).first()
    if tool:
        db.delete(tool)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Инструмент не найден")

@router.delete("/profile-tool/{tool_id}/component/")
def delete_profile_tool_component(tool_id: int, db: Session = Depends(get_db)):
    """Удалить все компоненты инструмента профиля по ID инструмента"""
    component = db.query(ProfileToolComponent).filter(ProfileToolComponent.tool_id == tool_id).all()
    if component:
        for comp in component:
            db.delete(comp)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Компоненты не найдены")

@router.delete("/profile-tool/component/{component_id}")
def delete_profile_tool_component_by_id(component_id: int, db: Session = Depends(get_db)):
    """Удалить компонент инструмента профиля по ID"""
    component = db.query(ProfileToolComponent).filter(ProfileToolComponent.id == component_id).first()
    if component:
        db.delete(component)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Компонент не найден")