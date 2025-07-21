"""
Модели для инструментов профилей
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ToolDimension(Base):
    """Справочник размерностей инструментов"""
    __tablename__ = "dir_tool_dimensions"
    
    id = Column(Integer, primary_key=True, index=True)
    dimension = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Связи
    tools = relationship("ProfileTool", back_populates="dimension")


class ComponentType(Base):
    """Справочник типов компонентов инструментов"""
    __tablename__ = "dir_component_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    
    # Связи
    components = relationship("ProfileToolComponent", back_populates="component_type")


class ComponentStatus(Base):
    """Справочник статусов компонентов"""
    __tablename__ = "dir_component_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    
    # Связи
    components = relationship("ProfileToolComponent", back_populates="status")


class ProfileTool(Base):
    """Инструмент для изготовления профиля"""
    __tablename__ = "profile_tools"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    dimension_id = Column(Integer, ForeignKey("dir_tool_dimensions.id"), nullable=False)
    description = Column(Text)
    
    # Связи
    profile = relationship("Profile", back_populates="tools")
    dimension = relationship("ToolDimension", back_populates="tools")
    components = relationship("ProfileToolComponent", back_populates="tool", cascade="all, delete-orphan")


class ProfileToolComponent(Base):
    """Компонент инструмента для профиля"""
    __tablename__ = "profile_tools_components"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("profile_tools.id"), nullable=False)
    component_type_id = Column(Integer, ForeignKey("dir_component_types.id"), nullable=False)
    variant = Column(Integer, nullable=True)  # Номер варианта (1, 2, 3... или NULL)
    description = Column(Text)
    status_id = Column(Integer, ForeignKey("dir_component_statuses.id"), nullable=False)
    
    # Связи
    tool = relationship("ProfileTool", back_populates="components")
    component_type = relationship("ComponentType", back_populates="components")
    status = relationship("ComponentStatus", back_populates="components")


class ProductComponent(Base):
    """Компонент изделия"""
    __tablename__ = "product_components"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    component_name = Column(String(200), nullable=False)
    description = Column(Text)
    quantity = Column(Integer, default=1)
    
    # Связи
    product = relationship("Product", back_populates="components")
