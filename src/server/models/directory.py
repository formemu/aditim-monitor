"""Directory models for ADITIM Monitor"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ModelDirectoryBase(Base):
    """Базовый класс для всех справочников"""
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

class ModelDirDepartment(ModelDirectoryBase):
    """Справочник подразделений"""
    __tablename__ = "dir_department"
    product = relationship("ModelProduct", back_populates="department")

class ModelDirTaskStatus(ModelDirectoryBase):
    """Справочник статусов задач"""
    __tablename__ = "dir_task_status"
    task = relationship("ModelTask", back_populates="status")

class ModelDirProfileToolDimension(ModelDirectoryBase):
    """Справочник размерностей инструментов"""
    __tablename__ = "dir_profiletool_dimension"
    profiletool = relationship("ModelProfileTool", back_populates="dimension")
    list_component_type = relationship("ModelDirProfileToolComponentType", back_populates="profiletool_dimension")

class ModelDirProfileToolComponentType(ModelDirectoryBase):
    """Справочник типов компонентов инструментов"""
    __tablename__ = "dir_profiletool_component_type"
    profiletool_dimension_id = Column(Integer, ForeignKey("dir_profiletool_dimension.id"), nullable=True)
    component = relationship("ModelProfileToolComponent", back_populates="type")
    plan_stage = relationship("ModelPlanTaskComponentStage", back_populates="profiletool_component_type")
    profiletool_dimension = relationship("ModelDirProfileToolDimension", back_populates="list_component_type")

class ModelDirProfileToolComponentStatus(ModelDirectoryBase):
    """Справочник статусов компонентов"""
    __tablename__ = "dir_profiletool_component_status"
    history = relationship("ModelProfileToolComponentHistory", back_populates="status")

class ModelDirMachine(ModelDirectoryBase):
    """Справочник станков"""
    __tablename__ = "dir_machine"
    work_type_id = Column(Integer, ForeignKey("dir_work_type.id"), nullable=False)
    component_stage = relationship("ModelTaskComponentStage", back_populates="machine")
    work_type = relationship("ModelDirWorkType", back_populates="machine")

class ModelDirWorkType(ModelDirectoryBase):
    """Справочник типов работ"""
    __tablename__ = "dir_work_type"
    machine = relationship("ModelDirMachine", back_populates="work_type")
    work_subtype = relationship("ModelDirWorkSubtype", back_populates="work_type")

class ModelDirTaskType(ModelDirectoryBase):
    """Справочник типов задач"""
    __tablename__ = "dir_task_type"
    task = relationship("ModelTask", back_populates="type")

class ModelDirWorkSubtype(ModelDirectoryBase):
    """Справочник подтипов работ"""
    __tablename__ = "dir_work_subtype"
    work_type_id = Column(Integer, ForeignKey("dir_work_type.id"), nullable=False)
    component_stage = relationship("ModelTaskComponentStage", back_populates="work_subtype")
    plan_stage = relationship("ModelPlanTaskComponentStage", back_populates="work_subtype")
    work_type = relationship("ModelDirWorkType", back_populates="work_subtype")

class ModelDirTaskLocation(ModelDirectoryBase):
    """Справочник локаций задач"""
    __tablename__ = "dir_task_location"
    task = relationship("ModelTask", back_populates="location")

class ModelDirBlankMaterial(ModelDirectoryBase):
    """Справочник материалов заготовок"""
    __tablename__ = "dir_blank_material"
    blank = relationship("ModelBlank", back_populates="material")
    list_type = relationship("ModelDirBlankType", back_populates="material")

class ModelDirBlankType(ModelDirectoryBase):
    """Справочник типов заготовок"""
    __tablename__ = "dir_blank_type"
    width = Column(Integer)
    length = Column(Integer)
    height = Column(Integer)
    material_id = Column(Integer, ForeignKey("dir_blank_material.id"))
    material = relationship("ModelDirBlankMaterial", back_populates="list_type")
