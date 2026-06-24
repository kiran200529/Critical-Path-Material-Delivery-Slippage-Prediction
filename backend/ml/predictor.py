import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd

from backend.config import CLASSIFICATION_THRESHOLD, FEATURE_COLUMNS_PATH, METADATA_PATH, MODEL_PATH

# Runtime model assets
pipeline = None
model = None
preprocessor = None
feature_columns: List[str] = []
metadata: Dict[str, Any] = {}
classification_threshold: float = CLASSIFICATION_THRESHOLD


DEFAULT_INPUTS: Dict[str, Any] = {
    "material_category": "Structural Steel & Metalwork",
    "supplier_tier": "Approved – Regional",
    "planned_lead_calendar_days": 30,
    "distance_supplier_to_site_km": 50,
    "delivery_terms": "DAP – Delivered at Site",
    "site_access_restriction_level": "Standard Laydown",
    "project_sector": "Commercial / Offices",
    "region_site": "London & South East",
    "order_value_band_gbp": "£2k – £15k",
    "shipment_mode": "Full Load – Direct",
    "import_or_customs_hold_liable": "No",
    "made_to_order_or_long_fabrication": "No",
    "upstream_delay_flag_programme": "No",
    "market_shortage_stress_band": "Low",
    "po_line_changes_before_release_count": 0,
    "weather_or_temperature_sensitive_goods": "No",
    "busy_season_construction_index": "Typical",
    "jit_critical_path_item": "No",
    "supplier_rolling_otif_band": "85% – 94%",
    "haulier_capacity_stress_quarter": "No",
    "packaging_handling_complexity": "Standard Pallet / Bulk",
}

TEXT_NORMALIZATION_MAP = {
    # Supplier tiers
    "Preferred  Framework": "Preferred – Framework",
    "Preferred - Framework": "Preferred – Framework",
    "Preferred – Framework": "Preferred – Framework",
    "Approved  Regional": "Approved – Regional",
    "Approved - Regional": "Approved – Regional",
    "Approved – Regional": "Approved – Regional",
    "Spot / Non-Framework": "Spot / Non-Framework",
    # Delivery terms
    "DAP  Delivered at Site": "DAP – Delivered at Site",
    "DAP - Delivered at Site": "DAP – Delivered at Site",
    "DAP – Delivered at Site": "DAP – Delivered at Site",
    "FCA  Collect Ex-Works": "FCA – Collect Ex-Works",
    "FCA - Collect Ex-Works": "FCA – Collect Ex-Works",
    "FCA – Collect Ex-Works": "FCA – Collect Ex-Works",
    "CPT  Carriage Paid To Yard": "CPT – Carriage Paid To Yard",
    "CPT - Carriage Paid To Yard": "CPT – Carriage Paid To Yard",
    "CPT – Carriage Paid To Yard": "CPT – Carriage Paid To Yard",
    "DDP  Inclusive to Site (Import)": "DDP – Inclusive to Site (Import)",
    "DDP - Inclusive to Site (Import)": "DDP – Inclusive to Site (Import)",
    "DDP – Inclusive to Site (Import)": "DDP – Inclusive to Site (Import)",
    # Order value bands
    "2k  15k": "£2k – £15k",
    "£2k  £15k": "£2k – £15k",
    "£2k - £15k": "£2k – £15k",
    "£2k – £15k": "£2k – £15k",
    "15k  75k": "£15k – £75k",
    "£15k  £75k": "£15k – £75k",
    "£15k - £75k": "£15k – £75k",
    "£15k – £75k": "£15k – £75k",
    "75k  250k": "£75k – £250k",
    "£75k  £250k": "£75k – £250k",
    "£75k - £250k": "£75k – £250k",
    "£75k – £250k": "£75k – £250k",
    # Shipment modes
    "Full Load  Direct": "Full Load – Direct",
    "Full Load - Direct": "Full Load – Direct",
    "Full Load – Direct": "Full Load – Direct",
    # Site access
    "Restricted  City Centre / Congestion": "Restricted – City Centre / Congestion",
    "Restricted - City Centre / Congestion": "Restricted – City Centre / Congestion",
    "Restricted – City Centre / Congestion": "Restricted – City Centre / Congestion",
    # Material categories
    "MEP  Cable & Containment": "MEP – Cable & Containment",
    "MEP - Cable & Containment": "MEP – Cable & Containment",
    "MEP – Cable & Containment": "MEP – Cable & Containment",
    "MEP  Plant & Equipment": "MEP – Plant & Equipment",
    "MEP - Plant & Equipment": "MEP – Plant & Equipment",
    "MEP – Plant & Equipment": "MEP – Plant & Equipment",
    # OTIF bands
    "85%  94%": "85% – 94%",
    "85% - 94%": "85% – 94%",
    "85% – 94%": "85% – 94%",
}


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_model_assets() -> None:
    """Load the final notebook-exported sklearn Pipeline and metadata once."""
    global pipeline, model, preprocessor, feature_columns, metadata, classification_threshold

    if pipeline is not None:
        return

    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}. "
            "Expected backend/ml/final_model_pipeline.joblib."
        )

    try:
        pipeline = joblib.load(model_path)
    except Exception as exc:
        raise RuntimeError(
            "Unable to load the ML model pipeline. This model was saved from Google Colab. "
            "Install the project requirements, especially scikit-learn==1.6.1, then run again. "
            f"Original error: {exc}"
        ) from exc

    if not hasattr(pipeline, "predict_proba"):
        raise TypeError("Loaded model must be a fitted sklearn Pipeline with predict_proba support.")

    metadata = _load_json(Path(METADATA_PATH), {})
    feature_columns = _load_json(Path(FEATURE_COLUMNS_PATH), [])

    if not feature_columns:
        feature_columns = list(getattr(pipeline, "feature_names_in_", []))

    if not feature_columns:
        raise ValueError("Feature columns are missing. Check backend/ml/feature_columns.json.")

    classification_threshold = float(metadata.get("threshold", CLASSIFICATION_THRESHOLD))

    model = pipeline.named_steps.get("model") if hasattr(pipeline, "named_steps") else None
    preprocessor = pipeline.named_steps.get("preprocessor") if hasattr(pipeline, "named_steps") else None

    print(f"Loaded ML model pipeline: {model_path}")
    print(f"Loaded feature count: {len(feature_columns)}")
    print(f"Classification threshold: {classification_threshold}")


def normalize_category_value(value: Any) -> Any:
    """Normalize old UI/database values to match the new notebook training categories."""
    if not isinstance(value, str):
        return value

    cleaned = value.strip()
    if cleaned in TEXT_NORMALIZATION_MAP:
        return TEXT_NORMALIZATION_MAP[cleaned]

    # Convert common typed hyphen variants to the en dash style used in the dataset.
    normalized = cleaned.replace(" – ", " – ").replace(" - ", " – ")
    normalized = normalized.replace("  ", " – ") if "%" in normalized else normalized

    return TEXT_NORMALIZATION_MAP.get(normalized, normalized)


def _to_number(value: Any, default: float) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_date(value: Any, default: pd.Timestamp, field_name: str, required: bool = False) -> pd.Timestamp:
    """Parse date values safely. Required dates must be valid YYYY-MM-DD values."""
    if value is None or value == "":
        if required:
            raise ValueError(f"{field_name} is required and must be in YYYY-MM-DD format.")
        return default

    if isinstance(value, str):
        value = value.strip()
        if len(value) != 10 or value[4] != "-" or value[7] != "-":
            raise ValueError(f"{field_name} must be a valid date in YYYY-MM-DD format.")

    parsed = pd.to_datetime(value, errors="coerce", dayfirst=False)
    if pd.isna(parsed):
        raise ValueError(f"{field_name} must be a valid date in YYYY-MM-DD format.")

    return pd.Timestamp(parsed)


def prepare_model_input(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert API/UI input into the exact 26 feature columns used by the new model.

    The new notebook uses order date derived features. The current application UI does not
    collect order_placed_date, so when it is missing we estimate it as:
    committed_delivery_date - planned_lead_calendar_days.
    """
    load_model_assets()

    planned_lead = int(round(_to_number(data.get("planned_lead_calendar_days"), 30)))

    committed_default = pd.Timestamp.today().normalize() + pd.Timedelta(days=max(planned_lead, 1))
    committed_date = _parse_date(data.get("committed_delivery_date"), committed_default, "committed_delivery_date", required=True)

    order_default = committed_date - pd.Timedelta(days=max(planned_lead, 1))
    order_date = _parse_date(
        data.get("order_placed_date", data.get("order_date", data.get("purchase_order_date"))),
        order_default,
        "order_placed_date",
        required=False,
    )

    row: Dict[str, Any] = {
        "material_category": normalize_category_value(data.get("material_category", DEFAULT_INPUTS["material_category"])),
        "supplier_tier": normalize_category_value(data.get("supplier_tier", DEFAULT_INPUTS["supplier_tier"])),
        "planned_lead_calendar_days": planned_lead,
        "distance_supplier_to_site_km": _to_number(data.get("distance_supplier_to_site_km"), 50),
        "delivery_terms": normalize_category_value(data.get("delivery_terms", DEFAULT_INPUTS["delivery_terms"])),
        "site_access_restriction_level": normalize_category_value(data.get("site_access_restriction_level", DEFAULT_INPUTS["site_access_restriction_level"])),
        "project_sector": normalize_category_value(data.get("project_sector", DEFAULT_INPUTS["project_sector"])),
        "region_site": normalize_category_value(data.get("region_site", DEFAULT_INPUTS["region_site"])),
        "order_value_band_gbp": normalize_category_value(data.get("order_value_band_gbp", DEFAULT_INPUTS["order_value_band_gbp"])),
        "shipment_mode": normalize_category_value(data.get("shipment_mode", DEFAULT_INPUTS["shipment_mode"])),
        "import_or_customs_hold_liable": normalize_category_value(data.get("import_or_customs_hold_liable", DEFAULT_INPUTS["import_or_customs_hold_liable"])),
        "made_to_order_or_long_fabrication": normalize_category_value(data.get("made_to_order_or_long_fabrication", DEFAULT_INPUTS["made_to_order_or_long_fabrication"])),
        "upstream_delay_flag_programme": normalize_category_value(data.get("upstream_delay_flag_programme", DEFAULT_INPUTS["upstream_delay_flag_programme"])),
        "market_shortage_stress_band": normalize_category_value(data.get("market_shortage_stress_band", DEFAULT_INPUTS["market_shortage_stress_band"])),
        "po_line_changes_before_release_count": int(round(_to_number(data.get("po_line_changes_before_release_count"), 0))),
        "weather_or_temperature_sensitive_goods": normalize_category_value(data.get("weather_or_temperature_sensitive_goods", DEFAULT_INPUTS["weather_or_temperature_sensitive_goods"])),
        "busy_season_construction_index": normalize_category_value(data.get("busy_season_construction_index", DEFAULT_INPUTS["busy_season_construction_index"])),
        "jit_critical_path_item": normalize_category_value(data.get("jit_critical_path_item", DEFAULT_INPUTS["jit_critical_path_item"])),
        "supplier_rolling_otif_band": normalize_category_value(data.get("supplier_rolling_otif_band", DEFAULT_INPUTS["supplier_rolling_otif_band"])),
        "haulier_capacity_stress_quarter": normalize_category_value(data.get("haulier_capacity_stress_quarter", DEFAULT_INPUTS["haulier_capacity_stress_quarter"])),
        "packaging_handling_complexity": normalize_category_value(data.get("packaging_handling_complexity", DEFAULT_INPUTS["packaging_handling_complexity"])),
        "order_month": int(order_date.month),
        "order_dayofweek": int(order_date.dayofweek),
        "committed_month": int(committed_date.month),
        "committed_dayofweek": int(committed_date.dayofweek),
        "committed_is_weekend": int(committed_date.dayofweek in [5, 6]),
    }

    # Guarantee exact training feature names and order.
    return pd.DataFrame([{column: row.get(column, DEFAULT_INPUTS.get(column, 0)) for column in feature_columns}])


def _format_feature_name(raw_name: str) -> str:
    name = raw_name.replace("num__", "").replace("cat__", "")

    known_prefixes = sorted(DEFAULT_INPUTS.keys(), key=len, reverse=True)
    known_prefixes.extend(["order_month", "order_dayofweek", "committed_month", "committed_dayofweek", "committed_is_weekend"])

    for prefix in known_prefixes:
        token = prefix + "_"
        if name.startswith(token):
            value = name[len(token):]
            return f"{prefix.replace('_', ' ').title()}: {value}"

    return name.replace("_", " ").title()


def _model_contributions(input_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Approximate feature contribution values for UI compatibility with the old SHAP display."""
    if preprocessor is None or model is None or not hasattr(model, "coef_"):
        return []

    try:
        transformed = preprocessor.transform(input_df)
        if hasattr(transformed, "toarray"):
            transformed = transformed.toarray()
        transformed = np.asarray(transformed)

        coefficients = np.asarray(model.coef_[0])
        contributions = transformed[0] * coefficients

        try:
            names = preprocessor.get_feature_names_out()
        except Exception:
            names = [f"feature_{index}" for index in range(len(contributions))]

        results = []
        for raw_name, value in zip(names, contributions):
            value = float(value)
            if abs(value) < 1e-6:
                continue
            clean_name = str(raw_name).replace("num__", "").replace("cat__", "")
            results.append({
                "feature": clean_name,
                "display_name": _format_feature_name(str(raw_name)),
                "shap_value": value,
            })

        results.sort(key=lambda item: abs(item["shap_value"]), reverse=True)
        return results[:8]
    except Exception as exc:
        print(f"Feature contribution generation failed: {exc}")
        return []


def _risk_level(probability: float) -> str:
    if probability >= 0.65:
        return "HIGH"
    if probability >= classification_threshold:
        return "MEDIUM"
    return "LOW"


def _expected_delay_days(probability: float) -> int:
    if probability >= 0.65:
        return max(4, int(round(probability * 8)))
    if probability >= classification_threshold:
        return max(2, int(round(probability * 5)))
    return max(0, int(round(probability * 2)))


def predict(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run delivery slippage prediction using the updated Logistic Regression pipeline."""
    load_model_assets()

    input_df = prepare_model_input(input_data)
    probability = float(pipeline.predict_proba(input_df)[0, 1])
    predicted_class = int(probability >= classification_threshold)
    shap_features = _model_contributions(input_df)

    return {
        "delay_probability": probability,
        "predicted_class": predicted_class,
        "risk_level": _risk_level(probability),
        "expected_delay_days": _expected_delay_days(probability),
        "shap_features": shap_features,
    }
