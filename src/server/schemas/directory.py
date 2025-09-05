"""Pydantic schemas for directory"""
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Базовая модель — общие поля для всех справочников
class DirectoryBase(BaseModel):
    name: str

# Схема для создания — без id!
class DirectoryCreate(DirectoryBase):
    description: Optional[str] = None

# Схема для обновления — все поля опциональны
class DirectoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Схема для ответа — включает id и поддержку ORM
class DirectoryResponse(DirectoryBase):
    id: int
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Конкретные справочники — наследуются и расширяются
class DirDepartment(DirectoryResponse):
    """Справочник: Подразделения"""
    pass

class DirTaskStatus(DirectoryResponse):
    """Справочник: Статусы задач"""
    pass

class DirComponentType(DirectoryResponse):
    """Справочник: Типы компонентов"""
    pass

class DirComponentStatus(DirectoryResponse):
    """Справочник: Статусы компонентов"""
    pass

class DirToolDimension(DirectoryResponse):
    """Справочник: размерности инструментов"""
    pass

class DirMachine(DirectoryResponse):
    """Справочник: станки"""
    pass

class DirTaskComponentStage(DirectoryResponse):  
    """Справочник: статусы компонентов задач"""
    pass
