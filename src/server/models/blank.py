"""Directory models for ADITIM Monitor"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from ..database import Base

class ModelBlank(Base):
    __tablename__ = "blank"

    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer, nullable=True, index=True, default=0)
    material_id = Column(Integer, ForeignKey("dir_blank_material.id"), nullable=True)
    profiletool_component_id = Column(Integer, ForeignKey("profiletool_component.id"))
    product_component_id = Column(Integer, ForeignKey("product_component.id"))
    date_order = Column(Date, nullable=True)
    date_arrival = Column(Date, nullable=True)
    date_product = Column(Date, nullable=True)
    blank_width = Column(Integer, nullable=True)
    blank_height = Column(Integer, nullable=True)
    blank_length = Column(Integer, nullable=True)
    product_width = Column(Integer, nullable=True)
    product_height = Column(Integer, nullable=True)
    product_length = Column(Integer, nullable=True)

    # Связи
    profiletool_component = relationship("ModelProfileToolComponent", back_populates="blank")
    product_component = relationship("ModelProductComponent", back_populates="blank")
    material = relationship("ModelDirBlankMaterial", back_populates="blank")


