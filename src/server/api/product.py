"""API routes for products"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.product import ModelProduct, ModelProductComponent
from ..schemas.product import (
    SchemaProductCreate,
    SchemaProductUpdate,
    SchemaProductResponse,
    SchemaProductComponentCreate,
    SchemaProductComponentResponse,
)

router = APIRouter(prefix="/api", tags=["products"])

# =============================================================================
# ROUTER.GET
# =============================================================================
@router.get("/product", response_model=List[SchemaProductResponse])
def get_product(db: Session = Depends(get_db)):
    """Получить все продукты"""
    return db.query(ModelProduct).all()

@router.get("/product/{product_id}/component", response_model=List[SchemaProductComponentResponse])
def get_product_component(product_id: int, db: Session = Depends(get_db)):
    """Получить все компоненты для продукта"""
    return db.query(ModelProductComponent).filter(ModelProductComponent.product_id == product_id).all()

# =============================================================================
# ROUTER.POST
# =============================================================================
@router.post("/product", response_model=SchemaProductResponse)
def create_product(product: SchemaProductCreate, db: Session = Depends(get_db)):
    """Создать новый продукт"""
    db_product = ModelProduct(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.post("/product/{product_id}/component", response_model=SchemaProductComponentResponse)
def create_product_component(product_id: int, component: SchemaProductComponentCreate, db: Session = Depends(get_db)):
    """Создать компонент для продукта"""
    try:
        db_component = ModelProductComponent(
            product_id=product_id,
            name = component.name,
            description = component.description,
            quantity = component.quantity
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
@router.patch("/product/{product_id}", response_model=SchemaProductResponse)
def update_product(product_id: int, product: SchemaProductUpdate, db: Session = Depends(get_db)):
    """Обновить данные продукта"""
    db_product = db.get(ModelProduct, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Продукт не найден")
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value) 
    db.commit()
    db.refresh(db_product)
    return db_product

# =============================================================================
# ROUTER.DELETE
# =============================================================================
@router.delete("/product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Удалить продукт и все его компоненты"""
    db_product = db.query(ModelProduct).filter(ModelProduct.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Удаляем сначала компоненты (из-за внешнего ключа)
    db.query(ModelProductComponent).filter(ModelProductComponent.product_id == product_id).delete()
    db.delete(db_product)
    db.commit()
    return {"detail": "Продукт и его компоненты удалены успешно"}

@router.delete("/product/{product_id}/component")
def delete_all_product_component(product_id: int, db: Session = Depends(get_db)):
    """Удалить все компоненты продукта по ID продукта"""
    deleted_count = db.query(ModelProductComponent).filter(ModelProductComponent.product_id == product_id).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Компоненты не найдены")
    db.commit()
    return {"detail": f"Удалены все компоненты продукта {product_id}"}

@router.delete("/product/component/{component_id}")
def delete_product_component_by_id(component_id: int, db: Session = Depends(get_db)):
    """Удалить компонент изделия по ID"""
    component = db.query(ModelProductComponent).filter(ModelProductComponent.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Компонент не найден")

    db.delete(component)
    db.commit()
    return {"detail": "Компонент удален успешно"}