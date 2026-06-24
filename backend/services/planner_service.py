import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.models.supplier import Supplier
from backend.models.material import Material
from backend.services.prediction_service import predict_delivery_risk

def calculate_optimal_order_date(
    required_delivery_date: datetime.date,
    predicted_delay_days: int,
    safety_buffer_days: int,
    planned_lead_days: int = 0
) -> Dict[str, Any]:
    """
    Computes the recommended order date based on:
    Required Date - Planned Lead Days - Predicted Delay Days - Safety Buffer
    """
    total_days_back = planned_lead_days + predicted_delay_days + safety_buffer_days
    recommended_date = required_delivery_date - datetime.timedelta(days=total_days_back)
    
    return {
        "required_delivery_date": required_delivery_date.isoformat(),
        "planned_lead_days": planned_lead_days,
        "predicted_delay_days": predicted_delay_days,
        "safety_buffer_days": safety_buffer_days,
        "total_lead_time_days": total_days_back,
        "recommended_order_date": recommended_date.isoformat()
    }

def get_planner_defaults(
    db: Session,
    supplier_id: int,
    material_id: int,
    required_delivery_date: datetime.date
) -> Dict[str, Any]:
    """
    Queries the database and uses the ML model to get default parameters for the planner.
    Pre-populates Lead Days and runs a risk prediction to get predicted delay days.
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    material = db.query(Material).filter(Material.id == material_id).first()
    
    if not supplier or not material:
        return {
            "planned_lead_days": 30,
            "predicted_delay_days": 3,
            "safety_buffer_days": 3
        }
        
    # Standard lead days based on supplier type and material
    # Spot suppliers take longer, preferred are faster
    planned_lead = 30
    if "Framework" in supplier.supplier_type and "Non-Framework" not in supplier.supplier_type:
        planned_lead = 25
    elif "Spot" in supplier.supplier_type:
        planned_lead = 45
        
    # Estimate distance based on supplier type
    distance = 50
    if "Regional" in supplier.supplier_type:
        distance = 35
    elif "Spot" in supplier.supplier_type:
        distance = 180
        
    # Setup default features to feed the ML predictor
    default_input = {
        "committed_delivery_date": required_delivery_date.isoformat(),
        "planned_lead_calendar_days": planned_lead,
        "distance_supplier_to_site_km": distance,
        "material_category": material.category,
        "supplier_tier": supplier.supplier_type,
        "delivery_terms": "DAP  Delivered at Site" if "Framework" in supplier.supplier_type and "Non-Framework" not in supplier.supplier_type else "FCA  Collect Ex-Works",
        "site_access_restriction_level": "Standard Laydown",
        "project_sector": "Commercial / Offices",
        "region_site": "London & South East",
        "order_value_band_gbp": "15k  75k",
        "shipment_mode": "Full Load  Direct" if planned_lead < 30 else "Consolidated Hub",
        "import_or_customs_hold_liable": "No",
        "made_to_order_or_long_fabrication": "Yes" if "Steel" in material.material_name or "Precast" in material.material_name else "No",
        "upstream_delay_flag_programme": "No",
        "market_shortage_stress_band": "Low" if supplier.risk_score < 30 else "Moderate",
        "po_line_changes_before_release_count": 0,
        "weather_or_temperature_sensitive_goods": "Yes" if "Concrete" in material.material_name else "No",
        "busy_season_construction_index": "Typical",
        "jit_critical_path_item": "Yes" if "Steel" in material.material_name else "No",
        "supplier_rolling_otif_band": "95%+" if supplier.performance_rating > 4.5 else "85%  94%",
        "haulier_capacity_stress_quarter": "No",
        "packaging_handling_complexity": "Oversize  Permit / Escort" if "Steel" in material.material_name or "Precast" in material.material_name else "Standard Pallet / Bulk"
    }
    
    # Run prediction
    pred = predict_delivery_risk(db, default_input)
    predicted_delay = pred["expected_delay_days"]
    
    # Define safety buffer based on supplier risk
    safety_buffer = 2
    if supplier.risk_score > 60:
        safety_buffer = 5
    elif supplier.risk_score > 30:
        safety_buffer = 3
        
    return {
        "planned_lead_days": planned_lead,
        "predicted_delay_days": predicted_delay,
        "safety_buffer_days": safety_buffer,
        "predicted_probability": pred["delay_probability"],
        "risk_level": pred["risk_level"]
    }
