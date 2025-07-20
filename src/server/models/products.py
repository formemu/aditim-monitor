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
    id_departament = Column(Integer, ForeignKey("dir_departament.id"), nullable=False)
    sketch = Column(Text, nullable=True)
    
    # Relationships
    departament = relationship("DirDepartament", backref="products")


class ProductComponent(Base):
    __tablename__ = "product_component"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    id_product = Column(Integer, ForeignKey("product.id"), nullable=False)
    
    # Relationships
    product = relationship("Product", backref="components")


class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String, nullable=False, unique=True)
    sketch = Column(LargeBinary, nullable=True)  # Бинарные данные изображения


class ProfileComponent(Base):
    __tablename__ = "profile_component"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    id_profile = Column(Integer, ForeignKey("profile.id"), nullable=False)
    
    # Relationships
    profile = relationship("Profile", backref="components")
