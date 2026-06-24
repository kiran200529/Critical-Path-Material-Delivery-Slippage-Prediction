from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.services.analytics_service import (
    get_dashboard_kpis,
    get_analytics_charts_data
)
from backend.api.dependencies.auth import get_current_user
from typing import Any

router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])

@router.get("/kpis")
def read_dashboard_kpis(
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Returns platform-wide KPI metrics for dashboard display.
    """
    return get_dashboard_kpis(db)

@router.get("/charts")
def read_charts_data(
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Returns structured data for the Supplier, Material, and Project charts.
    """
    return get_analytics_charts_data(db)
