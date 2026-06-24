from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.database.db import get_db
from backend.schemas.schemas import SupplierProfile, SupplierOut
from backend.services.supplier_service import (
    get_all_suppliers_intelligence,
    get_supplier_risk_profile,
    get_supplier_rankings
)
from backend.api.dependencies.auth import get_current_user

from backend.models.material import Material

router = APIRouter(prefix="/suppliers", tags=["Supplier Intelligence"])

@router.get("/materials")
def list_materials(
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Returns list of all materials in the system catalog.
    """
    return db.query(Material).all()

@router.get("", response_model=List[SupplierProfile])
def list_suppliers_intelligence(
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Returns list of all suppliers evaluated by the reliability engine.
    Sorted by reliability score.
    """
    return get_all_suppliers_intelligence(db)

@router.get("/rankings", response_model=Dict[str, List[SupplierProfile]])
def get_ranked_suppliers(
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Retrieves the Top 5 performing and Top 5 high-risk suppliers.
    """
    return get_supplier_rankings(db)

@router.get("/{supplier_id}", response_model=SupplierProfile)
def get_supplier_profile(
    supplier_id: int,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user)
):
    """
    Retrieves the detailed risk and OTIF profile for a specific supplier.
    """
    profile = get_supplier_risk_profile(db, supplier_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with ID {supplier_id} not found."
        )
    return profile
