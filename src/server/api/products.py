"""
API routes for products and profiles
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import base64

from ..database import get_db
from ..models.products import Product, Profile, ProductComponent, ProfileComponent
from ..schemas.products import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProfileCreate, ProfileUpdate, ProfileResponse,
    ProductComponentCreate, ProductComponentResponse,
    ProfileComponentCreate, ProfileComponentResponse
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
    return db.query(ProductComponent).filter(ProductComponent.id_product == product_id).all()


@router.post("/products/{product_id}/components", response_model=ProductComponentResponse)
def create_product_component(
    product_id: int, 
    component: ProductComponentCreate, 
    db: Session = Depends(get_db)
):
    """Create a new product component"""
    component.id_product = product_id
    db_component = ProductComponent(**component.dict())
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component


# Profile Components
@router.get("/profiles/{profile_id}/components", response_model=List[ProfileComponentResponse])
def get_profile_components(profile_id: int, db: Session = Depends(get_db)):
    """Get all components for a profile"""
    return db.query(ProfileComponent).filter(ProfileComponent.id_profile == profile_id).all()


@router.post("/profiles/{profile_id}/components", response_model=ProfileComponentResponse)
def create_profile_component(
    profile_id: int, 
    component: ProfileComponentCreate, 
    db: Session = Depends(get_db)
):
    """Create a new profile component"""
    component.id_profile = profile_id
    db_component = ProfileComponent(**component.dict())
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component
