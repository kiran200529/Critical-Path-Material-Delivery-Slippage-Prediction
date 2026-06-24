// Type Definitions for Slippage Shield Next.js Frontend

export interface User {
  id: number;
  name: string;
  email: string;
  role: 'Admin' | 'Procurement Manager' | 'Project Manager';
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Supplier {
  id: number;
  name: string;
  supplier_type: string;
  risk_score: number;
  performance_rating: number;
  created_at: string;
}

export interface SupplierProfile extends Supplier {
  reliability_score: number;
  total_orders: number;
  delayed_orders: number;
  delivery_success_rate: number;
  average_delay_days: number;
  risk_status: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface Material {
  id: number;
  material_name: string;
  category: string;
  unit_cost: number;
}

export interface Order {
  id: number;
  supplier_id: number;
  material_id: number;
  quantity: number;
  order_date: string;
  delivery_date: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  prediction_probability: number;
}

export interface Alert {
  id: number;
  order_id: number;
  alert_type: 'CRITICAL' | 'WARNING';
  message: string;
  created_at: string;
}

export interface Prediction {
  id: number;
  order_id: number;
  probability: number;
  expected_delay_days: number;
  prediction_timestamp: string;
}

export interface PredictRequest {
  committed_delivery_date: string;
  planned_lead_calendar_days: number;
  distance_supplier_to_site_km: number;
  material_category: string;
  supplier_tier: string;
  delivery_terms: string;
  site_access_restriction_level: string;
  project_sector: string;
  region_site: string;
  order_value_band_gbp: string;
  shipment_mode: string;
  import_or_customs_hold_liable: string;
  made_to_order_or_long_fabrication: string;
  upstream_delay_flag_programme: string;
  market_shortage_stress_band: string;
  po_line_changes_before_release_count: number;
  weather_or_temperature_sensitive_goods: string;
  busy_season_construction_index: string;
  jit_critical_path_item: string;
  supplier_rolling_otif_band: string;
  haulier_capacity_stress_quarter: string;
  packaging_handling_complexity: string;
}

export interface ShapFeatureInfo {
  feature: string;
  display_name: string;
  shap_value: number;
}

export interface PredictResponse {
  delay_probability: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  expected_delay_days: number;
  shap_features: ShapFeatureInfo[];
  ai_explanation: string;
}

export interface PlannerRequest {
  required_delivery_date: string;
  predicted_delay_days: number;
  safety_buffer_days: number;
  planned_lead_days: number;
}

export interface PlannerResponse {
  required_delivery_date: string;
  planned_lead_days: number;
  predicted_delay_days: number;
  safety_buffer_days: number;
  total_lead_time_days: number;
  recommended_order_date: string;
}

export interface WhatIfRequest {
  material_category: string;
  current_supplier_tier: string;
  target_supplier_tier: string;
  current_shipment_mode: string;
  target_shipment_mode: string;
  committed_delivery_date: string;
  planned_lead_calendar_days?: number;
  distance_supplier_to_site_km?: number;
}

export interface WhatIfResponse {
  current_risk_score: number;
  target_risk_score: number;
  risk_difference: number;
  improvement_percentage: number;
  expected_delay_days_saved: number;
  expected_cost_saving_gbp: number;
}
