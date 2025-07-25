"""
Pydantic schemas for products and profiles
"""

from typing import Optional, List, Union
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


class ProfileBase(BaseModel):
    article: str
    description: Optional[str] = None  # Описание профиля
    sketch: Optional[Union[str, bytes]] = None  # Base64 encoded image data or binary


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    article: Optional[str] = None
    description: Optional[str] = None  # Описание профиля
    sketch: Optional[Union[str, bytes]] = None  # Base64 encoded image data or binary


class ProfileResponse(ProfileBase):
    id: int
    
    @validator('sketch', pre=True)
    def convert_binary_to_base64(cls, v):
        """Конвертирует бинарные данные в base64 строку для ответа"""
        if v is None:
            return None
        if isinstance(v, bytes):
            # Конвертируем бинарные данные в base64
            base64_data = base64.b64encode(v).decode('utf-8')
            return f"data:image/png;base64,{base64_data}"
        return v
    
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
