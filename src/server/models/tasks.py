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
    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    profile_tool_id = Column(Integer, ForeignKey("profile_tool.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("dir_department.id"), nullable=False)
    stage = Column(String, nullable=True)
    deadline_on = Column(Date, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    status_id = Column(Integer, ForeignKey("dir_task_status.id"), nullable=False, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="task")
    profile_tool = relationship("ProfileTool", back_populates="task")
    department = relationship("DirDepartment", back_populates="task")
    status = relationship("DirTaskStatus", back_populates="task")
    component = relationship("TaskComponent", back_populates="task", cascade="all, delete-orphan")


class TaskComponent(Base):
    """Компонент задачи - связь между задачей и конкретными компонентами"""
    __tablename__ = "task_component"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    # Ссылка на компонент инструмента профиля (если задача для профиля)
    profile_tool_component_id = Column(Integer, ForeignKey("profile_tool_component.id"), nullable=True)
    # Ссылка на компонент изделия (если задача для изделия)
    product_component_id = Column(Integer, ForeignKey("product_component.id"), nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="component")
    profile_tool_component = relationship("ProfileToolComponent", back_populates="task_component")
    product_component = relationship("ProductComponent", back_populates="task_component")
