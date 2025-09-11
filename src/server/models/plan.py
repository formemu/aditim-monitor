"""Plan models for ADITIM Monitor"""
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ModelPlanTaskComponentStage(Base):
    __tablename__= "plan_task_component_stage"
    id = Column(Integer, primary_key=True, index=True)
    component_type_id = Column(Integer, ForeignKey("dir_component_type.id"), nullable=False)
    task_component_stage_id = Column(Integer, ForeignKey("dir_task_component_stage.id"), nullable=False)
    num_stage = Column(Integer, nullable=False)
    # Relationships
    component_type = relationship("ModelDirComponentType", back_populates="plan_stage")
    task_component_stage = relationship("ModelDirTaskComponentStage", back_populates="plan_stage")