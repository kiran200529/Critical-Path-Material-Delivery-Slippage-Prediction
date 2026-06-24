from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from backend.database.db import get_db
from backend.schemas.schemas import PredictRequest, PredictResponse
from backend.services.prediction_service import predict_delivery_risk
from backend.services.ai_service import generate_prediction_explanation
from backend.api.dependencies.auth import get_current_user, RoleChecker
from backend.models.user import User

router = APIRouter(prefix="/predict", tags=["Delivery Risk Prediction"])

# Allow Admin and Procurement Manager to run predictions
prediction_permission = Depends(RoleChecker(["Admin", "Procurement Manager", "Project Manager"]))

@router.post("", response_model=PredictResponse, status_code=status.HTTP_200_OK)
def run_prediction(
    request: PredictRequest,
    order_id: Optional[int] = Query(None, description="Optional Order ID to log the prediction against"),
    db: Session = Depends(get_db),
    user: User = prediction_permission
):
    """
    Predicts the risk of delivery slippage (> 3 working days) for a construction order.
    Calculates model feature contributions and generates AI root cause summaries.
    """
    input_dict = request.model_dump()
    
    # 1. Run the prediction service
    pred_res = predict_delivery_risk(db, input_dict, order_id=order_id)
    
    # 2. Generate the AI explanation
    ai_explanation = generate_prediction_explanation(
        probability=pred_res["delay_probability"],
        risk_level=pred_res["risk_level"],
        expected_delay_days=pred_res["expected_delay_days"],
        shap_features=pred_res["shap_features"],
        input_data=input_dict
    )
    
    return {
        "delay_probability": pred_res["delay_probability"],
        "risk_score": pred_res["risk_score"],
        "risk_level": pred_res["risk_level"],
        "expected_delay_days": pred_res["expected_delay_days"],
        "shap_features": pred_res["shap_features"],
        "ai_explanation": ai_explanation
    }
