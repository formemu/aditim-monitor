"""API routes for products"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.product import Product, ProductComponent
from ..schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductComponentCreate,
    ProductComponentResponse,
)

router = APIRouter(prefix="/api", tags=["products"])

# =============================================================================
# ROUTER.GET
# =============================================================================
@router.get("/product", response_model=List[ProductResponse])
def get_product(db: Session = Depends(get_db)):
    """Получить все продукты"""
    return db.query(Product).all()

@router.get("/product/{product_id}/component", response_model=List[ProductComponentResponse])
def get_product_component(product_id: int, db: Session = Depends(get_db)):
    """Получить все компоненты для продукта"""
    return db.query(ProductComponent).filter(ProductComponent.product_id == product_id).all()

# =============================================================================
# ROUTER.POST
# =============================================================================
@router.post("/product", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Создать новый продукт"""
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.post("/product/{product_id}/component", response_model=ProductComponentResponse)
def create_product_component(product_id: int, component: ProductComponentCreate, db: Session = Depends(get_db)):
    """Создать компонент для продукта"""
    # Проверяем, существует ли продукт
    if not db.query(Product).filter(Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")

    db_component = ProductComponent(**component.model_dump())
    db_component.product_id = product_id
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component

# =============================================================================
# ROUTER.PUT
# =============================================================================
@router.put("/product/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Обновить данные продукта"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Обновляем только ненулевые поля (или используй exclude_unset)
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)  # Обновляем db_product, а не product!

    db.commit()
    db.refresh(db_product)
    return db_product

# =============================================================================
# ROUTER.DELETE
# =============================================================================
@router.delete("/product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Удалить продукт и все его компоненты"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Удаляем сначала компоненты (из-за внешнего ключа)
    db.query(ProductComponent).filter(ProductComponent.product_id == product_id).delete()
    db.delete(db_product)
    db.commit()
    return {"detail": "Продукт и его компоненты удалены успешно"}

@router.delete("/product/{product_id}/component")
def delete_all_product_components(product_id: int, db: Session = Depends(get_db)):
    """Удалить все компоненты продукта по ID продукта"""
    components = db.query(ProductComponent).filter(ProductComponent.product_id == product_id).all()
    if not components:
        raise HTTPException(status_code=404, detail="Компоненты не найдены")

    for comp in components:
        db.delete(comp)
    db.commit()
    return {"detail": f"Удалены все компоненты продукта {product_id}"}

@router.delete("/product/component/{component_id}")
def delete_product_component_by_id(component_id: int, db: Session = Depends(get_db)):
    """Удалить компонент изделия по ID"""
    component = db.query(ProductComponent).filter(ProductComponent.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Компонент не найден")

    db.delete(component)
    db.commit()
    return {"detail": "Компонент удален успешно"}