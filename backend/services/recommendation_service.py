from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.models.supplier import Supplier
from backend.models.material import Material
from backend.services.prediction_service import predict_delivery_risk
import datetime

def recommend_alternative_suppliers(
    db: Session,
    current_supplier_id: int,
    material_id: int,
    quantity: int,
    committed_delivery_date: str
) -> List[Dict[str, Any]]:
    """
    Finds alternative suppliers for the material, predicts their risk profile,
    and returns recommendations including delay reductions, reliability scores, and cost deltas.
    """
    material = db.query(Material).filter(Material.id == material_id).first()
    current_supplier = db.query(Supplier).filter(Supplier.id == current_supplier_id).first()
    
    if not material or not current_supplier:
        return []
        
    # Get current supplier prediction baseline
    # We will simulate a standard predictor run for the current supplier
    current_input = {
        "committed_delivery_date": committed_delivery_date,
        "planned_lead_calendar_days": 35,
        "distance_supplier_to_site_km": 120,
        "material_category": material.category,
        "supplier_tier": current_supplier.supplier_type,
        "delivery_terms": "DAP  Delivered at Site" if "Framework" in current_supplier.supplier_type and "Non-Framework" not in current_supplier.supplier_type else "FCA  Collect Ex-Works",
        "site_access_restriction_level": "Standard Laydown",
        "project_sector": "Commercial / Offices",
        "region_site": "London & South East",
        "order_value_band_gbp": "15k  75k",
        "shipment_mode": "Consolidated Hub",
        "import_or_customs_hold_liable": "No",
        "made_to_order_or_long_fabrication": "Yes",
        "upstream_delay_flag_programme": "No",
        "market_shortage_stress_band": "Moderate",
        "po_line_changes_before_release_count": 0,
        "weather_or_temperature_sensitive_goods": "No",
        "busy_season_construction_index": "Typical",
        "jit_critical_path_item": "No",
        "supplier_rolling_otif_band": "Under 85%" if current_supplier.risk_score > 60 else "85%  94%",
        "haulier_capacity_stress_quarter": "No",
        "packaging_handling_complexity": "Standard Pallet / Bulk"
    }
    
    current_pred = predict_delivery_risk(db, current_input)
    current_prob = current_pred["delay_probability"]
    current_delay = current_pred["expected_delay_days"]
    
    # Calculate current baseline cost
    # To simulate cost differences, we assume:
    # Framework = unit_cost * 0.95 (5% discount)
    # Regional = unit_cost
    # Spot = unit_cost * 1.10 (10% premium)
    def estimate_multiplier(supplier_type: str) -> float:
        if "Framework" in supplier_type and "Non-Framework" not in supplier_type:
            return 0.95
        elif "Spot" in supplier_type:
            return 1.10
        return 1.0
        
    current_cost = quantity * material.unit_cost * estimate_multiplier(current_supplier.supplier_type)
    
    # Find alternative suppliers (excluding the current one)
    alternatives = db.query(Supplier).filter(Supplier.id != current_supplier_id).all()
    recommendations = []
    
    for alt in alternatives:
        # Standardize lead times and distances based on alternative supplier type
        alt_lead = 25 if "Framework" in alt.supplier_type and "Non-Framework" not in alt.supplier_type else 30 if "Regional" in alt.supplier_type else 45
        alt_dist = 40 if "Regional" in alt.supplier_type else 80 if "Framework" in alt.supplier_type and "Non-Framework" not in alt.supplier_type else 180
        
        alt_input = current_input.copy()
        alt_input["supplier_tier"] = alt.supplier_type
        alt_input["planned_lead_calendar_days"] = alt_lead
        alt_input["distance_supplier_to_site_km"] = alt_dist
        alt_input["supplier_rolling_otif_band"] = "95%+" if alt.performance_rating > 4.5 else "85%  94%" if alt.performance_rating > 3.5 else "Under 85%"
        
        alt_pred = predict_delivery_risk(db, alt_input)
        alt_prob = alt_pred["delay_probability"]
        alt_delay = alt_pred["expected_delay_days"]
        
        # Calculate alternative cost
        alt_cost = quantity * material.unit_cost * estimate_multiplier(alt.supplier_type)
        cost_delta = alt_cost - current_cost
        
        # We only suggest alternatives that have lower or equal risk
        if alt_prob < current_prob:
            delay_reduction = max(0, current_delay - alt_delay)
            
            # Reliability score formula
            reliability = int((alt.performance_rating / 5.0) * 60 + (100 - alt.risk_score) * 0.4)
            
            recommendations.append({
                "supplier_id": alt.id,
                "supplier_name": alt.name,
                "supplier_type": alt.supplier_type,
                "risk_score": alt.risk_score,
                "reliability_score": reliability,
                "delay_probability": alt_prob,
                "expected_delay_days": alt_delay,
                "expected_delay_reduction_days": delay_reduction,
                "expected_cost_impact_gbp": round(cost_delta, 2),
                "performance_rating": alt.performance_rating
            })
            
    # Sort recommendations by risk score ascending (lowest risk first)
    recommendations.sort(key=lambda x: x["risk_score"])
    return recommendations
