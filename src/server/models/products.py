"""
Product models for ADITIM Monitor
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from ..database import Base


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    department_id = Column(Integer, ForeignKey("dir_department.id"), nullable=False)
    
    # Связи
    department = relationship("DirDepartment", back_populates="product")
    component = relationship("ProductComponent", back_populates="product", cascade="all, delete-orphan")
    task = relationship("Task", back_populates="product")


class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    sketch = Column(LargeBinary, nullable=True)
    
    # Связи
    tool = relationship("ProfileTool", back_populates="profile", cascade="all, delete-orphan")
    task = relationship("Task", back_populates="profile")


class ProductComponent(Base):
    __tablename__ = "product_component"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    component_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=True)
    
    # Связи
    product = relationship("Product", back_populates="component")
    task_component = relationship("TaskComponent", back_populates="product_component")
