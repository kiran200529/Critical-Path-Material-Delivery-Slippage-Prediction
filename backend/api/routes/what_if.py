from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.schemas.schemas import WhatIfRequest, WhatIfResponse
from backend.services.prediction_service import predict_delivery_risk
from backend.api.dependencies.auth import get_current_user
from typing import Any

router = APIRouter(prefix="/what-if", tags=["What-If Simulation"])

@router.post("/simulate", response_model=WhatIfResponse)
def simulate_scenario(
    request: WhatIfRequest,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Simulates changing supplier tier and shipment mode parameters
    to calculate improvement percentage, risk drop, and cost impact.
    """
    # 1. Base input features dictionary
    base_input = {
        "committed_delivery_date": request.committed_delivery_date,
        "planned_lead_calendar_days": request.planned_lead_calendar_days,
        "distance_supplier_to_site_km": request.distance_supplier_to_site_km,
        "material_category": request.material_category,
        "supplier_tier": request.current_supplier_tier,
        "delivery_terms": "DAP  Delivered at Site" if "Framework" in request.current_supplier_tier and "Non-Framework" not in request.current_supplier_tier else "FCA  Collect Ex-Works",
        "site_access_restriction_level": "Standard Laydown",
        "project_sector": "Commercial / Offices",
        "region_site": "London & South East",
        "order_value_band_gbp": "15k  75k",
        "shipment_mode": request.current_shipment_mode,
        "import_or_customs_hold_liable": "No",
        "made_to_order_or_long_fabrication": "Yes",
        "upstream_delay_flag_programme": "No",
        "market_shortage_stress_band": "Moderate",
        "po_line_changes_before_release_count": 0,
        "weather_or_temperature_sensitive_goods": "No",
        "busy_season_construction_index": "Typical",
        "jit_critical_path_item": "No",
        "supplier_rolling_otif_band": "85%  94%" if "Regional" in request.current_supplier_tier else "95%+" if "Framework" in request.current_supplier_tier and "Non-Framework" not in request.current_supplier_tier else "Under 85%",
        "haulier_capacity_stress_quarter": "No",
        "packaging_handling_complexity": "Standard Pallet / Bulk"
    }
    
    # 2. Predict CURRENT baseline
    current_pred = predict_delivery_risk(db, base_input)
    current_risk = current_pred["risk_score"]
    current_days = current_pred["expected_delay_days"]
    
    # 3. Predict TARGET scenario
    target_input = base_input.copy()
    target_input["supplier_tier"] = request.target_supplier_tier
    target_input["shipment_mode"] = request.target_shipment_mode
    target_input["delivery_terms"] = "DAP  Delivered at Site" if "Framework" in request.target_supplier_tier and "Non-Framework" not in request.target_supplier_tier else "FCA  Collect Ex-Works"
    target_input["supplier_rolling_otif_band"] = "85%  94%" if "Regional" in request.target_supplier_tier else "95%+" if "Framework" in request.target_supplier_tier and "Non-Framework" not in request.target_supplier_tier else "Under 85%"
    
    # Adjust lead time/distance logic slightly for target to simulate realistic operational shifts
    if "Framework" in request.target_supplier_tier and "Non-Framework" not in request.target_supplier_tier:
        target_input["planned_lead_calendar_days"] = max(25, request.planned_lead_calendar_days - 5)
        target_input["distance_supplier_to_site_km"] = max(30, request.distance_supplier_to_site_km - 20)
    elif "Spot" in request.target_supplier_tier:
        target_input["planned_lead_calendar_days"] = request.planned_lead_calendar_days + 10
        target_input["distance_supplier_to_site_km"] = request.distance_supplier_to_site_km + 50
        
    target_pred = predict_delivery_risk(db, target_input)
    target_risk = target_pred["risk_score"]
    target_days = target_pred["expected_delay_days"]
    
    # 4. Compute differences
    risk_diff = current_risk - target_risk
    improvement_pct = 0.0
    if current_risk > 0:
        improvement_pct = round((risk_diff / current_risk) * 100, 1)
        
    days_saved = max(0, current_days - target_days)
    
    # 5. Estimate cost differences (simulating a standard bulk procurement order)
    # Assume bulk quantity = 200 units, unit cost = £500
    qty = 200
    unit_cost = 500.0
    
    def estimate_multiplier(tier: str) -> float:
        if "Framework" in tier and "Non-Framework" not in tier:
            return 0.95  # 5% framework discount
        elif "Spot" in tier:
            return 1.10  # 10% spot premium
        return 1.0
        
    current_cost = qty * unit_cost * estimate_multiplier(request.current_supplier_tier)
    target_cost = qty * unit_cost * estimate_multiplier(request.target_supplier_tier)
    
    # Cost savings = current cost - target cost
    cost_saving = current_cost - target_cost
    
    return {
        "current_risk_score": current_risk,
        "target_risk_score": target_risk,
        "risk_difference": risk_diff,
        "improvement_percentage": improvement_pct,
        "expected_delay_days_saved": days_saved,
        "expected_cost_saving_gbp": round(cost_saving, 2)
    }
