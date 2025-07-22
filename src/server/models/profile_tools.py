"""
Модели для инструментов профилей
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ToolDimension(Base):
    """Справочник размерностей инструментов"""
    __tablename__ = "dir_tool_dimension"
    
    id = Column(Integer, primary_key=True, index=True)
    dimension = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Связи
    tool = relationship("ProfileTool", back_populates="dimension")


class ComponentType(Base):
    """Справочник типов компонентов инструментов"""
    __tablename__ = "dir_component_type"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    
    # Связи
    component = relationship("ProfileToolComponent", back_populates="component_type")


class ComponentStatus(Base):
    """Справочник статусов компонентов"""
    __tablename__ = "dir_component_status"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    
    # Связи
    component = relationship("ProfileToolComponent", back_populates="status")


class ProfileTool(Base):
    """Инструмент для изготовления профиля"""
    __tablename__ = "profile_tool"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profile.id"), nullable=False)
    dimension_id = Column(Integer, ForeignKey("dir_tool_dimension.id"), nullable=False)
    description = Column(Text)
    
    # Связи
    profile = relationship("Profile", back_populates="tool")
    dimension = relationship("ToolDimension", back_populates="tool")
    component = relationship("ProfileToolComponent", back_populates="tool", cascade="all, delete-orphan")


class ProfileToolComponent(Base):
    """Компонент инструмента для профиля"""
    __tablename__ = "profile_tool_component"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("profile_tool.id"), nullable=False)
    component_type_id = Column(Integer, ForeignKey("dir_component_type.id"), nullable=False)
    variant = Column(Integer, nullable=True)  # Номер варианта (1, 2, 3... или NULL)
    description = Column(Text)
    status_id = Column(Integer, ForeignKey("dir_component_status.id"), nullable=False)
    
    # Связи
    tool = relationship("ProfileTool", back_populates="component")
    component_type = relationship("ComponentType", back_populates="component")
    status = relationship("ComponentStatus", back_populates="component")
    task_component = relationship("TaskComponent", back_populates="profile_tool_component")
