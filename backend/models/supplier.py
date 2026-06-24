from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database.db import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    supplier_type = Column(String(100), nullable=False)  # Preferred  Framework, Approved  Regional, Spot / Non-Framework
    risk_score = Column(Integer, nullable=False, default=50)  # 0 to 100
    performance_rating = Column(Float, nullable=False, default=3.0)  # 1.0 to 5.0
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to orders
    orders = relationship("Order", back_populates="supplier", cascade="all, delete-orphan")
