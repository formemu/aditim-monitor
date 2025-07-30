"""
API routes for profile tools
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile import Profile
from ..models.profile_tool import ProfileTool, ProfileToolComponent
from ..models.directory import DirToolDimension, DirComponentType

router = APIRouter(prefix="/api", tags=["profile-tool"])


@router.get("/profile-tool", response_model=List[dict])
def get_profile_tool(db: Session = Depends(get_db)):
    """Get all profile tool with profile information"""
    list_tool = db.query(ProfileTool).all()
    result = []
    for tool in list_tool:
        result.append({
            "id": tool.id,
            "profile_id": tool.profile_id,
            "profile_article": tool.profile.article if tool.profile else "Неизвестно",
            "profile_description": tool.profile.description if tool.profile else "",
            "dimension": tool.dimension.dimension if tool.dimension else "Неизвестно",
            "description": tool.description or "",
            "components_count": len(tool.component)
        })
    return result


@router.get("/profile-tool/{tool_id}/component", response_model=List[dict])
def get_profile_tool_component(tool_id: int, db: Session = Depends(get_db)):
    """Get component of a profile tool"""
    tool = db.query(ProfileTool).filter(ProfileTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Profile tool not found")
    
    result = []
    for component in tool.component:
        result.append({
            "id": component.id,
            "component_type": component.component_type.name if component.component_type else "Неизвестно",
            "variant": component.variant,
            "description": component.description or "",
            "status": component.status.name if component.status else "Неизвестно"
        })
    return result


@router.post("/profile-tool", response_model=dict)
def create_profile_tool(tool_data: dict, db: Session = Depends(get_db)):
    """Create new profile tool"""
    try:
        # Проверяем обязательные поля
        profile_id = tool_data.get("profile_id")
        dimension = tool_data.get("dimension")
        
        if not profile_id:
            raise HTTPException(status_code=400, detail="profile_id is required")
        if not dimension:
            raise HTTPException(status_code=400, detail="dimension is required")
        
        # Проверяем что профиль существует
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Ищем размерность в справочнике (если нужно)
        dimension_obj = db.query(DirToolDimension).filter(DirToolDimension.dimension == dimension).first()
        
        # Создаем инструмент профиля
        new_tool = ProfileTool(
            profile_id=profile_id,
            dimension_id=dimension_obj.id if dimension_obj else None,
            description=tool_data.get("description")
        )
        
        db.add(new_tool)
        db.commit()
        db.refresh(new_tool)
        
        return {
            "id": new_tool.id,
            "profile_id": new_tool.profile_id,
            "dimension": dimension,
            "description": new_tool.description,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating profile tool: {str(e)}")


@router.post("/profile-tool/{tool_id}/component", response_model=dict)
def create_profile_tool_component(tool_id: int, component_data: dict, db: Session = Depends(get_db)):
    """Create new profile tool component"""
    try:
        # Проверяем что инструмент существует
        tool = db.query(ProfileTool).filter(ProfileTool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Profile tool not found")
        
        # Проверяем обязательные поля
        component_type_id = component_data.get("component_type_id")
        if not component_type_id:
            raise HTTPException(status_code=400, detail="component_type_id is required")
        
        # Проверяем что тип компонента существует
        component_type = db.query(DirComponentType).filter(DirComponentType.id == component_type_id).first()
        if not component_type:
            raise HTTPException(status_code=404, detail="Component type not found")
        
        # Создаем компонент
        new_component = ProfileToolComponent(
            tool_id=tool_id,
            component_type_id=component_type_id,
            variant=component_data.get("variant", 1),
            description=component_data.get("description"),
            status_id=component_data.get("status_id", 1)  # По умолчанию статус "В разработке"
        )
        
        db.add(new_component)
        db.commit()
        db.refresh(new_component)
        
        return {
            "id": new_component.id,
            "tool_id": new_component.tool_id,
            "component_type_id": new_component.component_type_id,
            "variant": new_component.variant,
            "description": new_component.description,
            "status_id": new_component.status_id,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating component: {str(e)}")


@router.delete("/profile-tool/by-profile/{profile_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_profile_tool_by_profile(profile_id: int, db: Session = Depends(get_db)):
    """Удалить все инструменты профиля и их компоненты по profile_id (единственное число)"""
    list_tool = db.query(ProfileTool).filter(ProfileTool.profile_id == profile_id).all()
    if not list_tool:
        return {"success": True, "deleted": 0}

    count_tool_deleted = 0
    count_component_deleted = 0
    for tool in list_tool:
        list_component = db.query(ProfileToolComponent).filter(ProfileToolComponent.tool_id == tool.id).all()
        for component in list_component:
            db.delete(component)
            count_component_deleted += 1
        db.delete(tool)
        count_tool_deleted += 1
    db.commit()
    return {"success": True, "deleted_tools": count_tool_deleted, "deleted_components": count_component_deleted}


@router.delete("/profile-tool/{tool_id}/component", response_model=dict, status_code=status.HTTP_200_OK)
def delete_profile_tool_component(tool_id: int, db: Session = Depends(get_db)):
    """Удалить все компоненты инструмента профиля по tool_id"""
    list_component = db.query(ProfileToolComponent).filter(ProfileToolComponent.tool_id == tool_id).all()
    if not list_component:
        return {"success": True, "deleted": 0}

    count_deleted = 0
    for component in list_component:
        db.delete(component)
        count_deleted += 1
    db.commit()
    return {"success": True, "deleted": count_deleted}
