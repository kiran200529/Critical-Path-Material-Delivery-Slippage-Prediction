from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from backend.models.supplier import Supplier
from backend.models.order import Order
from backend.models.prediction import Prediction

def get_supplier_risk_profile(db: Session, supplier_id: int) -> Dict[str, Any]:
    """
    Computes a detailed risk and performance profile for a specific supplier.
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        return {}
        
    orders = db.query(Order).filter(Order.supplier_id == supplier_id).all()
    total_orders = len(orders)
    
    # Calculate delay counts based on risk score threshold (prob >= 0.40)
    delayed_orders = sum(1 for o in orders if o.prediction_probability >= 0.40)
    success_rate = 100.0
    if total_orders > 0:
        success_rate = round(((total_orders - delayed_orders) / total_orders) * 100, 1)
        
    # Get average expected delay days from predictions
    order_ids = [o.id for o in orders]
    avg_delay_days = 0.0
    if order_ids:
        avg_days = db.query(func.avg(Prediction.expected_delay_days))\
                     .filter(Prediction.order_id.in_(order_ids)).scalar()
        if avg_days:
            avg_delay_days = round(float(avg_days), 1)
            
    # Formula for Supplier Score (0-100)
    # Higher rating, lower risk = higher score (more reliable)
    # Performance rating is 1-5, risk score is 0-100
    reliability_score = int((supplier.performance_rating / 5.0) * 60 + (100 - supplier.risk_score) * 0.4)
    reliability_score = max(0, min(100, reliability_score))
    
    return {
        "id": supplier.id,
        "name": supplier.name,
        "supplier_type": supplier.supplier_type,
        "risk_score": supplier.risk_score,
        "reliability_score": reliability_score,
        "performance_rating": supplier.performance_rating,
        "total_orders": total_orders,
        "delayed_orders": delayed_orders,
        "delivery_success_rate": success_rate,
        "average_delay_days": avg_delay_days,
        "risk_status": "HIGH" if supplier.risk_score > 60 else "MEDIUM" if supplier.risk_score > 30 else "LOW"
    }

def get_all_suppliers_intelligence(db: Session) -> List[Dict[str, Any]]:
    """
    Returns risk intelligence profiles for all suppliers, sorted by reliability score (descending).
    """
    suppliers = db.query(Supplier).all()
    profiles = [get_supplier_risk_profile(db, s.id) for s in suppliers]
    # Sort by reliability score descending
    profiles.sort(key=lambda x: x["reliability_score"], reverse=True)
    return profiles

def get_supplier_rankings(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """
    Splits suppliers into Top Performers and High-Risk Suppliers.
    """
    all_profiles = get_all_suppliers_intelligence(db)
    
    top_performers = [p for p in all_profiles if p["reliability_score"] >= 75]
    high_risk = [p for p in all_profiles if p["reliability_score"] < 50]
    
    # Sort high-risk by risk score descending
    high_risk.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return {
        "top_performers": top_performers[:5],
        "high_risk": high_risk[:5]
    }
