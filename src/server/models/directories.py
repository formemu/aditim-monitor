"""
Directory models for ADITIM Monitor
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..database import Base


class DirDepartment(Base):
    """Справочник подразделений"""
    __tablename__ = "dir_department"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Связи
    product = relationship("Product", back_populates="department")
    task = relationship("Task", back_populates="department")


class DirTaskStatus(Base):
    """Справочник статусов задач"""
    __tablename__ = "dir_task_status"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    
    # Связи  
    task = relationship("Task", back_populates="status")
