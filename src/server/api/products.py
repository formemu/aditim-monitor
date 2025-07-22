"""
API routes for products and profiles
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
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
@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    """Get all products"""
    return db.query(Product).all()


@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Profiles
@router.get("/profiles", response_model=List[ProfileResponse])
def get_profiles(db: Session = Depends(get_db)):
    """Get all profiles"""
    return db.query(Profile).all()


@router.post("/profiles", response_model=ProfileResponse)
def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """Create a new profile"""
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


@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get profile by ID"""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


# Product Components
@router.get("/products/{product_id}/components", response_model=List[ProductComponentResponse])
def get_product_components(product_id: int, db: Session = Depends(get_db)):
    """Get all components for a product"""
    return db.query(ProductComponent).filter(ProductComponent.product_id == product_id).all()


@router.post("/products/{product_id}/components", response_model=ProductComponentResponse)
def create_product_component(
    product_id: int, 
    component: ProductComponentCreate, 
    db: Session = Depends(get_db)
):
    """Create a new product component"""
    component.product_id = product_id
    db_component = ProductComponent(**component.dict())
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component


# Profile Tools
@router.get("/profile-tools", response_model=List[dict])
def get_profile_tools(db: Session = Depends(get_db)):
    """Get all profile tools with profile information"""
    tools = db.query(ProfileTool).all()
    result = []
    for tool in tools:
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


@router.get("/profile-tools/{tool_id}/components", response_model=List[dict])
def get_profile_tool_components(tool_id: int, db: Session = Depends(get_db)):
    """Get components of a profile tool"""
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


@router.post("/profile-tools", response_model=dict)
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


@router.post("/profile-tools/{tool_id}/components", response_model=dict)
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
