from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database.db import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    probability = Column(Float, nullable=False)
    expected_delay_days = Column(Integer, nullable=False)
    prediction_timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to order
    order = relationship("Order", back_populates="prediction")
