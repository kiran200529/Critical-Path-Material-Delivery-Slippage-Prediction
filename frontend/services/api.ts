// API Service Layer for Next.js Frontend
// Connects UI components to the FastAPI backend endpoints

import { 
  Token, User, PredictRequest, PredictResponse, 
  SupplierProfile, PlannerRequest, PlannerResponse, 
  WhatIfRequest, WhatIfResponse 
} from '../types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8050/api';

// Helper to get auth headers
const getHeaders = (contentType = 'application/json') => {
  const headers: Record<string, string> = {};
  if (contentType) {
    headers['Content-Type'] = contentType;
  }
  
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }
  return headers;
};

export const apiService = {
  // Authentication
  async login(email: string, password: string): Promise<Token> {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error('Authentication failed');
    return res.json();
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${BASE_URL}/auth/me`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to retrieve user profile');
    return res.json();
  },

  // Predictor
  async predict(payload: PredictRequest): Promise<PredictResponse> {
    const res = await fetch(`${BASE_URL}/predict`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Prediction request failed');
    return res.json();
  },

  // Suppliers Intel
  async getSuppliers(): Promise<SupplierProfile[]> {
    const res = await fetch(`${BASE_URL}/suppliers`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch suppliers list');
    return res.json();
  },

  async getSupplierMaterials(): Promise<any[]> {
    const res = await fetch(`${BASE_URL}/suppliers/materials`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch materials catalog');
    return res.json();
  },

  // Planner
  async calculatePlanner(payload: PlannerRequest): Promise<PlannerResponse> {
    const res = await fetch(`${BASE_URL}/planner/calculate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Planner calculation failed');
    return res.json();
  },

  async getPlannerDefaults(supplierId: number, materialId: number, requiredDate: string): Promise<any> {
    const res = await fetch(`${BASE_URL}/planner/defaults?supplier_id=${supplierId}&material_id=${materialId}&required_delivery_date=${requiredDate}`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to retrieve planner defaults');
    return res.json();
  },

  // What-If Simulator
  async simulateWhatIf(payload: WhatIfRequest): Promise<WhatIfResponse> {
    const res = await fetch(`${BASE_URL}/what-if/simulate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('What-if simulation failed');
    return res.json();
  },

  // Analytics
  async getKpis(): Promise<any> {
    const res = await fetch(`${BASE_URL}/analytics/kpis`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to load KPIs');
    return res.json();
  },

  async getChartsData(): Promise<any> {
    const res = await fetch(`${BASE_URL}/analytics/charts`, {
      headers: getHeaders()
    });
    if (!res.ok) throw new Error('Failed to load charts datasets');
    return res.json();
  },

  // Copilot Chat
  async chatWithCopilot(question: string): Promise<{ answer: string; sources: string[] }> {
    const res = await fetch(`${BASE_URL}/copilot/chat`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ question })
    });
    if (!res.ok) throw new Error('Copilot communication failed');
    return res.json();
  }
};
