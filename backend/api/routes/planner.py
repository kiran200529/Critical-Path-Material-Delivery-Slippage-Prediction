from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Any
from backend.database.db import get_db
from backend.schemas.schemas import PlannerRequest, PlannerResponse, PlannerDefaultsRequest
from backend.services.planner_service import (
    calculate_optimal_order_date,
    get_planner_defaults
)
from backend.api.dependencies.auth import get_current_user
import datetime

router = APIRouter(prefix="/planner", tags=["Procurement Planner"])

@router.post("/calculate", response_model=PlannerResponse)
def calculate_schedule(
    request: PlannerRequest,
    user: Any = Depends(get_current_user)
):
    """
    Calculates the recommended order date:
    Required Date - Planned Lead Days - Predicted Delay - Safety Buffer
    """
    required_date = datetime.datetime.strptime(request.required_delivery_date, "%Y-%m-%d").date()
    
    res = calculate_optimal_order_date(
        required_delivery_date=required_date,
        predicted_delay_days=request.predicted_delay_days,
        safety_buffer_days=request.safety_buffer_days,
        planned_lead_days=request.planned_lead_days
    )
    return res

@router.get("/defaults")
def get_scheduling_defaults(
    supplier_id: int = Query(..., description="ID of the supplier"),
    material_id: int = Query(..., description="ID of the material"),
    required_delivery_date: str = Query(..., description="Target delivery date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Queries lead calendar days and runs ML prediction for the selected supplier/material
    to pre-populate planner inputs (lead time, delay probability, risk, expected delay days).
    """
    req_date = datetime.datetime.strptime(required_delivery_date, "%Y-%m-%d").date()
    defaults = get_planner_defaults(db, supplier_id, material_id, req_date)
    return defaults
