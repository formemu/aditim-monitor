"""Pydantic schemas for profile_tool"""
from typing import Optional
from pydantic import BaseModel, ConfigDict
from ..schemas.directory import DirToolDimension


# === PROFILE TOOL SCHEMAS ===

class ProfileToolBase(BaseModel):
    """Базовая модель: общие поля для профиля инструмента (без id)"""
    description: Optional[str] = None
    dimension: Optional[DirToolDimension] = None

class ProfileToolCreate(ProfileToolBase):
    """Создание профиля инструмента — клиент не передаёт id"""
    pass  # Все поля из Base (обязательные/опциональные)

class ProfileToolUpdate(BaseModel):
    """Обновление профиля — все поля опциональны для частичного обновления"""
    description: Optional[str] = None
    dimension: Optional[DirToolDimension] = None

class ProfileToolResponse(ProfileToolBase):
    """Ответ API — включает id и поддержку ORM"""
    id: int
    dimension: DirToolDimension  # ← вложенный объект
    model_config = ConfigDict(from_attributes=True)

# === PROFILE TOOL COMPONENT SCHEMAS ===

class ProfileToolComponentBase(BaseModel):
    """Базовая модель компонента (без id)"""
    component_name: str
    description: Optional[str] = None
    variant: Optional[str] = None
    profile_tool_id: int  # Связь с профилем

class ProfileToolComponentCreate(ProfileToolComponentBase):
    """Создание компонента — без id, но с profile_tool_id"""
    pass

class ProfileToolComponentUpdate(BaseModel):
    """Частичное обновление компонента"""
    component_name: Optional[str] = None
    description: Optional[str] = None
    variant: Optional[str] = None
    profile_tool_id: Optional[int] = None  # редко, но может меняться

class ProfileToolComponentResponse(ProfileToolComponentBase):
    """Ответ с компонентом — включает id и поддержку ORM"""
    id: int
    model_config = ConfigDict(from_attributes=True)