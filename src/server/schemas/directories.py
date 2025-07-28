"""
Pydantic schemas for directories
"""

from pydantic import BaseModel
from typing import Optional


class DirectoryBase(BaseModel):
    name: str


class DirectoryCreate(DirectoryBase):
    pass


class DirectoryResponse(DirectoryBase):
    id: int
    
    class Config:
        from_attributes = True


# Specific directory schemas
class DepartmentResponse(DirectoryResponse):
    pass


class TaskStatusResponse(DirectoryResponse):
    pass


class ComponentTypeResponse(DirectoryResponse):
    description: Optional[str] = None


class ComponentStatusResponse(DirectoryResponse):
    description: Optional[str] = None


class ToolDimensionResponse(BaseModel):
    id: int
    dimension: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
