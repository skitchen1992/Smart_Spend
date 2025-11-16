from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.core.db import Base


class BaseModel(Base):
    """Базовая модель с общими полями"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

