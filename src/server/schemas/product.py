"""Pydantic schemas for product"""
from typing import Optional
from pydantic import BaseModel, validator
import base64


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    department_id: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    department_id: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    class Config:
        from_attributes = True

class ProductComponentBase(BaseModel):
    component_name: str
    description: Optional[str] = None
    quantity: int = 1

class ProductComponentCreate(ProductComponentBase):
    pass

class ProductComponentResponse(ProductComponentBase):
    id: int
    product_id: int
    
    class Config:
        from_attributes = True
