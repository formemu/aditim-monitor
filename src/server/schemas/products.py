"""
Pydantic schemas for products and profiles
"""

from typing import Optional, List
from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    id_departament: int
    sketch: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    id_departament: Optional[int] = None
    sketch: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    
    class Config:
        from_attributes = True


class ProfileBase(BaseModel):
    article: str
    sketch: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    article: Optional[str] = None
    sketch: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int
    
    class Config:
        from_attributes = True


class ProductComponentBase(BaseModel):
    name: str
    id_product: int


class ProductComponentCreate(ProductComponentBase):
    pass


class ProductComponentResponse(ProductComponentBase):
    id: int
    
    class Config:
        from_attributes = True


class ProfileComponentBase(BaseModel):
    name: str
    id_profile: int


class ProfileComponentCreate(ProfileComponentBase):
    pass


class ProfileComponentResponse(ProfileComponentBase):
    id: int
    
    class Config:
        from_attributes = True
