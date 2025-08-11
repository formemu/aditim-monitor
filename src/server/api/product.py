"""
API routes for products
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.product import Product, ProductComponent
from ..schemas.product import ( ProductCreate, ProductResponse, ProductComponentCreate, ProductComponentResponse, ProductUpdate )

router = APIRouter(prefix="/api", tags=["products"])

# =============================================================================
# ROUTER.GET
# =============================================================================

@router.get("/product")
def get_product(db: Session = Depends(get_db)):
    """Получить все продукты"""
    return db.query(Product).all()

@router.get("/product/{product_id}/component")
def get_product_component(product_id: int, db: Session = Depends(get_db)):
    """Получить все компоненты для продукта"""
    return db.query(ProductComponent).filter(ProductComponent.product_id == product_id).all()

# =============================================================================
# ROUTER.POST
# =============================================================================
@router.post("/product")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Создать новый продукт"""
    product = Product(**product.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.post("/product/{product_id}/component")
def create_product_component(product_id: int, component: ProductComponentCreate, db: Session = Depends(get_db)):
    component = ProductComponent(**component.model_dump()) 
    component.product_id = product_id
    db.add(component)
    db.commit()
    db.refresh(component)

# =============================================================================
# ROUTER.PUT
# =============================================================================
@router.put("/product/{product_id}")
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Обновить данные продукта"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        product_data = product.model_dump()
        for field, value in product_data.items():
            if value:  # Только обновляем поля, которые не None
                setattr(product, field, value)
        db.commit()
        db.refresh(product)
    else:
        raise HTTPException(status_code=404, detail="Product not found")

# =============================================================================
# ROUTER.DELETE
# =============================================================================
@router.delete("/product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return {"detail": "Изделие удалено успешно"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@router.delete("/product/{product_id}/component/")
def delete_product_component(product_id: int, db: Session = Depends(get_db)):
    """Удалить все компоненты продукта по ID продукта"""
    component = db.query(ProductComponent).filter(ProductComponent.product_id == product_id).all()
    if component:
        for comp in component:
            db.delete(comp)
        db.commit()
        return {"detail": f"Удалены все компоненты"}
    else:
        raise HTTPException(status_code=404, detail="Компоненты не найдены")

@router.delete("/product/component/{component_id}")
def delete_product_component(component_id: int, db: Session = Depends(get_db)):
    """Удалить компонент изделия по ID"""
    component = db.query(ProductComponent).filter(ProductComponent.id == component_id).first()
    if component:
        db.delete(component)
        db.commit()
        return {"detail": "Компонент удален успешно"}
    else:
        raise HTTPException(status_code=404, detail="Компонент не найден")

    


