"""Pydantic schemas for product"""
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .directory import DirDepartment


# === PRODUCT SCHEMAS ===

class ProductBase(BaseModel):
    """Общие поля для продукта (без id)"""
    name: str
    description: Optional[str] = None
    department: DirDepartment = None

class ProductCreate(ProductBase):
    """Схема для создания продукта — без id, все поля обязательны (кроме опциональных)"""
    pass  # Можно добавить валидацию позже


class ProductUpdate(BaseModel):
    """Схема для частичного обновления — все поля опциональны"""
    name: Optional[str] = None
    description: Optional[str] = None
    department: DirDepartment = None


class ProductResponse(ProductBase):
    """Схема для ответа — включает id и поддержку ORM"""
    id: int
    model_config = ConfigDict(from_attributes=True)


# === PRODUCT COMPONENT SCHEMAS ===

class ProductComponentBase(BaseModel):
    """Общие поля для компонента продукта (без id)"""
    name: str
    description: Optional[str] = None
    quantity: int = 1


class ProductComponentCreate(ProductComponentBase):
    """Создание компонента — без id"""
    product_id: int  # ← важно: компонент привязан к продукту


class ProductComponentUpdate(BaseModel):
    """Частичное обновление компонента"""
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None


class ProductComponentResponse(ProductComponentBase):
    """Ответ с компонентом — включает id и поддержку ORM"""
    id: int
    model_config = ConfigDict(from_attributes=True)