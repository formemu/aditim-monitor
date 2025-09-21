"""Pydantic schemas for directory"""
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Базовая модель — общие поля для всех справочников
class SchemaDirectoryBase(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)
    
# Схема для создания — без id!
class SchemaDirectoryCreate(SchemaDirectoryBase):
    description: Optional[str] = None

# Схема для обновления — все поля опциональны
class SchemaDirectoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Схема для ответа — включает id и поддержку ORM
class SchemaDirectoryResponse(SchemaDirectoryBase):
    id: int
    description: Optional[str] = None


# Конкретные справочники — наследуются и расширяются
class SchemaDirDepartment(SchemaDirectoryResponse):
    """Справочник: Подразделения"""
    pass

class SchemaDirTaskStatus(SchemaDirectoryResponse):
    """Справочник: Статусы задач"""
    pass

class SchemaDirProfiletoolComponentType(SchemaDirectoryResponse):
    """Справочник: Типы компонентов инструментов профиля"""
    pass

class SchemaDirComponentStatus(SchemaDirectoryResponse):
    """Справочник: Статусы компонентов"""
    pass

class SchemaDirToolDimension(SchemaDirectoryResponse):
    """Справочник: размерности инструментов"""
    pass

class SchemaDirMachine(SchemaDirectoryResponse):
    """Справочник: станки"""
    work_type_id: int
    work_type: Optional['SchemaDirWorkType']


class WorkSubtype(SchemaDirectoryResponse):  
    """Справочник:  стадии задач компонентов"""
    work_type_id: Optional[int]
    work_type: Optional['SchemaDirWorkType']


class SchemaDirWorkType(SchemaDirectoryResponse):
    """Справочник: типы станков"""
    pass

class SchemaDirTaskType(SchemaDirectoryResponse):
    """Справочник: типы задач"""
    pass

class SchemaDirTaskLocation(SchemaDirectoryResponse):
    """Справочник:  местоположения задач"""
    pass