"""Product models for ADITIM Monitor"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class ModelProduct(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    department_id = Column(Integer, ForeignKey("dir_department.id"), nullable=False)
    
    # Связи
    department = relationship("ModelDirDepartment", back_populates="product")
    component = relationship("ModelProductComponent", back_populates="product", cascade="all, delete-orphan")
    task = relationship("ModelTask", back_populates="product")


class ModelProductComponent(Base):
    __tablename__ = "product_component"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=True)
    
    # Связи
    product = relationship("ModelProduct", back_populates="component")
    task_component = relationship("ModelTaskComponent", back_populates="product_component")
