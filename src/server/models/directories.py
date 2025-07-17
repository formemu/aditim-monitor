"""
Directory models for ADITIM Monitor
"""

from sqlalchemy import Column, Integer, String
from ..database import Base


class DirComponent(Base):
    __tablename__ = "dir_component"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True, unique=False)


class DirDepartament(Base):
    __tablename__ = "dir_departament"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=True)


class DirQueueStatus(Base):
    __tablename__ = "dir_queue_status"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)


class DirTypeWork(Base):
    __tablename__ = "dir_type_work"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
