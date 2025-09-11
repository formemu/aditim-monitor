"""Pydantic schemas for product"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .directory import SchemaDirDepartment


# === PRODUCT SCHEMAS ===

class SchemaProductBase(BaseModel):
    """Общие поля для продукта (без id)"""
    name: str
    department_id: int
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SchemaProductCreate(SchemaProductBase):
    """Схема для создания продукта — без id, все поля обязательны (кроме опциональных)"""
    pass 

class SchemaProductUpdate(BaseModel):
    """Схема для частичного обновления — все поля опциональны"""
    name: Optional[str] = None
    description: Optional[str] = None
    department: SchemaDirDepartment = None

class SchemaProductResponse(SchemaProductBase):
    """Схема для ответа — включает id и поддержку ORM"""
    id: int
    department: SchemaDirDepartment = None
    component: List["SchemaProductComponentResponse"] = []


# === PRODUCT COMPONENT SCHEMAS ===

class SchemaProductComponentBase(BaseModel):
    """Общие поля для компонента продукта (без id)"""
    name: str
    description: Optional[str] = None
    quantity: int = 1

    model_config = ConfigDict(from_attributes=True)


class SchemaProductComponentCreate(SchemaProductComponentBase):
    pass


class SchemaProductComponentUpdate(BaseModel):
    """Частичное обновление компонента"""
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None


class SchemaProductComponentResponse(SchemaProductComponentBase):
    id: int
    product_id: int
