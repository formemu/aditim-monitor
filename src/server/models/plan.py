"""Plan models for ADITIM Monitor"""
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ModelPlanTaskComponentStage(Base):
    __tablename__= "plan_task_component_stage"
    id = Column(Integer, primary_key=True, index=True)
    profiletool_component_type_id = Column(Integer, ForeignKey("dir_profiletool_component_type.id"), nullable=False)
    task_component_stage_name_id = Column(Integer, ForeignKey("dir_task_component_stage_name.id"), nullable=False)
    stage_num = Column(Integer, nullable=False)
    # Relationships
    profiletool_component_type = relationship("ModelDirProfileToolComponentType", back_populates="plan_stage")
    task_component_stage_name = relationship("ModelDirTaskComponentStageName", back_populates="plan_stage")