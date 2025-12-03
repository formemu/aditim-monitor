"""Pydantic schemas for profiletool"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from ..schemas.directory import SchemaDirToolDimension, SchemaDirComponentStatus, SchemaDirProfiletoolComponentType
from datetime import date


# === PROFILE TOOL SCHEMAS ===
class SchemaProfileToolBase(BaseModel):
    profile_id: int
    dimension_id: int
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SchemaProfileToolCreate(SchemaProfileToolBase):
    pass

class SchemaProfileToolUpdate(BaseModel):
    dimension_id: Optional[int] = None
    description: Optional[str] = None

class SchemaProfileToolResponse(SchemaProfileToolBase):
    id: int
    profile: Optional["SchemaProfileBase"] = None
    dimension: Optional[SchemaDirToolDimension] = None
    component: List["SchemaProfileToolComponentResponse"] = []


# === PROFILE TOOL COMPONENT SCHEMAS ===


class ProfileToolComponentBase(BaseModel):
    """Базовая модель компонента (без id)"""
    type_id: int
    variant: int
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class SchemaProfileToolComponentCreate(ProfileToolComponentBase):
    pass

class ProfileToolComponentUpdate(BaseModel):
    """Частичное обновление компонента"""
    type_id: int
    description: Optional[str] = None
    variant: Optional[int] = None

class SchemaProfileToolComponentResponse(ProfileToolComponentBase):
    id: int
    profiletool_id: int
    type: Optional[SchemaDirProfiletoolComponentType] = None
    history: List["SchemaProfileToolComponentHistoryResponse"] = []

class SchemaProfileToolComponentHistoryCreate(BaseModel):
    """Схема создания истории компонента (без component_id — берётся из URL)"""
    date: date
    status_id: int
    description: Optional[str] = None

class SchemaProfileToolComponentHistoryResponse(BaseModel):
    id: int
    profiletool_component_id: int
    date: date
    status: Optional[SchemaDirComponentStatus] = None
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)