from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import List, Dict, Any, Optional
import datetime
import re

DATE_FORMAT_MESSAGE = "Date must be a valid calendar date in YYYY-MM-DD format, for example 2026-06-15."
COMMITTED_DATE_REQUIRED_MESSAGE = "Committed delivery date is required. Please select a valid committed delivery date."
_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_PREDICTION_HORIZON_DAYS = 365
MAX_UNEXPLAINED_BUFFER_DAYS = 60


def _validate_iso_date_value(
    value: Any,
    *,
    required: bool = True,
    required_message: str = DATE_FORMAT_MESSAGE,
) -> Optional[str]:
    """Validate and normalize date strings used by the UI/API."""
    if value is None or value == "":
        if required:
            raise ValueError(required_message)
        return None

    if isinstance(value, datetime.datetime):
        value = value.date().isoformat()
    elif isinstance(value, datetime.date):
        value = value.isoformat()
    elif isinstance(value, str):
        value = value.strip()
    else:
        raise ValueError(DATE_FORMAT_MESSAGE)

    if not _DATE_PATTERN.fullmatch(value):
        raise ValueError(DATE_FORMAT_MESSAGE)

    try:
        datetime.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(DATE_FORMAT_MESSAGE) from exc

    return value

# --- AUTH SCHEMAS ---
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="Application User")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None
    reset_url: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    reset_token: str = Field(..., min_length=20)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class ResetPasswordResponse(BaseModel):
    message: str

# --- ML PREDICTION SCHEMAS ---
class PredictRequest(BaseModel):
    committed_delivery_date: str = Field(..., description="Date format YYYY-MM-DD")
    order_placed_date: Optional[str] = Field(None, description="Optional date format YYYY-MM-DD. If omitted, the app derives it from committed date and planned lead days.")
    planned_lead_calendar_days: int = Field(30, ge=1)
    distance_supplier_to_site_km: int = Field(50, ge=1)
    material_category: str
    supplier_tier: str
    delivery_terms: str
    site_access_restriction_level: str
    project_sector: str
    region_site: str
    order_value_band_gbp: str
    shipment_mode: str
    import_or_customs_hold_liable: str = "No"
    made_to_order_or_long_fabrication: str = "No"
    upstream_delay_flag_programme: str = "No"
    market_shortage_stress_band: str = "Low"
    po_line_changes_before_release_count: int = Field(0, ge=0)
    weather_or_temperature_sensitive_goods: str = "No"
    busy_season_construction_index: str = "Typical"
    jit_critical_path_item: str = "No"
    supplier_rolling_otif_band: str = "85% – 94%"
    haulier_capacity_stress_quarter: str = "No"
    packaging_handling_complexity: str = "Standard Pallet / Bulk"

    @field_validator("committed_delivery_date", mode="before")
    @classmethod
    def validate_committed_delivery_date(cls, value: Any) -> str:
        return _validate_iso_date_value(
            value,
            required=True,
            required_message=COMMITTED_DATE_REQUIRED_MESSAGE,
        )

    @field_validator("order_placed_date", mode="before")
    @classmethod
    def validate_order_placed_date(cls, value: Any) -> Optional[str]:
        return _validate_iso_date_value(value, required=False)

    @model_validator(mode="after")
    def validate_schedule_consistency(self):
        """Prevent misleading predictions when the committed date is far beyond the stated lead time."""
        today = datetime.date.today()
        committed_date = datetime.date.fromisoformat(self.committed_delivery_date)

        if committed_date < today:
            raise ValueError("Committed delivery date cannot be in the past.")

        days_until_committed = (committed_date - today).days
        if days_until_committed > MAX_PREDICTION_HORIZON_DAYS:
            raise ValueError(
                f"Committed delivery date is {days_until_committed} days from today. "
                f"This model is intended for operational predictions up to {MAX_PREDICTION_HORIZON_DAYS} days ahead."
            )

        if self.order_placed_date:
            order_date = datetime.date.fromisoformat(self.order_placed_date)
            if order_date > committed_date:
                raise ValueError("Order placed date cannot be after the committed delivery date.")
            actual_lead_days = (committed_date - order_date).days
            if actual_lead_days <= 0:
                raise ValueError("Committed delivery date must be after the order placed date.")
            if abs(actual_lead_days - self.planned_lead_calendar_days) > MAX_UNEXPLAINED_BUFFER_DAYS:
                raise ValueError(
                    f"The date gap between order placed date and committed delivery date is {actual_lead_days} days, "
                    f"but planned lead time is {self.planned_lead_calendar_days} days. Please keep these values consistent."
                )
        else:
            # The current dashboard does not collect order_placed_date. Without that date, a far-future
            # committed date can look like a large buffer from today, while the ML model only sees the
            # stated planned lead time. Reject inconsistent inputs instead of returning a misleading risk.
            unexplained_buffer_days = days_until_committed - self.planned_lead_calendar_days
            if unexplained_buffer_days > MAX_UNEXPLAINED_BUFFER_DAYS:
                raise ValueError(
                    f"Committed delivery date is {days_until_committed} days from today, but planned lead time is "
                    f"only {self.planned_lead_calendar_days} days. If this is a long-term order, set the planned "
                    f"lead time closer to {days_until_committed} days or provide an order placed date."
                )

        return self

class ShapFeatureInfo(BaseModel):
    feature: str
    display_name: str
    shap_value: float

class PredictResponse(BaseModel):
    delay_probability: float
    risk_score: int
    risk_level: str
    expected_delay_days: int
    shap_features: List[ShapFeatureInfo]
    ai_explanation: Optional[str] = None

# --- PLANNER SCHEMAS ---
class PlannerRequest(BaseModel):
    required_delivery_date: str
    predicted_delay_days: int
    safety_buffer_days: int
    planned_lead_days: int = 0

    @field_validator("required_delivery_date", mode="before")
    @classmethod
    def validate_required_delivery_date(cls, value: Any) -> str:
        return _validate_iso_date_value(value, required=True)

class PlannerResponse(BaseModel):
    required_delivery_date: str
    planned_lead_days: int
    predicted_delay_days: int
    safety_buffer_days: int
    total_lead_time_days: int
    recommended_order_date: str

class PlannerDefaultsRequest(BaseModel):
    supplier_id: int
    material_id: int
    required_delivery_date: str

    @field_validator("required_delivery_date", mode="before")
    @classmethod
    def validate_required_delivery_date(cls, value: Any) -> str:
        return _validate_iso_date_value(value, required=True)

# --- SUPPLIER SCHEMAS ---
class SupplierOut(BaseModel):
    id: int
    name: str
    supplier_type: str
    risk_score: int
    performance_rating: float
    
    class Config:
        from_attributes = True

class SupplierProfile(BaseModel):
    id: int
    name: str
    supplier_type: str
    risk_score: int
    reliability_score: int
    performance_rating: float
    total_orders: int
    delayed_orders: int
    delivery_success_rate: float
    average_delay_days: float
    risk_status: str

# --- RECOMMENDATION SCHEMAS ---
class AlternativeSupplierRecommendation(BaseModel):
    supplier_id: int
    supplier_name: str
    supplier_type: str
    risk_score: int
    reliability_score: int
    delay_probability: float
    expected_delay_days: int
    expected_delay_reduction_days: int
    expected_cost_impact_gbp: float
    performance_rating: float

class RecommendationRequest(BaseModel):
    supplier_id: int
    material_id: int
    quantity: int
    committed_delivery_date: str

    @field_validator("committed_delivery_date", mode="before")
    @classmethod
    def validate_committed_delivery_date(cls, value: Any) -> str:
        return _validate_iso_date_value(
            value,
            required=True,
            required_message=COMMITTED_DATE_REQUIRED_MESSAGE,
        )

# --- ALERTS ---
class AlertOut(BaseModel):
    id: int
    order_id: int
    alert_type: str
    message: str
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

# --- COPILOT SCHEMAS ---
class CopilotRequest(BaseModel):
    question: str

class CopilotResponse(BaseModel):
    answer: str
    sources: List[str]

# --- WHAT-IF SCHEMAS ---
class WhatIfRequest(BaseModel):
    material_category: str
    current_supplier_tier: str
    target_supplier_tier: str
    current_shipment_mode: str
    target_shipment_mode: str
    committed_delivery_date: str
    planned_lead_calendar_days: int = 30
    distance_supplier_to_site_km: int = 100

    @field_validator("committed_delivery_date", mode="before")
    @classmethod
    def validate_committed_delivery_date(cls, value: Any) -> str:
        return _validate_iso_date_value(
            value,
            required=True,
            required_message=COMMITTED_DATE_REQUIRED_MESSAGE,
        )

    @model_validator(mode="after")
    def validate_schedule_consistency(self):
        today = datetime.date.today()
        committed_date = datetime.date.fromisoformat(self.committed_delivery_date)
        if committed_date < today:
            raise ValueError("Committed delivery date cannot be in the past.")

        days_until_committed = (committed_date - today).days
        if days_until_committed > MAX_PREDICTION_HORIZON_DAYS:
            raise ValueError(
                f"Committed delivery date is {days_until_committed} days from today. "
                f"This model is intended for operational predictions up to {MAX_PREDICTION_HORIZON_DAYS} days ahead."
            )

        unexplained_buffer_days = days_until_committed - self.planned_lead_calendar_days
        if unexplained_buffer_days > MAX_UNEXPLAINED_BUFFER_DAYS:
            raise ValueError(
                f"Committed delivery date is {days_until_committed} days from today, but planned lead time is "
                f"only {self.planned_lead_calendar_days} days. Please keep the date and planned lead time consistent."
            )
        return self

class WhatIfResponse(BaseModel):
    current_risk_score: int
    target_risk_score: int
    risk_difference: int
    improvement_percentage: float
    expected_delay_days_saved: int
    expected_cost_saving_gbp: float
