"""Схемы для заготовок"""
from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from .directory import SchemaDirBlankMaterial


class SchemaBlankBase(BaseModel):
    """Базовая схема заготовки"""
    order: Optional[int] = None
    material_id: Optional[int] = None
    profiletool_component_id: Optional[int] = None
    product_component_id: Optional[int] = None
    date_order: Optional[date] = None
    date_arrival: Optional[date] = None
    date_product: Optional[date] = None
    blank_width: Optional[int] = None
    blank_height: Optional[int] = None
    blank_length: Optional[int] = None
    product_width: Optional[int] = None
    product_height: Optional[int] = None
    product_length: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SchemaBlankCreate(SchemaBlankBase):
    """Схема создания заготовки"""
    pass


class SchemaBlankBulkCreate(SchemaBlankBase):
    """Схема массового создания заготовок одного типа"""
    quantity: int = 1  # Количество заготовок для создания


class SchemaBlankUpdate(SchemaBlankBase):
    """Схема обновления заготовки"""
    pass


class SchemaBlankResponse(SchemaBlankBase):
    """Схема ответа с заготовкой"""
    id: int
    material: Optional[SchemaDirBlankMaterial] = None