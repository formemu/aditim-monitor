"""
Product models for ADITIM Monitor
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from ..database import Base


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    article = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    id_departament = Column(Integer, ForeignKey("dir_departament.id"), nullable=False)
    
    # Связи
    departament = relationship("DirDepartament", backref="products")
    components = relationship("ProductComponent", back_populates="product", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    sketch = Column(LargeBinary, nullable=True)
    
    # Связи
    tools = relationship("ProfileTool", back_populates="profile", cascade="all, delete-orphan")
