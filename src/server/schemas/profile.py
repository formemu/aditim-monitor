from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .profiletool import SchemaProfileToolResponse

class SchemaProfileBase(BaseModel):
    """Базовая модель профиля"""
    article: str
    description: Optional[str] = None
    sketch: Optional[str] = None  # Base64 строка
    model_config = ConfigDict(from_attributes=True)

class SchemaProfileCreate(SchemaProfileBase):
    """Создание профиля — все поля из Base"""
    pass

class SchemaProfileUpdate(BaseModel):
    """Частичное обновление профиля — все поля опциональны"""
    article: Optional[str] = None
    description: Optional[str] = None
    sketch: Optional[str] = None

class SchemaProfileResponse(SchemaProfileBase):
    """Ответ API — включает id и поддержку ORM"""
    id: int
    profiletool: List[SchemaProfileToolResponse] = []


SchemaProfileToolResponse.model_rebuild()