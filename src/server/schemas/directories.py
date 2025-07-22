"""
Pydantic schemas for directories
"""

from pydantic import BaseModel


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


class ComponentResponse(DirectoryResponse):
    pass
