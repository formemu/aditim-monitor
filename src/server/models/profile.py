"""Profile models for ADITIM Monitor"""

from sqlalchemy import Column, Integer, String, LargeBinary, Text
from sqlalchemy.orm import relationship
from ..database import Base

class ModelProfile(Base):
    """Профиль - абстрактная сущность, описание каким должен быть профиль"""
    __tablename__ = "profile"
    
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    sketch = Column(Text)  # ← хранить как строку (Base64)
    # Связи
    profile_tool = relationship("ModelProfileTool", back_populates="profile", cascade="all, delete")
