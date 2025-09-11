"""Pydantic schemas for plan"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .directory import SchemaDirComponentType, SchemaDirTaskComponentStage


# === PLAN SCHEMAS ===

class SchemaPlanTaskComponentStageBase(BaseModel):
    num_stage: int
    component_type_id: int
    task_component_stage_id: int
    model_config = ConfigDict(from_attributes=True)

class SchemaPlanTaskComponentStageResponse(SchemaPlanTaskComponentStageBase):
    id: int
    component_type: Optional[SchemaDirComponentType] = None
    task_component_stage: Optional[SchemaDirTaskComponentStage] = None
