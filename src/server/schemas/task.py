"""Pydantic schemas for task"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .directory import DirTaskStatus

# === TASK SCHEMAS ===

class TaskBase(BaseModel):
    """Базовые поля задачи (без id и created_at)"""
    product_id: Optional[int] = None
    profile_tool_id: Optional[int] = None
    stage: Optional[str] = None
    deadline_on: Optional[date] = None
    created_at: Optional[date] = None
    position: int = 0
    status_id: int = 1
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SchemaTaskCreate(TaskBase):
    """Создание задачи — сервер сам установит created_at и id"""
    pass  # Все поля из Base

class TaskUpdate(BaseModel):
    """Частичное обновление задачи — все поля опциональны"""
    product_id: Optional[int] = None
    profile_tool_id: Optional[int] = None
    stage: Optional[str] = None
    deadline_on: Optional[date] = None
    position: Optional[int] = None
    status_id: Optional[int] = None
    description: Optional[str] = None

class SchemaTaskResponse(TaskBase):
    """Ответ API — включает id и created_at"""
    id: int
    created_at: date
    status: DirTaskStatus

# === TASK STATUS UPDATE (частное обновление статуса) ===

class SchemaTaskStatusUpdate(BaseModel):
    """Только для обновления статуса задачи"""
    status_id: int

# === TASK COMPONENT SCHEMAS ===

class TaskComponentBase(BaseModel):
    """Базовая модель компонента задачи"""
    profile_tool_component_id: Optional[int] = None
    product_component_id: Optional[int] = None
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SchemaTaskComponentCreate(TaskComponentBase):
    """Создание компонента — привязка к задаче обязательна"""
    

class TaskComponentUpdate(BaseModel):
    """Частичное обновление компонента"""
    profile_tool_component_id: Optional[int] = None
    product_component_id: Optional[int] = None
    description: Optional[str] = None

class SchemaTaskComponentResponse(TaskComponentBase):
    """Ответ с компонентом"""
    id: int
