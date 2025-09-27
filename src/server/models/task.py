"""Task models for ADITIM Monitor"""

from sqlalchemy import Column, Integer, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class ModelTask(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    position = Column(Integer, nullable=True)
    deadline = Column(Date, nullable=True)
    created = Column(Date, nullable=True)
    completed = Column(Date, nullable=True)

    product_id = Column(Integer, ForeignKey("product.id"), nullable=True)
    profiletool_id = Column(Integer, ForeignKey("profiletool.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("dir_task_status.id"), nullable=True, default=1)
    type_id = Column(Integer, ForeignKey("dir_task_type.id"), nullable=True, default=1)
    location_id = Column(Integer, ForeignKey("dir_task_location.id"), nullable=True, default=1)

    description = Column(Text, nullable=True)

    # Relationships
    product = relationship("ModelProduct", back_populates="task")
    profiletool = relationship("ModelProfileTool", back_populates="task")
    status = relationship("ModelDirTaskStatus", back_populates="task")
    location = relationship("ModelDirTaskLocation", back_populates="task")
    type = relationship("ModelDirTaskType", back_populates="task")
    component = relationship("ModelTaskComponent", back_populates="task", cascade="all, delete-orphan")

class ModelTaskComponent(Base):
    """Компонент задачи - связь между задачей и конкретными компонентами"""
    __tablename__ = "task_component"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    profiletool_component_id = Column(Integer, ForeignKey("profiletool_component.id"), nullable=True)
    product_component_id = Column(Integer, ForeignKey("product_component.id"), nullable=True)

    description = Column(Text, nullable=True)

    # Relationships
    task = relationship("ModelTask", back_populates="component")
    profiletool_component = relationship("ModelProfileToolComponent", back_populates="task_component")
    product_component = relationship("ModelProductComponent", back_populates="task_component")
    stage = relationship("ModelTaskComponentStage", back_populates="task_component", cascade="all, delete-orphan")

class ModelTaskComponentStage(Base):
    __tablename__ = "task_component_stage"

    id = Column(Integer, primary_key=True, index=True)
    stage_num = Column(Integer, nullable=True)

    start = Column(Date, nullable=True)
    finish = Column(Date, nullable=True)

    task_component_id = Column(Integer, ForeignKey("task_component.id"), nullable=True)
    work_subtype_id = Column(Integer, ForeignKey("dir_work_subtype.id"), nullable=True)
    machine_id = Column(Integer, ForeignKey("dir_machine.id"), nullable=True)

    description = Column(Text, nullable=True)

    # Relationships
    task_component = relationship("ModelTaskComponent", back_populates="stage")
    work_subtype = relationship("ModelDirWorkSubtype", back_populates="component_stage")
    machine = relationship("ModelDirMachine", back_populates="component_stage")

