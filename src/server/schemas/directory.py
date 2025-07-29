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
class DirDepartmentResponse(DirectoryResponse):
    pass


class DirTaskStatusResponse(DirectoryResponse):
    pass


class DirComponentTypeResponse(DirectoryResponse):
    description: Optional[str] = None


class DirComponentStatusResponse(DirectoryResponse):
    description: Optional[str] = None


class DirToolDimensionResponse(BaseModel):
    id: int
    dimension: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
