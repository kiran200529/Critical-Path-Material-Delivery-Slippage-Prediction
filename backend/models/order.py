from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.db import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=False)
    risk_score = Column(Integer, nullable=False, default=0)  # 0 to 100
    risk_level = Column(String(50), nullable=False, default="LOW")  # LOW, MEDIUM, HIGH
    prediction_probability = Column(Float, nullable=False, default=0.0)

    # Operational features for ML predictions and project grouping
    region_site = Column(String(255), nullable=True)
    project_sector = Column(String(255), nullable=True)
    shipment_mode = Column(String(255), nullable=True)
    planned_lead_calendar_days = Column(Integer, nullable=True, default=30)
    distance_supplier_to_site_km = Column(Integer, nullable=True, default=50)
    po_line_changes_before_release_count = Column(Integer, nullable=True, default=0)
    delivery_terms = Column(String(255), nullable=True)
    site_access_restriction_level = Column(String(255), nullable=True)
    import_or_customs_hold_liable = Column(String(50), nullable=True, default="No")
    made_to_order_or_long_fabrication = Column(String(50), nullable=True, default="No")
    upstream_delay_flag_programme = Column(String(50), nullable=True, default="No")
    market_shortage_stress_band = Column(String(50), nullable=True, default="Low")
    weather_or_temperature_sensitive_goods = Column(String(50), nullable=True, default="No")
    busy_season_construction_index = Column(String(50), nullable=True, default="Typical")
    jit_critical_path_item = Column(String(50), nullable=True, default="No")
    supplier_rolling_otif_band = Column(String(50), nullable=True, default="85%  94%")
    haulier_capacity_stress_quarter = Column(String(50), nullable=True, default="No")
    packaging_handling_complexity = Column(String(50), nullable=True, default="Standard Pallet / Bulk")

    # Relationships
    supplier = relationship("Supplier", back_populates="orders")
    material = relationship("Material", back_populates="orders")
    alerts = relationship("Alert", back_populates="order", cascade="all, delete-orphan")
    prediction = relationship("Prediction", back_populates="order", uselist=False, cascade="all, delete-orphan")
