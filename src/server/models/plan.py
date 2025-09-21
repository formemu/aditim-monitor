"""Plan models for ADITIM Monitor"""
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class ModelPlanTaskComponentStage(Base):
    __tablename__= "plan_task_component_stage"
    id = Column(Integer, primary_key=True, index=True)
    profiletool_component_type_id = Column(Integer, ForeignKey("dir_profiletool_component_type.id"), nullable=False)
    work_subtype_id = Column(Integer, ForeignKey("dir_work_subtype.id"), nullable=False)
    stage_num = Column(Integer, nullable=False)
    # Relationships
    profiletool_component_type = relationship("ModelDirProfileToolComponentType", back_populates="plan_stage")
    work_subtype = relationship("ModelDirWorkSubtype", back_populates="plan_stage")