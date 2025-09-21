"""Pydantic schemas for plan"""
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .directory import SchemaDirProfiletoolComponentType, WorkSubtype


# === PLAN SCHEMAS ===

class SchemaPlanTaskComponentStageBase(BaseModel):
    stage_num: int
    profiletool_component_type_id: int
    work_subtype_id: int
    model_config = ConfigDict(from_attributes=True)

class SchemaPlanTaskComponentStageResponse(SchemaPlanTaskComponentStageBase):
    id: int
    profiletool_component_type: Optional[SchemaDirProfiletoolComponentType] = None
    work_subtype: Optional[WorkSubtype] = None
