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
    equipment = Column(String, nullable=True)
    stage = Column(String, nullable=True)
    deadline = Column(Date, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    id_type_work = Column(Integer, ForeignKey("dir_type_work.id"), nullable=False)
    id_status = Column(Integer, ForeignKey("dir_queue_status.id"), nullable=False, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", backref="tasks")
    profile = relationship("Profile", backref="tasks")
    departament = relationship("DirDepartament", backref="tasks")
    type_work = relationship("DirTypeWork", backref="tasks")
    status = relationship("DirQueueStatus", backref="tasks")
