"""
Task models for ADITIM Monitor
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True)
    id_product = Column(Integer, ForeignKey("products.id"), nullable=True)
    id_profile = Column(Integer, ForeignKey("profiles.id"), nullable=True)
    id_departament = Column(Integer, ForeignKey("dir_departament.id"), nullable=False)
    stage = Column(String, nullable=True)
    deadline = Column(Date, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    id_status = Column(Integer, ForeignKey("dir_queue_status.id"), nullable=False, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", backref="tasks")
    profile = relationship("Profile", backref="tasks")
    departament = relationship("DirDepartament", backref="tasks")
    status = relationship("DirQueueStatus", backref="tasks")
    components = relationship("TaskComponent", back_populates="task", cascade="all, delete-orphan")


class TaskComponent(Base):
    """Компонент задачи - связь между задачей и конкретными компонентами"""
    __tablename__ = "task_components"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    # Ссылка на компонент инструмента профиля (если задача для профиля)
    profile_tool_component_id = Column(Integer, ForeignKey("profile_tools_components.id"), nullable=True)
    # Ссылка на компонент изделия (если задача для изделия)
    product_component_id = Column(Integer, ForeignKey("product_components.id"), nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="components")
    profile_tool_component = relationship("ProfileToolComponent", backref="task_components")
    product_component = relationship("ProductComponent", backref="task_components")
