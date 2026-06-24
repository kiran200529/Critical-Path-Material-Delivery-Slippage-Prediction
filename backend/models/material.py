from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from backend.database.db import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    material_name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    unit_cost = Column(Float, nullable=False)

    # Relationship to orders
    orders = relationship("Order", back_populates="material", cascade="all, delete-orphan")
