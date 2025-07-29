"""
API routes for products
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.product import Product, ProductComponent
from ..schemas.product import (
    ProductCreate, ProductResponse,
    ProductComponentCreate, ProductComponentResponse
)

router = APIRouter(prefix="/api", tags=["products"])


@router.get("/product", response_model=List[ProductResponse])
def get_product(db: Session = Depends(get_db)):
    """Get all product """
    return db.query(Product).all()


@router.post("/product", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product """
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# @router.get("/product/{product_id}", response_model=ProductResponse) # НЕ ИСПОЛЬЗУЕТСЯ
# def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
#     """Get product by ID """
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product


@router.get("/product/{product_id}/component", response_model=List[ProductComponentResponse])
def get_product_component(product_id: int, db: Session = Depends(get_db)):
    """Get all component for a product """
    return db.query(ProductComponent).filter(ProductComponent.product_id == product_id).all()


@router.post("/product/{product_id}/component", response_model=ProductComponentResponse)
def create_product_component(
    product_id: int, 
    component: ProductComponentCreate, 
    db: Session = Depends(get_db)):
    # Создаем словарь данных и добавляем product_id
    component_data = component.dict()
    component_data['product_id'] = product_id
    
    db_component = ProductComponent(**component_data)
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component


