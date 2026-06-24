'use client';

import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';
import { PredictResponse, Material, SupplierProfile } from '../../types';

export default function PredictionPage() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [suppliers, setSuppliers] = useState<SupplierProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  
  // Form State
  const [form, setForm] = useState({
    committed_delivery_date: '',
    planned_lead_calendar_days: 30,
    distance_supplier_to_site_km: 50,
    material_index: '0',
    supplier_index: '0',
    delivery_terms: 'DAP - Delivered at Site',
    site_access_restriction_level: 'Standard Laydown',
    project_sector: 'Commercial / Offices',
    region_site: 'London & South East',
    order_value_band_gbp: '£15k - £75k',
    shipment_mode: 'Full Load - Direct',
    import_or_customs_hold_liable: 'No'
  });

  useEffect(() => {
    async function loadData() {
      try {
        const mats = await apiService.getSupplierMaterials();
        const sups = await apiService.getSuppliers();
        setMaterials(mats);
        setSuppliers(sups);
        
        // Default date
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 14);
        setForm(f => ({ ...f, committed_delivery_date: toIsoDate(tomorrow) }));
      } catch (e) {
        console.error('Error fetching master lists', e);
      }
    }
    loadData();
  }, []);

  const MAX_PREDICTION_HORIZON_DAYS = 365;
  const MAX_UNEXPLAINED_BUFFER_DAYS = 60;

  const todayAtMidnight = () => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
  };

  const toIsoDate = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const buildLocalDate = (year: number, month: number, day: number) => {
    const date = new Date(year, month - 1, day);
    if (
      date.getFullYear() !== year ||
      date.getMonth() !== month - 1 ||
      date.getDate() !== day
    ) {
      return null;
    }
    return date;
  };

  const parseIsoDateLocal = (value: string) => {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec((value || '').trim());
    if (!match) return null;
    return buildLocalDate(Number(match[1]), Number(match[2]), Number(match[3]));
  };

  const parseDisplayDateLocal = (value: string) => {
    const cleaned = (value || '').trim();
    const ddmmyyyy = /^(\d{2})[-/](\d{2})[-/](\d{4})$/.exec(cleaned);
    if (ddmmyyyy) {
      return buildLocalDate(Number(ddmmyyyy[3]), Number(ddmmyyyy[2]), Number(ddmmyyyy[1]));
    }
    const yyyymmddSlash = /^(\d{4})[/](\d{2})[/](\d{2})$/.exec(cleaned);
    if (yyyymmddSlash) {
      return buildLocalDate(Number(yyyymmddSlash[1]), Number(yyyymmddSlash[2]), Number(yyyymmddSlash[3]));
    }
    return null;
  };

  const normalizeDateValue = (value: string) => {
    const parsedDate = parseIsoDateLocal(value) || parseDisplayDateLocal(value);
    return parsedDate ? toIsoDate(parsedDate) : null;
  };

  const addDays = (date: Date, days: number) => {
    const copy = new Date(date.getTime());
    copy.setDate(copy.getDate() + days);
    return copy;
  };

  const daysFromToday = (value: string) => {
    const selectedDate = parseIsoDateLocal(value);
    if (!selectedDate) return Number.NaN;
    const diffMs = selectedDate.getTime() - todayAtMidnight().getTime();
    return Math.round(diffMs / (1000 * 60 * 60 * 24));
  };

  const validatePredictionSchedule = (committedDate: string, plannedLeadDays: number) => {
    const daysUntilCommitted = daysFromToday(committedDate);
    if (daysUntilCommitted < 0) return 'Committed delivery date cannot be in the past.';
    if (daysUntilCommitted > MAX_PREDICTION_HORIZON_DAYS) {
      return `Committed delivery date is ${daysUntilCommitted} days from today. This model is intended for operational predictions up to ${MAX_PREDICTION_HORIZON_DAYS} days ahead.`;
    }
    const unexplainedBufferDays = daysUntilCommitted - plannedLeadDays;
    if (unexplainedBufferDays > MAX_UNEXPLAINED_BUFFER_DAYS) {
      return `Committed delivery date is ${daysUntilCommitted} days from today, but planned lead time is only ${plannedLeadDays} days. For a long-term order, increase planned lead time close to ${daysUntilCommitted} days instead of leaving it as ${plannedLeadDays}.`;
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const committedDate = normalizeDateValue(form.committed_delivery_date);
    if (!committedDate) {
      alert('Committed delivery date is required. Please select a valid committed delivery date from the date picker.');
      return;
    }

    if (!Number.isFinite(form.planned_lead_calendar_days) || form.planned_lead_calendar_days <= 0) {
      alert('Planned lead time must be a valid number greater than 0.');
      return;
    }

    const scheduleError = validatePredictionSchedule(committedDate, form.planned_lead_calendar_days);
    if (scheduleError) {
      alert(scheduleError);
      return;
    }

    setLoading(true);
    
    const selectedMat = materials[parseInt(form.material_index)];
    const selectedSup = suppliers[parseInt(form.supplier_index)];
    
    if (!selectedMat || !selectedSup) return;
    
    const payload = {
      committed_delivery_date: committedDate,
      planned_lead_calendar_days: form.planned_lead_calendar_days,
      distance_supplier_to_site_km: form.distance_supplier_to_site_km,
      material_category: selectedMat.category,
      supplier_tier: selectedSup.supplier_type,
      delivery_terms: form.delivery_terms,
      site_access_restriction_level: form.site_access_restriction_level,
      project_sector: form.project_sector,
      region_site: form.region_site,
      order_value_band_gbp: form.order_value_band_gbp,
      shipment_mode: form.shipment_mode,
      import_or_customs_hold_liable: form.import_or_customs_hold_liable,
      made_to_order_or_long_fabrication: 'Yes',
      upstream_delay_flag_programme: 'No',
      market_shortage_stress_band: 'Moderate',
      po_line_changes_before_release_count: 0,
      weather_or_temperature_sensitive_goods: 'No',
      busy_season_construction_index: 'Typical',
      jit_critical_path_item: 'No',
      supplier_rolling_otif_band: '85%  94%',
      haulier_capacity_stress_quarter: 'No',
      packaging_handling_complexity: 'Standard Pallet / Bulk'
    };
    
    try {
      const data = await apiService.predict(payload);
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getGaugeColor = (level: string) => {
    if (level === 'HIGH') return '#ef4444'; // Red
    if (level === 'MEDIUM') return '#f59e0b'; // Amber
    return '#10b981'; // Green
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
      {/* Form Card */}
      <div className="bg-slate-850 border border-slate-700 rounded-xl p-6 shadow-md">
        <h2 className="text-lg font-semibold text-white mb-6">Run Slippage Prediction</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-medium text-slate-400">Material Category</label>
              <select
                className="bg-slate-900 border border-slate-700 text-white rounded-lg p-2 text-sm"
                value={form.material_index}
                onChange={e => setForm({ ...form, material_index: e.target.value })}
              >
                {materials.map((m, i) => (
                  <option key={m.id} value={i}>{m.material_name}</option>
                ))}
              </select>
            </div>
            
            <div className="flex flex-col gap-2">
              <label className="text-xs font-medium text-slate-400">Proposed Supplier</label>
              <select
                className="bg-slate-900 border border-slate-700 text-white rounded-lg p-2 text-sm"
                value={form.supplier_index}
                onChange={e => setForm({ ...form, supplier_index: e.target.value })}
              >
                {suppliers.map((s, i) => (
                  <option key={s.id} value={i}>{s.name}</option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-medium text-slate-400">Committed Date</label>
              <input
                type="date"
                className="bg-slate-900 border border-slate-700 text-white rounded-lg p-2 text-sm"
                value={form.committed_delivery_date}
                onChange={e => setForm({ ...form, committed_delivery_date: e.target.value })}
                min={toIsoDate(todayAtMidnight())}
                max={toIsoDate(addDays(todayAtMidnight(), MAX_PREDICTION_HORIZON_DAYS))}
                required
              />
              <span className="text-[11px] text-slate-500">Keep this date consistent with the entered lead time.</span>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-medium text-slate-400">Lead Time (Days)</label>
              <input
                type="number"
                className="bg-slate-900 border border-slate-700 text-white rounded-lg p-2 text-sm"
                value={form.planned_lead_calendar_days}
                onChange={e => setForm({ ...form, planned_lead_calendar_days: parseInt(e.target.value) })}
                min={1}
                required
              />
              <span className="text-[11px] text-slate-500">For a one-year delivery window, enter around 365 days.</span>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-medium text-slate-400">Transit Distance (km)</label>
              <input
                type="number"
                className="bg-slate-900 border border-slate-700 text-white rounded-lg p-2 text-sm"
                value={form.distance_supplier_to_site_km}
                onChange={e => setForm({ ...form, distance_supplier_to_site_km: parseInt(e.target.value) })}
                min={1}
                required
              />
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-medium text-slate-400">Shipment Mode</label>
              <select
                className="bg-slate-900 border border-slate-700 text-white rounded-lg p-2 text-sm"
                value={form.shipment_mode}
                onChange={e => setForm({ ...form, shipment_mode: e.target.value })}
              >
                <option value="Full Load - Direct">Full Load - Direct</option>
                <option value="Consolidated Hub">Consolidated Hub</option>
                <option value="Part Load / Groupage">Part Load / Groupage</option>
                <option value="Courier / Parcel">Courier / Parcel</option>
              </select>
            </div>
          </div>
          
          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg text-sm transition"
            disabled={loading}
          >
            {loading ? 'Predicting...' : 'Predict Delivery Risk'}
          </button>
        </form>
      </div>

      {/* Results Card */}
      <div className="bg-slate-850 border border-slate-700 rounded-xl p-6 shadow-md flex flex-col justify-between">
        <h2 className="text-lg font-semibold text-white mb-4">Risk Output & Driver Contributions</h2>
        
        {!result ? (
          <div className="flex-grow flex flex-col items-center justify-center text-slate-500 py-12">
            <p>Enter data and click predict to render driver analytics.</p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center gap-6 bg-slate-900/50 p-4 border border-slate-800 rounded-lg">
              <div className="relative w-24 h-24 rounded-full flex items-center justify-center" style={{
                background: `conic-gradient(${getGaugeColor(result.risk_level)} ${Math.round(result.delay_probability * 100)}%, #334155 0%)`
              }}>
                <div className="absolute w-20 h-20 bg-slate-850 rounded-full flex items-center justify-center text-white font-bold text-xl">
                  {Math.round(result.delay_probability * 100)}%
                </div>
              </div>
              <div>
                <h3 className="text-sm text-slate-400 font-medium uppercase tracking-wider">Delay Risk Level</h3>
                <div className="text-2xl font-bold mt-1" style={{ color: getGaugeColor(result.risk_level) }}>
                  {result.risk_level} RISK
                </div>
                <div className="text-sm text-slate-300 mt-1">
                  Expected Delay: <strong>{result.expected_delay_days} Working Days</strong>
                </div>
              </div>
            </div>

            <div className="bg-blue-900/20 border-l-4 border-blue-500 p-4 rounded-r-lg text-sm text-slate-300 leading-relaxed">
              <h4 className="font-semibold text-white mb-1"><i className="fa-solid fa-brain"></i> AI Explainer:</h4>
              <p>{result.ai_explanation}</p>
            </div>

            {/* Feature contribution chart */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Operational Risk Driver Contributions</h4>
              <div className="space-y-2">
                {result.shap_features.map((f, i) => (
                  <div key={i} className="flex items-center gap-4 text-xs">
                    <span className="w-36 text-right truncate text-slate-400" title={f.display_name}>{f.display_name}</span>
                    <div className="flex-grow h-4 bg-slate-800 rounded relative">
                      <div className="h-2.5 rounded absolute top-0.75" style={{
                        backgroundColor: f.shap_value > 0 ? '#ef4444' : '#10b981',
                        width: `${Math.min(50, Math.round(Math.abs(f.shap_value) * 100))}%`,
                        left: f.shap_value > 0 ? '50%' : 'auto',
                        right: f.shap_value > 0 ? 'auto' : '50%',
                      }}></div>
                    </div>
                    <span className="w-12 text-slate-300 font-mono">
                      {f.shap_value > 0 ? '+' : ''}{f.shap_value.toFixed(3)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
