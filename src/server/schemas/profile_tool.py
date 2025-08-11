"""Pydantic schemas for profile_tool"""

from typing import Optional
from pydantic import BaseModel


class ProfileToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    dimension: Optional[str] = None

class ProfileToolCreate(ProfileToolBase):
    pass

class ProfileToolUpdate(ProfileToolBase):
    name: Optional[str] = None
    dimension: Optional[str] = None
    description: Optional[str] = None

class ProfileToolResponse(ProfileToolBase):
    id: int
    
    class Config:
        from_attributes = True

class ProfileToolComponentBase(BaseModel):
    component_name: str
    description: Optional[str] = None
    variant: Optional[str] = None

class ProfileToolComponentCreate(ProfileToolComponentBase):
    pass

class ProfileToolComponentResponse(ProfileToolComponentBase):
    id: int
    profile_tool_id: int
    
    class Config:
        from_attributes = True
