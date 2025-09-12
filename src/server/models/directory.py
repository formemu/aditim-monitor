"""Directory models for ADITIM Monitor"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ModelDirDepartment(Base):
    """Справочник подразделений"""
    __tablename__ = "dir_department"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    product = relationship("ModelProduct", back_populates="department")

class ModelDirTaskStatus(Base):
    """Справочник статусов задач"""
    __tablename__ = "dir_task_status"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    task = relationship("ModelTask", back_populates="status")

class ModelDirToolDimension(Base):
    """Справочник размерностей инструментов"""
    __tablename__ = "dir_tool_dimension"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    profile_tool = relationship("ModelProfileTool", back_populates="dimension")

class ModelDirComponentType(Base):
    """Справочник типов компонентов инструментов"""
    __tablename__ = "dir_component_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    component = relationship("ModelProfileToolComponent", back_populates="type")
    plan_stage = relationship("ModelPlanTaskComponentStage", back_populates="component_type")

class ModelDirComponentStatus(Base):
    """Справочник статусов компонентов"""
    __tablename__ = "dir_component_status"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    # Relationships
    component = relationship("ModelProfileToolComponent", back_populates="status")

class ModelDirTaskComponentStage(Base):
    __tablename__= "dir_task_component_stage"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    type_id = Column(Integer, ForeignKey("dir_machine_type.id"), nullable=False)
    # Relationships
    component_stage = relationship("ModelTaskComponentStage", back_populates="stage")
    plan_stage = relationship("ModelPlanTaskComponentStage", back_populates="task_component_stage")
    type = relationship("ModelDirMachineType", back_populates="task_component_stage")

class ModelDirMachine(Base):
    __tablename__= "dir_machine"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    type_id = Column(Integer, ForeignKey("dir_machine_type.id"), nullable=False)
    description = Column(Text)
    # Relationships
    component_stage = relationship("ModelTaskComponentStage", back_populates="machine")
    type = relationship("ModelDirMachineType", back_populates="machine")


class ModelDirMachineType(Base):
    __tablename__= "dir_machine_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    # Relationships
    machine = relationship("ModelDirMachine", back_populates="type")
    task_component_stage = relationship("ModelDirTaskComponentStage", back_populates="type")