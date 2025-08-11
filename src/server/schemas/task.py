"""Pydantic schemas for task"""

from datetime import datetime, date
from typing import Optional, List, Union
from pydantic import BaseModel


class TaskBase(BaseModel):
    product_id: Optional[int] = None
    profile_tool_id: Optional[int] = None
    stage: Optional[str] = None
    deadline_on: Optional[date] = None
    position: int = 0
    status_id: int = 1
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    product_id: Optional[int] = None
    profile_tool_id: Optional[int] = None
    stage: Optional[str] = None
    deadline_on: Optional[date] = None
    position: Optional[int] = None
    status_id: Optional[int] = None
    description: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TaskStatusUpdate(BaseModel):
    status_id: int

class TaskComponentCreate(BaseModel):
    task_id: int
    profile_tool_component_id: Optional[int] = None
    product_component_id: Optional[int] = None
