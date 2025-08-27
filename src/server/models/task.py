"""Task models for ADITIM Monitor"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class ModelTask(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    profile_tool_id = Column(Integer, ForeignKey("profile_tool.id"), nullable=True)
    stage = Column(String, nullable=True)
    deadline_on = Column(Date, nullable=True)
    position = Column(Integer, nullable=True)
    status_id = Column(Integer, ForeignKey("dir_task_status.id"), nullable=False, default=1)
    created_at = Column(Date, server_default=func.now())
    description = Column(Text, nullable=True)

    # Relationships
    product = relationship("ModelProduct", back_populates="task")
    profile_tool = relationship("ModelProfileTool", back_populates="task")
    status = relationship("ModelDirTaskStatus", back_populates="task")
    component = relationship("ModelTaskComponent", back_populates="task", cascade="all, delete-orphan")

class ModelTaskComponent(Base):
    """Компонент задачи - связь между задачей и конкретными компонентами"""
    __tablename__ = "task_component"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    # Ссылка на компонент инструмента профиля (если задача для профиля)
    profile_tool_component_id = Column(Integer, ForeignKey("profile_tool_component.id"), nullable=True)
    # Ссылка на компонент изделия (если задача для изделия)
    product_component_id = Column(Integer, ForeignKey("product_component.id"), nullable=True)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False, default=1)

    # Relationships
    task = relationship("ModelTask", back_populates="component")
    profile_tool_component = relationship("ModelProfileToolComponent", back_populates="task_component")
    product_component = relationship("ModelProductComponent", back_populates="task_component")
