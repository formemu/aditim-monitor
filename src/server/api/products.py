"""
API routes for products and profiles
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session
import base64

from ..database import get_db
from ..models.products import Product, Profile, ProductComponent
from ..models.profile_tools import ProfileTool, ProfileToolComponent, ToolDimension, ComponentType, ComponentStatus
from ..schemas.products import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProfileCreate, ProfileUpdate, ProfileResponse,
    ProductComponentCreate, ProductComponentResponse
)

router = APIRouter(prefix="/api", tags=["products", "profiles"])


# Products
@router.get("/product", response_model=List[ProductResponse])
def get_product(db: Session = Depends(get_db)):
    """Get all product (единственное число)"""
    return db.query(Product).all()


@router.post("/product", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product (единственное число)"""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/product/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID (единственное число)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Profiles
@router.get("/profile", response_model=List[ProfileResponse])
def get_profile(db: Session = Depends(get_db)):
    """Get all profile (единственное число)"""
    return db.query(Profile).all()


@router.post("/profile", response_model=ProfileResponse)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """Create a new profile (единственное число)"""
    profile_data = profile.dict()
    
    # Convert base64 image to binary if provided
    if profile_data.get("sketch"):
        try:
            # Remove data URI prefix if present (data:image/png;base64,...)
            sketch_data = profile_data["sketch"]
            if sketch_data.startswith("data:"):
                sketch_data = sketch_data.split(",", 1)[1]
            
            # Decode base64 to binary
            profile_data["sketch"] = base64.b64decode(sketch_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")
    
    db_profile = Profile(**profile_data)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/profile/{profile_id}", response_model=ProfileResponse)
def get_profile_by_id(profile_id: int, db: Session = Depends(get_db)):
    """Get profile by ID (единственное число)"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


# Product Components
@router.get("/product/{product_id}/component", response_model=List[ProductComponentResponse])
def get_product_component(product_id: int, db: Session = Depends(get_db)):
    """Get all component for a product (единственное число)"""
    return db.query(ProductComponent).filter(ProductComponent.product_id == product_id).all()


@router.post("/product/{product_id}/component", response_model=ProductComponentResponse)
def create_product_component(
    product_id: int, 
    component: ProductComponentCreate, 
    db: Session = Depends(get_db)
):
    """Create a new product component (единственное число)"""
    component.product_id = product_id
    db_component = ProductComponent(**component.dict())
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component


# Profile Tools
@router.get("/profile-tool", response_model=List[dict])
def get_profile_tool(db: Session = Depends(get_db)):
    """Get all profile tool with profile information (единственное число)"""
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
    """Get component of a profile tool (единственное число)"""
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
    """Create new profile tool (единственное число)"""
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
        dimension_obj = db.query(ToolDimension).filter(ToolDimension.dimension == dimension).first()
        
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
    """Create new profile tool component (единственное число)"""
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
        component_type = db.query(ComponentType).filter(ComponentType.id == component_type_id).first()
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


# === ENDPOINT: Удаление всех инструментов профиля и их компонентов по profile_id ===
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



# === ENDPOINT: Удаление профиля по profile_id ===
@router.delete("/profile/{profile_id}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """Удалить профиль по profile_id (единственное число)"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return {"success": True, "deleted": 1}

# === ENDPOINT: Удаление всех компонентов инструмента профиля по tool_id ===
@router.delete("/profile-tool/{tool_id}/component", response_model=dict, status_code=status.HTTP_200_OK)
def delete_profile_tool_component(tool_id: int, db: Session = Depends(get_db)):
    """Удалить все компоненты инструмента профиля по tool_id (единственное число)"""
    list_component = db.query(ProfileToolComponent).filter(ProfileToolComponent.tool_id == tool_id).all()
    if not list_component:
        return {"success": True, "deleted": 0}

    count_deleted = 0
    for component in list_component:
        db.delete(component)
        count_deleted += 1
    db.commit()
    return {"success": True, "deleted": count_deleted}


