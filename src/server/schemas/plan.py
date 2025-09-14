"""Pydantic schemas for plan"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .directory import SchemaDirProfiletoolComponentType, SchemaDirTaskComponentStageName


# === PLAN SCHEMAS ===

class SchemaPlanTaskComponentStageBase(BaseModel):
    stage_num: int
    profiletool_component_type_id: int
    task_component_stage_name_id: int
    model_config = ConfigDict(from_attributes=True)

class SchemaPlanTaskComponentStageResponse(SchemaPlanTaskComponentStageBase):
    id: int
    profiletool_component_type: Optional[SchemaDirProfiletoolComponentType] = None
    task_component_stage_name: Optional[SchemaDirTaskComponentStageName] = None
