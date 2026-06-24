from sqlalchemy.orm import Session
from typing import Dict, Any, List
import datetime
from backend.ml import predictor
from backend.models.order import Order
from backend.models.prediction import Prediction
from backend.models.alert import Alert
from backend.models.supplier import Supplier
from backend.models.material import Material
from backend.config import CLASSIFICATION_THRESHOLD

def predict_delivery_risk(db: Session, order_data: Dict[str, Any], order_id: int = None) -> Dict[str, Any]:
    """
    Performs delivery slippage prediction using the ML predictor,
    saves the prediction, creates necessary alerts, and updates database records.
    """
    # 1. Run the predictor wrapper
    pred_res = predictor.predict(order_data)
    
    prob = pred_res["delay_probability"]
    risk_level = pred_res["risk_level"]
    expected_delay_days = pred_res["expected_delay_days"]
    shap_features = pred_res["shap_features"]
    
    # Risk score is probability converted to 0-100 scale
    risk_score = int(prob * 100)
    
    # 2. If an order_id is provided, persist prediction and handle alerts in database
    if order_id:
        # Retrieve the order
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            # Update order details
            order.risk_score = risk_score
            order.risk_level = risk_level
            order.prediction_probability = prob
            
            # Save to predictions table
            prediction_record = Prediction(
                order_id=order_id,
                probability=prob,
                expected_delay_days=expected_delay_days
            )
            db.add(prediction_record)
            
            # Delete existing alerts for this order to prevent duplicates
            db.query(Alert).filter(Alert.order_id == order_id).delete()
            
            # Generate new alerts based on thresholds
            alert_type = None
            alert_msg = ""
            
            # Get supplier and material names for the message
            supplier_name = db.query(Supplier.name).filter(Supplier.id == order.supplier_id).scalar() or "Supplier"
            material_name = db.query(Material.material_name).filter(Material.id == order.material_id).scalar() or "Material"
            
            if prob >= 0.70:
                alert_type = "CRITICAL"
                alert_msg = f"Critical Risk Alert: Delivery of '{material_name}' from '{supplier_name}' is predicted to be delayed by more than 3 working days (Probability: {risk_score}%, Expected delay: {expected_delay_days} days)."
            elif prob >= CLASSIFICATION_THRESHOLD:
                alert_type = "WARNING"
                alert_msg = f"Warning Alert: Delivery of '{material_name}' from '{supplier_name}' has an elevated risk of delay (Probability: {risk_score}%, Expected delay: {expected_delay_days} days)."
                
            if alert_type:
                new_alert = Alert(
                    order_id=order_id,
                    alert_type=alert_type,
                    message=alert_msg
                )
                db.add(new_alert)
                
            db.commit()
            db.refresh(order)
            
    return {
        "order_id": order_id,
        "delay_probability": prob,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "expected_delay_days": expected_delay_days,
        "shap_features": shap_features
    }

def get_predictions_history(db: Session, limit: int = 50) -> List[Prediction]:
    """
    Returns historical predictions.
    """
    return db.query(Prediction).order_by(Prediction.prediction_timestamp.desc()).limit(limit).all()
