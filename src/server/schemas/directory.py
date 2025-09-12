"""Pydantic schemas for directory"""
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Базовая модель — общие поля для всех справочников
class SchemaDirectoryBase(BaseModel):
    name: str

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
    model_config = ConfigDict(from_attributes=True)

# Конкретные справочники — наследуются и расширяются
class SchemaDirDepartment(SchemaDirectoryResponse):
    """Справочник: Подразделения"""
    pass

class SchemaDirTaskStatus(SchemaDirectoryResponse):
    """Справочник: Статусы задач"""
    pass

class SchemaDirComponentType(SchemaDirectoryResponse):
    """Справочник: Типы компонентов"""
    pass

class SchemaDirComponentStatus(SchemaDirectoryResponse):
    """Справочник: Статусы компонентов"""
    pass

class SchemaDirToolDimension(SchemaDirectoryResponse):
    """Справочник: размерности инструментов"""
    pass

class SchemaDirMachine(SchemaDirectoryResponse):
    """Справочник: станки"""
    type_id: int
    type: Optional['SchemaDirMachineType']


class SchemaDirTaskComponentStage(SchemaDirectoryResponse):  
    """Справочник:  стадии задач компонентов"""
    type_id: Optional[int]
    type: Optional['SchemaDirMachineType']


class SchemaDirMachineType(SchemaDirectoryResponse):
    """Справочник: типы станков"""
    pass

