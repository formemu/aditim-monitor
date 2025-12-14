"""Схемы справочников"""
from pydantic import BaseModel, ConfigDict
from typing import Optional


class SchemaDirectoryBase(BaseModel):
    """Базовая схема справочника"""
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SchemaDirectoryCreate(SchemaDirectoryBase):
    """Схема создания справочника"""
    pass


class SchemaDirectoryUpdate(BaseModel):
    """Схема обновления справочника"""
    name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SchemaDirectoryResponse(SchemaDirectoryBase):
    """Схема ответа справочника"""
    id: int


# Конкретные справочники
class SchemaDirDepartment(SchemaDirectoryResponse):
    """Справочник: Подразделения"""
    pass


class SchemaDirTaskStatus(SchemaDirectoryResponse):
    """Справочник: Статусы задач"""
    pass


class SchemaDirToolDimension(SchemaDirectoryResponse):
    """Справочник: размерности инструментов"""
    pass


class SchemaDirToolDimensionCreate(SchemaDirectoryBase):
    """Схема создания размерности инструмента"""
    pass


class SchemaDirToolDimensionUpdate(SchemaDirectoryUpdate):
    """Схема обновления размерности инструмента"""
    pass


class SchemaDirProfiletoolComponentType(SchemaDirectoryResponse):
    """Справочник: Типы компонентов инструментов профиля"""
    profiletool_dimension_id: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    length: Optional[int] = None
    profiletool_dimension: Optional[SchemaDirToolDimension] = None


class SchemaDirProfiletoolComponentTypeCreate(BaseModel):
    """Схема создания типа компонента"""
    name: str
    description: Optional[str] = None
    profiletool_dimension_id: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    length: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SchemaDirProfiletoolComponentTypeUpdate(BaseModel):
    """Схема обновления типа компонента"""
    name: Optional[str] = None
    description: Optional[str] = None
    profiletool_dimension_id: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    length: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SchemaDirComponentStatus(SchemaDirectoryResponse):
    """Справочник: Статусы компонентов"""
    pass


class SchemaDirMachine(SchemaDirectoryResponse):
    """Справочник: Станки"""
    work_type_id: int


class SchemaDirWorkType(SchemaDirectoryResponse):
    """Справочник: Типы работ"""
    pass


class SchemaDirTaskType(SchemaDirectoryResponse):
    """Справочник: Типы задач"""
    pass


class SchemaDirWorkSubtype(SchemaDirectoryResponse):
    """Справочник: Подтипы работ"""
    work_type_id: int
    work_type: Optional[SchemaDirWorkType] = None


class SchemaDirBlankMaterial(SchemaDirectoryResponse):
    """Справочник: Материалы заготовок"""
    pass


class SchemaDirBlankTypeBase(BaseModel):
    """Базовая схема типа заготовки"""
    width: Optional[int] = None
    length: Optional[int] = None
    height: Optional[int] = None
    material_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class SchemaDirBlankTypeCreate(SchemaDirBlankTypeBase):
    """Схема создания типа заготовки"""
    pass


class SchemaDirBlankTypeUpdate(SchemaDirBlankTypeBase):
    """Схема обновления типа заготовки"""
    pass


class SchemaDirBlankTypeResponse(SchemaDirBlankTypeBase):
    """Схема ответа типа заготовки"""
    id: int
    material: Optional[SchemaDirBlankMaterial] = None


# Алиасы для обратной совместимости
WorkSubtype = SchemaDirWorkSubtype