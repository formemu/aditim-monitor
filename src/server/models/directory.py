"""Directory models for ADITIM Monitor"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..database import Base

class DirDepartment(Base):
    """Справочник подразделений"""
    __tablename__ = "dir_department"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    product = relationship("Product", back_populates="department")

class DirTaskStatus(Base):
    """Справочник статусов задач"""
    __tablename__ = "dir_task_status"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    task = relationship("Task", back_populates="status")

class DirToolDimension(Base):
    """Справочник размерностей инструментов"""
    __tablename__ = "dir_tool_dimension"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    tool = relationship("ModelProfileTool", back_populates="dimension")

class DirComponentType(Base):
    """Справочник типов компонентов инструментов"""
    __tablename__ = "dir_component_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    component = relationship("ModelProfileToolComponent", back_populates="type")

class DirComponentStatus(Base):
    """Справочник статусов компонентов"""
    __tablename__ = "dir_component_status"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    component = relationship("ModelProfileToolComponent", back_populates="status")