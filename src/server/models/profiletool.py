"""Модели для инструментов профилей"""
from sqlalchemy import Column, Integer, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from ..database import Base

class ModelProfileTool(Base):
    """Инструмент для изготовления профиля"""
    __tablename__ = "profiletool"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profile.id", ondelete="CASCADE"), nullable=False)
    dimension_id = Column(Integer, ForeignKey("dir_profiletool_dimension.id"), nullable=False)
    description = Column(Text)
    
    # Связи
    profile = relationship("ModelProfile", back_populates="profiletool")
    dimension = relationship("ModelDirProfileToolDimension", back_populates="profiletool")
    component = relationship("ModelProfileToolComponent", back_populates="profiletool", cascade="all, delete-orphan")
    task = relationship("ModelTask", back_populates="profiletool", cascade="all, delete-orphan")



class ModelProfileToolComponent(Base):
    """Компонент инструмента для профиля"""
    __tablename__ = "profiletool_component"
    
    id = Column(Integer, primary_key=True, index=True)
    profiletool_id = Column(Integer, ForeignKey("profiletool.id", ondelete="CASCADE"), nullable=False)
    type_id = Column(Integer, ForeignKey("dir_profiletool_component_type.id"), nullable=False)
    variant = Column(Integer, nullable=True)
    description = Column(Text)
    
    # Связи
    profiletool = relationship("ModelProfileTool", back_populates="component")
    type = relationship("ModelDirProfileToolComponentType", back_populates="component")
    task_component = relationship("ModelTaskComponent", back_populates="profiletool_component")
    history = relationship("ModelProfileToolComponentHistory", back_populates="component", cascade="all, delete-orphan")
    blank = relationship("ModelBlank", back_populates="profiletool_component")

class ModelProfileToolComponentHistory(Base):
    """История изменений компонента инструмента для профиля"""
    __tablename__ = "profiletool_component_history"

    id = Column(Integer, primary_key=True, index=True)
    profiletool_component_id = Column(Integer, ForeignKey("profiletool_component.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=True)
    status_id = Column(Integer, ForeignKey("dir_profiletool_component_status.id"), nullable=True, default=1)
    description = Column(Text, nullable=True)

    # Связи
    component = relationship("ModelProfileToolComponent", back_populates="history")
    status = relationship("ModelDirProfileToolComponentStatus", back_populates="history")