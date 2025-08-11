"""Pydantic schemas for directory"""
from pydantic import BaseModel
from typing import Optional


class DirectoryBase(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

    
    


class DirDepartment(DirectoryBase):
    pass

class DirTaskStatus(DirectoryBase):
    pass

class DirComponentType(DirectoryBase):
    description: Optional[str] = None

class DirComponentStatus(DirectoryBase):
    description: Optional[str] = None

class DirToolDimension(DirectoryBase):
    dimension: str
    description: Optional[str] = None
    class Config:
        from_attributes = True
