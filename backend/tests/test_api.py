import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.db import init_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Initializes and seeds the database before tests run."""
    init_db()

def test_read_kpis():
    response = client.get("/api/analytics/kpis")
    assert response.status_code == 200
    data = response.json()
    assert "total_orders" in data
    assert "delayed_orders" in data
    assert "average_risk_score" in data
    assert "expected_cost_impact" in data

def test_list_suppliers():
    response = client.get("/api/suppliers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]
    assert "reliability_score" in data[0]

def test_list_materials():
    response = client.get("/api/suppliers/materials")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "material_name" in data[0]
    assert "category" in data[0]

def test_predict_risk():
    payload = {
        "committed_delivery_date": "2026-06-15",
        "planned_lead_calendar_days": 30,
        "distance_supplier_to_site_km": 100,
        "material_category": "Structural Steel & Metalwork",
        "supplier_tier": "Approved  Regional",
        "delivery_terms": "FCA  Collect Ex-Works",
        "site_access_restriction_level": "Standard Laydown",
        "project_sector": "Commercial / Offices",
        "region_site": "North West",
        "order_value_band_gbp": "2k  15k",
        "shipment_mode": "Full Load  Direct",
        "import_or_customs_hold_liable": "No",
        "made_to_order_or_long_fabrication": "Yes",
        "upstream_delay_flag_programme": "Yes",
        "market_shortage_stress_band": "Moderate",
        "po_line_changes_before_release_count": 0,
        "weather_or_temperature_sensitive_goods": "No",
        "busy_season_construction_index": "Low",
        "jit_critical_path_item": "No",
        "supplier_rolling_otif_band": "85%  94%",
        "haulier_capacity_stress_quarter": "No",
        "packaging_handling_complexity": "Oversize  Permit / Escort"
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "delay_probability" in data
    assert "risk_level" in data
    assert "expected_delay_days" in data
    assert "shap_features" in data
    assert len(data["shap_features"]) > 0

def test_calculate_planner():
    payload = {
        "required_delivery_date": "2026-07-20",
        "predicted_delay_days": 5,
        "safety_buffer_days": 3,
        "planned_lead_days": 0
    }
    response = client.post("/api/planner/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_order_date"] == "2026-07-12"
    assert data["total_lead_time_days"] == 8

def test_what_if_simulation():
    payload = {
        "material_category": "Structural Steel & Metalwork",
        "current_supplier_tier": "Spot / Non-Framework",
        "target_supplier_tier": "Preferred  Framework",
        "current_shipment_mode": "Consolidated Hub",
        "target_shipment_mode": "Full Load  Direct",
        "committed_delivery_date": "2026-06-15"
    }
    response = client.post("/api/what-if/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "current_risk_score" in data
    assert "target_risk_score" in data
    assert "improvement_percentage" in data
    assert "expected_cost_saving_gbp" in data
    # Assert correct cost saving calculation: Spot (1.1 multiplier) vs Preferred Framework (0.95 multiplier)
    # qty = 200, unit_cost = 500
    # current = 200 * 500 * 1.10 = 110,000
    # target = 200 * 500 * 0.95 = 95,000
    # saving = 15,000
    assert data["expected_cost_saving_gbp"] == 15000.0

def test_copilot_chat():
    payload = {
        "question": "Show top risky deliveries."
    }
    response = client.post("/api/copilot/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
