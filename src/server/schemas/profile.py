from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProfileBase(BaseModel):
    """Базовая модель профиля"""
    article: str
    description: Optional[str] = None
    sketch: Optional[str] = None  # Base64 строка

class ProfileCreate(ProfileBase):
    """Создание профиля — все поля из Base"""
    pass

class ProfileUpdate(BaseModel):
    """Частичное обновление профиля — все поля опциональны"""
    article: Optional[str] = None
    description: Optional[str] = None
    sketch: Optional[str] = None

class ProfileResponse(ProfileBase):
    """Ответ API — включает id и поддержку ORM"""
    id: int
    model_config = ConfigDict(from_attributes=True)