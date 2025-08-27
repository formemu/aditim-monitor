from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from .profile_tool import SchemaProfileToolResponse

class SchemaProfileBase(BaseModel):
    """Базовая модель профиля"""
    article: str
    description: Optional[str] = None
    sketch: Optional[str] = None  # Base64 строка

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
    profile_tool: List[SchemaProfileToolResponse] = []
    model_config = ConfigDict(from_attributes=True)

SchemaProfileToolResponse.model_rebuild()