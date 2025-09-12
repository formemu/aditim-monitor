"""Pydantic schemas for task"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .directory import SchemaDirTaskStatus, SchemaDirTaskComponentStage, SchemaDirMachine
from .profile_tool import SchemaProfileToolComponentResponse
from .product import SchemaProductComponentResponse

# === TASK SCHEMAS ===

class TaskBase(BaseModel):
    """Базовые поля задачи (без id и created)"""
    product_id: Optional[int] = None
    profile_tool_id: Optional[int] = None
    stage: Optional[str] = None
    deadline: Optional[date] = None
    created: Optional[date] = None
    position: Optional[int] = None
    status_id: int = 1
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SchemaTaskCreate(TaskBase):
    """Создание задачи — сервер сам установит created и id"""
    pass

class SchemaTaskUpdate(BaseModel):
    """Частичное обновление задачи — все поля опциональны"""
    product_id: Optional[int] = None
    profile_tool_id: Optional[int] = None
    stage: Optional[str] = None
    deadline: Optional[date] = None
    position: Optional[int] = None
    status_id: Optional[int] = None
    description: Optional[str] = None

class SchemaTaskResponse(TaskBase):
    """Ответ API — включает id и created"""
    id: int
    created: date
    status: Optional[SchemaDirTaskStatus] = None
    component: Optional[list["SchemaTaskComponentResponse"]] = None
    position: Optional[int] = None

# === TASK COMPONENT SCHEMAS ===

class TaskComponentBase(BaseModel):
    """Базовая модель компонента задачи"""
    profile_tool_component_id: Optional[int] = None
    product_component_id: Optional[int] = None
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SchemaTaskComponentCreate(TaskComponentBase):
    """Создание компонента"""
    pass

class TaskComponentUpdate(BaseModel):
    """Частичное обновление компонента"""
    profile_tool_component_id: Optional[int] = None
    product_component_id: Optional[int] = None
    description: Optional[str] = None

class SchemaTaskComponentResponse(TaskComponentBase):
    """Ответ с компонентом"""
    id: int
    profile_tool_component: Optional[SchemaProfileToolComponentResponse] = None
    product_component: Optional[SchemaProductComponentResponse] = None


class SchemaQueueReorderRequest(BaseModel):
    task_ids: List[int]


# === TASK COMPONENT STAGE SCHEMAS ===


class SchemaTaskComponentStageBase(BaseModel):
    """Базовая модель компонента задачи"""
    stage_num : Optional[int] = None
    task_component_id : Optional[int] = None
    stage_id : Optional[int] = None
    machine_id : Optional[int] = None
    description: Optional[str] = None

class SchemaTaskComponentStageCreate(SchemaTaskComponentStageBase):
    pass

class SchemaTaskComponentStageUpdate(SchemaTaskComponentStageBase):
    id: int
    task_component_id : Optional[int] = None
    stage : Optional[SchemaDirTaskComponentStage] = None
    machine : Optional[SchemaDirMachine] = None
    start : Optional[date] = None
    finish : Optional[date] = None

class SchemaTaskComponentStageResponse(SchemaTaskComponentStageBase):
    id: int
    task_component : Optional[SchemaTaskComponentResponse] = None
    stage : Optional[SchemaDirTaskComponentStage] = None
    machine : Optional[SchemaDirMachine] = None
    start : Optional[date] = None
    finish : Optional[date] = None