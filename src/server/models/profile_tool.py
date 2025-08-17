"""
Модели для инструментов профилей
"""

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class ProfileTool(Base):
    """Инструмент для изготовления профиля"""
    __tablename__ = "profile_tool"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profile.id", ondelete="CASCADE"), nullable=False)
    dimension_id = Column(Integer, ForeignKey("dir_tool_dimension.id"), nullable=False)
    description = Column(Text)
    
    # Связи
    profile = relationship("Profile", back_populates="tool")
    dimension = relationship("DirToolDimension", back_populates="tool")
    component = relationship("ProfileToolComponent", back_populates="tool", cascade="all, delete-orphan")
    task = relationship("Task", back_populates="profile_tool")


class ProfileToolComponent(Base):
    """Компонент инструмента для профиля"""
    __tablename__ = "profile_tool_component"
    
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("profile_tool.id", ondelete="CASCADE"), nullable=False)
    component_type_id = Column(Integer, ForeignKey("dir_component_type.id"), nullable=False)
    variant = Column(Integer, nullable=True)  # Номер варианта (1, 2, 3... или NULL)
    description = Column(Text)
    status_id = Column(Integer, ForeignKey("dir_component_status.id"), nullable=False)
    
    # Связи
    tool = relationship("ProfileTool", back_populates="component")
    component_type = relationship("DirComponentType", back_populates="component")
    status = relationship("DirComponentStatus", back_populates="component")
    task_component = relationship("TaskComponent", back_populates="profile_tool_component")
