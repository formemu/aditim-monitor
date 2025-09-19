"""Модели для инструментов профилей"""
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ModelProfileTool(Base):
    """Инструмент для изготовления профиля"""
    __tablename__ = "profile_tool"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profile.id", ondelete="CASCADE"), nullable=False)
    dimension_id = Column(Integer, ForeignKey("dir_profiletool_dimension.id"), nullable=False)
    description = Column(Text)
    
    # Связи
    profile = relationship("ModelProfile", back_populates="profile_tool")
    dimension = relationship("ModelDirProfileToolDimension", back_populates="profile_tool")
    component = relationship("ModelProfileToolComponent", back_populates="profile_tool", cascade="all, delete-orphan")
    task = relationship("ModelTask", back_populates="profile_tool", cascade="all, delete-orphan")



class ModelProfileToolComponent(Base):
    """Компонент инструмента для профиля"""
    __tablename__ = "profile_tool_component"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_tool_id = Column(Integer, ForeignKey("profile_tool.id", ondelete="CASCADE"), nullable=False)
    type_id = Column(Integer, ForeignKey("dir_profiletool_component_type.id"), nullable=False)
    variant = Column(Integer, nullable=True)
    description = Column(Text)
    status_id = Column(Integer, ForeignKey("dir_profiletool_component_status.id"), nullable=False)
    
    # Связи
    profile_tool = relationship("ModelProfileTool", back_populates="component")
    type = relationship("ModelDirProfileToolComponentType", back_populates="component")
    status = relationship("ModelDirProfileToolComponentStatus", back_populates="component")
    task_component = relationship("ModelTaskComponent", back_populates="profile_tool_component")
