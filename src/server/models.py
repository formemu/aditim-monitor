from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

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

class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    id_departament = Column(Integer, ForeignKey("dir_departament.id"), nullable=False)
    sketch = Column(Text, nullable=True)
    departament = relationship("DirDepartament", backref="products")
    components = relationship("ProductComponent", back_populates="product")

class ProductComponent(Base):
    __tablename__ = "product_component"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    id_product = Column(Integer, ForeignKey("product.id"), nullable=False)
    product = relationship("Product", back_populates="components")

class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String, unique=True, nullable=False)
    sketch = Column(Text, nullable=True)

class ProfileComponent(Base):
    __tablename__ = "profile_component"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    comment = Column(Text, nullable=True)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    id_product = Column(Integer, ForeignKey("product.id"), nullable=True)
    id_profile = Column(Integer, ForeignKey("profile.id"), nullable=True)
    id_departament = Column(Integer, ForeignKey("dir_departament.id"), nullable=False)
    equipment = Column(String, nullable=False)
    deadline = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    id_type_work = Column(Integer, ForeignKey("dir_type_work.id"), nullable=False)
    id_status = Column(Integer, ForeignKey("dir_queue_status.id"), nullable=True)
    product = relationship("Product")
    profile = relationship("Profile")
    departament = relationship("DirDepartament")
    type_work = relationship("DirTypeWork")
    status = relationship("DirQueueStatus")

