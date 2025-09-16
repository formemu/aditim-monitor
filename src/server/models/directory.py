"""Directory models for ADITIM Monitor"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ModelDirDepartment(Base): # +
    """Справочник подразделений"""
    __tablename__ = "dir_department"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    product = relationship("ModelProduct", back_populates="department")

class ModelDirTaskStatus(Base): # +
    """Справочник статусов задач"""
    __tablename__ = "dir_task_status"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    task = relationship("ModelTask", back_populates="status")

class ModelDirProfileToolDimension(Base): # +
    """Справочник размерностей инструментов"""
    __tablename__ = "dir_profiletool_dimension"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    profile_tool = relationship("ModelProfileTool", back_populates="dimension")

class ModelDirProfileToolComponentType(Base): # +
    """Справочник типов компонентов инструментов"""
    __tablename__ = "dir_profiletool_component_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    component = relationship("ModelProfileToolComponent", back_populates="type")
    plan_stage = relationship("ModelPlanTaskComponentStage", back_populates="profiletool_component_type")

class ModelDirProfileToolComponentStatus(Base): # +
    """Справочник статусов компонентов"""
    __tablename__ = "dir_profiletool_component_status"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    component = relationship("ModelProfileToolComponent", back_populates="status")

class ModelDirTaskComponentStageName(Base): # +
    __tablename__= "dir_task_component_stage_name"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    work_type_id = Column(Integer, ForeignKey("dir_work_type.id"), nullable=False)
    # Relationships
    component_stage = relationship("ModelTaskComponentStage", back_populates="stage_name")
    plan_stage = relationship("ModelPlanTaskComponentStage", back_populates="task_component_stage_name")
    work_type = relationship("ModelDirWorkType", back_populates="task_component_stage_name")

class ModelDirMachine(Base): # +
    __tablename__= "dir_machine"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    work_type_id = Column(Integer, ForeignKey("dir_work_type.id"), nullable=False)
    description = Column(Text)
    # Relationships
    component_stage = relationship("ModelTaskComponentStage", back_populates="machine")
    work_type = relationship("ModelDirWorkType", back_populates="machine")


class ModelDirWorkType(Base): # +
    __tablename__= "dir_work_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    # Relationships
    machine = relationship("ModelDirMachine", back_populates="work_type")
    task_component_stage_name = relationship("ModelDirTaskComponentStageName", back_populates="work_type")

class ModelDirTaskType(Base): # +
    __tablename__= "dir_task_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    # Relationships
    task = relationship("ModelTask", back_populates="type")

class ModelDirTaskLocation(Base): # +
    __tablename__= "dir_task_location"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    # Relationships
    task = relationship("ModelTask", back_populates="location")