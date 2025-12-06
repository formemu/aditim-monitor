"""Pydantic schemas for task"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .directory import SchemaDirTaskStatus, WorkSubtype, SchemaDirMachine, SchemaDirTaskType, SchemaDirTaskLocation
from .profiletool import SchemaProfileToolComponentResponse, SchemaProfileToolResponse
from .product import SchemaProductComponentResponse, SchemaProductResponse

# === TASK SCHEMAS ===

class TaskBase(BaseModel):
    """Базовые поля задачи (без id и created)"""
    product_id: Optional[int] = None
    profiletool_id: Optional[int] = None
    deadline: Optional[date] = None
    created: Optional[date] = None
    position: Optional[int] = None
    status_id: int = 1
    type_id: Optional[int] = None
    location_id: Optional[int] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SchemaTaskCreate(TaskBase):
    """Создание задачи — сервер сам установит created и id"""
    pass

class SchemaTaskUpdate(BaseModel):
    """Частичное обновление задачи — все поля опциональны"""
    product_id: Optional[int] = None
    profiletool_id: Optional[int] = None
    deadline: Optional[date] = None
    position: Optional[int] = None
    completed: Optional[date] = None
    status_id: Optional[int] = None
    type_id: Optional[int] = None
    location_id: Optional[int] = None
    description: Optional[str] = None

class SchemaTaskResponse(TaskBase):
    """Ответ API — включает id и created"""
    id: int
    created: date
    completed: Optional[date] = None
    profiletool: Optional['SchemaProfileToolResponse'] = None
    product: Optional['SchemaProductResponse'] = None
    status: Optional['SchemaDirTaskStatus'] = None
    type: Optional['SchemaDirTaskType'] = None
    component: Optional[list['SchemaTaskComponentResponse']] = None
    position: Optional[int] = None
    location: Optional['SchemaDirTaskLocation'] = None

# === TASK COMPONENT SCHEMAS ===

class TaskComponentBase(BaseModel):
    """Базовая модель компонента задачи"""
    profiletool_component_id: Optional[int] = None
    product_component_id: Optional[int] = None
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SchemaTaskComponentCreate(TaskComponentBase):
    """Создание компонента"""
    pass

class TaskComponentUpdate(BaseModel):
    """Частичное обновление компонента"""
    profiletool_component_id: Optional[int] = None
    product_component_id: Optional[int] = None
    description: Optional[str] = None

class SchemaTaskComponentResponse(TaskComponentBase):
    """Ответ с компонентом"""
    id: int
    profiletool_component: Optional[SchemaProfileToolComponentResponse] = None
    product_component: Optional[SchemaProductComponentResponse] = None
    stage: Optional[list["SchemaTaskComponentStageResponse"]] = None


class SchemaQueueReorderRequest(BaseModel):
    task_ids: List[int]


# === TASK COMPONENT STAGE SCHEMAS ===

class SchemaTaskComponentStageBase(BaseModel):
    stage_num: Optional[int] = None
    task_component_id: Optional[int] = None
    work_subtype_id: Optional[int] = None
    machine_id: Optional[int] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SchemaTaskComponentStageCreate(SchemaTaskComponentStageBase):
    """Создание этапа компонента задачи"""
    pass

class SchemaTaskComponentStageUpdate(SchemaTaskComponentStageBase):
    """Частичное обновление этапа"""
    start: Optional[date] = None
    finish: Optional[date] = None

class SchemaTaskComponentStageResponse(SchemaTaskComponentStageBase):
    """Ответ с этапом компонента"""
    id: int
    machine: Optional[SchemaDirMachine] = None
    work_subtype: Optional[WorkSubtype] = None
    start: Optional[date] = None
    finish: Optional[date] = None
