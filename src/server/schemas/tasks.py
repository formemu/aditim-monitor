"""
Pydantic schemas for tasks
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class TaskBase(BaseModel):
    id_product: Optional[int] = None
    id_profile: Optional[int] = None
    id_departament: int
    equipment: Optional[str] = None
    stage: Optional[str] = None
    deadline: Optional[datetime] = None
    position: int = 0
    id_type_work: int
    id_status: int = 1


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    id_product: Optional[int] = None
    id_profile: Optional[int] = None
    id_departament: Optional[int] = None
    equipment: Optional[str] = None
    stage: Optional[str] = None
    deadline: Optional[datetime] = None
    position: Optional[int] = None
    id_type_work: Optional[int] = None
    id_status: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Related objects
    product: Optional[dict] = None
    profile: Optional[dict] = None
    departament: Optional[dict] = None
    type_work: Optional[dict] = None
    status: Optional[dict] = None
    
    class Config:
        from_attributes = True
