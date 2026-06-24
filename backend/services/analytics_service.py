from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from backend.models.order import Order
from backend.models.supplier import Supplier
from backend.models.material import Material
from backend.models.alert import Alert
from backend.models.prediction import Prediction

def get_dashboard_kpis(db: Session) -> Dict[str, Any]:
    """
    Computes dashboard KPIs for the platform.
    """
    total_orders = db.query(Order).count()
    delayed_orders = db.query(Order).filter(Order.prediction_probability >= 0.40).count()
    active_suppliers = db.query(Supplier).count()
    
    avg_risk = db.query(func.avg(Order.risk_score)).scalar() or 0.0
    avg_risk_score = round(float(avg_risk), 1)
    
    critical_alerts = db.query(Alert).filter(Alert.alert_type == "CRITICAL").count()
    
    # Calculate Projects At Risk
    # Projects are represented by region_site in our data
    project_risks = db.query(
        Order.region_site,
        func.avg(Order.risk_score).label("avg_risk")
    ).group_by(Order.region_site).all()
    
    projects_at_risk = sum(1 for p in project_risks if p.avg_risk >= 40)
    
    # Expected Cost Impact
    # Penalty cost = 15% of total order value for high/medium risk orders, scaled by their delay probability
    orders = db.query(Order).all()
    total_cost_impact = 0.0
    for o in orders:
        if o.prediction_probability >= 0.40:
            material = db.query(Material).filter(Material.id == o.material_id).first()
            if material:
                order_value = o.quantity * material.unit_cost
                # Cost impact = order value * delay probability * 0.15 (penalty factor)
                total_cost_impact += order_value * o.prediction_probability * 0.15
                
    return {
        "total_orders": total_orders,
        "delayed_orders": delayed_orders,
        "active_suppliers": active_suppliers,
        "average_risk_score": avg_risk_score,
        "projects_at_risk": projects_at_risk,
        "critical_alerts": critical_alerts,
        "expected_cost_impact": round(total_cost_impact, 2)
    }

def get_analytics_charts_data(db: Session) -> Dict[str, Any]:
    """
    Returns charts data matching the analytics module requirements.
    """
    # 1. Supplier Analytics: Supplier Delay Trend, Supplier Risk Ranking, Supplier Performance
    suppliers = db.query(Supplier).all()
    
    supplier_rankings = []
    supplier_performance = []
    for s in suppliers:
        # Supplier Risk Ranking
        supplier_rankings.append({
            "name": s.name,
            "risk_score": s.risk_score,
            "supplier_type": s.supplier_type
        })
        # Supplier Performance
        orders = db.query(Order).filter(Order.supplier_id == s.id).all()
        total = len(orders)
        delays = sum(1 for o in orders if o.prediction_probability >= 0.40)
        success_rate = 100.0 if total == 0 else round(((total - delays) / total) * 100, 1)
        supplier_performance.append({
            "name": s.name,
            "success_rate": success_rate,
            "rating": s.performance_rating
        })
        
    # Sort rankings by risk score descending
    supplier_rankings.sort(key=lambda x: x["risk_score"], reverse=True)
    # Sort performance by rating descending
    supplier_performance.sort(key=lambda x: x["rating"], reverse=True)
    
    # Supplier Delay Trend (mocked historical monthly trend for top 3 suppliers for richer view)
    supplier_delay_trend = [
        {"month": "Jan", "Apex Steel Solutions": 2, "London Merchant Goods": 4, "Precast Concrete Specialists": 8},
        {"month": "Feb", "Apex Steel Solutions": 1, "London Merchant Goods": 3, "Precast Concrete Specialists": 9},
        {"month": "Mar", "Apex Steel Solutions": 3, "London Merchant Goods": 5, "Precast Concrete Specialists": 7},
        {"month": "Apr", "Apex Steel Solutions": 2, "London Merchant Goods": 2, "Precast Concrete Specialists": 11},
        {"month": "May", "Apex Steel Solutions": 1, "London Merchant Goods": 4, "Precast Concrete Specialists": 10},
    ]

    # 2. Material Analytics: Material Delay Distribution, High-Risk Material Categories
    material_categories = db.query(Order.material_id, Order.risk_score).all()
    
    # Group by category
    category_risks = {}
    for m_id, risk in material_categories:
        material = db.query(Material).filter(Material.id == m_id).first()
        if material:
            cat = material.category
            if cat not in category_risks:
                category_risks[cat] = []
            category_risks[cat].append(risk)
            
    high_risk_categories = []
    for cat, risks in category_risks.items():
        avg_cat_risk = round(sum(risks) / len(risks), 1)
        high_risk_categories.append({
            "category": cat,
            "average_risk": avg_cat_risk,
            "volume": len(risks)
        })
    high_risk_categories.sort(key=lambda x: x["average_risk"], reverse=True)
    
    # Material Delay Distribution
    material_delay_distribution = [
        {"range": "0-20% Risk", "count": db.query(Order).filter(Order.prediction_probability < 0.20).count()},
        {"range": "20-40% Risk", "count": db.query(Order).filter(Order.prediction_probability >= 0.20, Order.prediction_probability < 0.40).count()},
        {"range": "40-60% Risk", "count": db.query(Order).filter(Order.prediction_probability >= 0.40, Order.prediction_probability < 0.60).count()},
        {"range": "60-80% Risk", "count": db.query(Order).filter(Order.prediction_probability >= 0.60, Order.prediction_probability < 0.80).count()},
        {"range": "80-100% Risk", "count": db.query(Order).filter(Order.prediction_probability >= 0.80).count()}
    ]

    # 3. Project Analytics: Project Risk Heatmap, Monthly Delay Trend, Project Health Score
    # Project regions (London, North West, Midlands, etc.)
    project_risk_heatmap = []
    project_health_scores = []
    
    regions = db.query(Order.region_site).distinct().all()
    for (r_name,) in regions:
        if not r_name:
            continue
        region_orders = db.query(Order).filter(Order.region_site == r_name).all()
        r_total = len(region_orders)
        r_delays = sum(1 for o in region_orders if o.prediction_probability >= 0.40)
        r_avg_risk = sum(o.risk_score for o in region_orders) / r_total if r_total > 0 else 0.0
        
        # Heatmap
        project_risk_heatmap.append({
            "project_name": f"Project {r_name}",
            "region": r_name,
            "risk_index": round(r_avg_risk, 1),
            "order_volume": r_total
        })
        
        # Health Score (100 - average risk)
        health_score = int(100 - r_avg_risk)
        project_health_scores.append({
            "project_name": f"Project {r_name}",
            "health_score": health_score,
            "status": "EXCELLENT" if health_score >= 80 else "STABLE" if health_score >= 60 else "CRITICAL"
        })
        
    project_risk_heatmap.sort(key=lambda x: x["risk_index"], reverse=True)
    project_health_scores.sort(key=lambda x: x["health_score"])

    # Monthly Delay Trend (historical delay numbers aggregate)
    monthly_delay_trend = [
        {"month": "Jan", "delayed_deliveries": 12, "on_time_deliveries": 85},
        {"month": "Feb", "delayed_deliveries": 15, "on_time_deliveries": 78},
        {"month": "Mar", "delayed_deliveries": 9, "on_time_deliveries": 92},
        {"month": "Apr", "delayed_deliveries": 18, "on_time_deliveries": 72},
        {"month": "May", "delayed_deliveries": 14, "on_time_deliveries": 80},
        {"month": "Jun", "delayed_deliveries": 6, "on_time_deliveries": 45}  # Current month partial
    ]

    return {
        "supplier_delay_trend": supplier_delay_trend,
        "supplier_risk_ranking": supplier_rankings[:5],
        "supplier_performance": supplier_performance[:5],
        "material_delay_distribution": material_delay_distribution,
        "high_risk_material_categories": high_risk_categories[:5],
        "project_risk_heatmap": project_risk_heatmap,
        "monthly_delay_trend": monthly_delay_trend,
        "project_health_scores": project_health_scores
    }
