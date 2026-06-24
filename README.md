# Critical-Path Material Delivery Slippage Prediction

This project is a machine learning-based construction procurement intelligence application designed to predict whether a scheduled site material delivery is likely to arrive more than three working days after the committed delivery date.

The application uses a trained Logistic Regression pipeline with threshold-based classification to identify high-risk material deliveries. It supports delivery risk prediction, business decision summaries, recommended action plans, supplier monitoring, procurement planning, what-if simulation, analytics visualization, and alert-style project monitoring.

The main objective of this project is to help planners, procurement teams, and project managers identify risky material deliveries early so they can follow up with suppliers, arrange alternate carriers, resequence work, or escalate critical-path risks before delays affect construction progress.

## Problem Statement

Construction projects often depend on timely delivery of critical materials. If a scheduled material drop arrives late, downstream construction activities may be delayed, project sequencing may be affected, and critical-path work can suffer. Manual monitoring alone may not identify high-risk deliveries early enough for planners to take preventive action.

This project solves the problem by predicting whether a scheduled site material delivery will arrive more than three working days after the committed delivery date.

## Prediction Target

The machine learning target column used in this project is:

```text
material_delivery_delayed_gt_3_working_days
```

Target meaning:

```text
0 = Delivery is not delayed by more than three working days
1 = Delivery is delayed by more than three working days
```

## Final Model Details

The final deployed model is a threshold-tuned Logistic Regression pipeline.

```text
Model Type: Logistic Regression
Decision Threshold: 0.45
Prediction Method: predict_proba()
Target: Delay greater than three working days
Input Features: 26
Model Artifact: backend/ml/final_model_pipeline.joblib
Feature Columns: backend/ml/feature_columns.json
Metadata File: backend/ml/metadata.json
```

Logistic Regression was selected because the project focuses on identifying delayed deliveries early. The model selection gives importance to delayed-class recall and F1-score, which are more useful for risk detection than accuracy alone.

## Application Architecture

The application is implemented as a FastAPI-based machine learning web application.

```text
backend/main.py                    FastAPI application entry point
backend/api/routes/                API route handlers
backend/schemas/                   Request and response validation schemas
backend/ml/                        Trained model and feature files
backend/static/                    Active HTML, CSS, and JavaScript frontend
database/                          Database-related files
requirements.txt                   Python package dependencies
RUN_INSTRUCTIONS.md                Steps to run the application
```

The active user interface is served from:

```text
backend/static/index.html
backend/static/app.js
backend/static/styles.css
```

The `frontend/` folder is retained as an optional or future frontend extension. It is not required for the current FastAPI run command.
## Current Limitations

This application is designed as a machine learning decision-support system for construction material delivery risk prediction. The current version has the following limitations:

* The model predicts delay risk using historical structured delivery features and does not use live GPS tracking data.
* The application does not currently integrate real-time traffic, weather, or port/customs API data.
* Some dashboard, alert, analytics, and simulator sections may use demo data for visualization and presentation purposes.
* The prediction output should support planner decision-making, but it should not completely replace human judgment.
* The model performance depends on the quality, completeness, and representativeness of the training dataset.
* The application is currently designed for local execution in VS Code using FastAPI and Uvicorn.

## Future Enhancements

The following improvements can be added in future versions of the project:

* Integrate live shipment tracking data from logistics providers.
* Add real-time traffic, weather, and customs-status API integration.
* Store prediction history and planner actions in a production database.
* Add role-based dashboards for procurement teams, planners, and project managers.
* Improve explainability using SHAP or LIME-based model interpretation.
* Add automated email or notification alerts for high-risk deliveries.
* Deploy the application on a cloud platform for remote access.
* Add supplier performance benchmarking using historical OTIF and delay records.
* Extend the what-if simulator to compare supplier, carrier, and lead-time alternatives.
* Add downloadable prediction reports in PDF or Excel format.

---

## 1. Project Directory Structure

```text
ML-proj-kiran/
├── backend/
│   ├── api/
│   │   ├── dependencies/
│   │   │   └── auth.py             # JWT & Role Access Controls
│   │   ├── middleware/
│   │   └── routes/
│   │       ├── auth.py             # Auth endpoints (signup/login/me)
│   │       ├── predict.py          # ML prediction, feature contributions, and AI explanations
│   │       ├── suppliers.py        # Supplier scorecards, rankings, materials
│   │       ├── planner.py          # Lead days & buffer arithmetic calculator
│   │       ├── analytics.py        # Dashboard KPIs & aggregated charts
│   │       ├── copilot.py          # AI procurement assistant chat
│   │       ├── what_if.py          # Scenario simulation comparison
│   │       └── reports.py          # openpyxl Styled Excel spreadsheets generator
│   ├── database/
│   │   └── db.py                   # SQLAlchemy connection & DB auto-seeder
│   ├── ml/
│   │   ├── predictor.py            # Updated ML prediction wrapper
│   │   ├── final_model_pipeline.joblib  # New Logistic Regression pipeline
│   │   ├── feature_columns.json     # Exact 26 model input columns
│   │   └── metadata.json            # Threshold and model metadata
│   ├── models/
│   │   ├── user.py, supplier.py, material.py, order.py, alert.py, prediction.py
│   ├── schemas/
│   │   └── schemas.py              # Pydantic request/response validations
│   ├── services/
│   │   ├── prediction_service.py, supplier_service.py, planner_service.py,
│   │   ├── analytics_service.py, recommendation_service.py, ai_service.py
│   ├── static/                     # Instant Preview Local UI (SPA)
│   │   ├── index.html              # HTML DOM Layout
│   │   ├── app.js                  # Frontend controllers, Chart.js integrations
│   │   └── styles.css              # Glassmorphism dark-theme styling
│   ├── tests/
│   │   └── test_api.py             # Pytest automated test scripts
│   ├── config.py                   # Environment settings & JWT credentials
│   └── main.py                     # Uvicorn FastAPI server entrypoint
│
├── frontend/                       # Production Next.js App Router Templates
│   ├── app/
│   │   ├── dashboard/page.tsx, prediction/page.tsx, suppliers/page.tsx,
│   │   ├── planner/page.tsx, analytics/page.tsx, alerts/page.tsx,
│   │   ├── copilot/page.tsx, what-if/page.tsx
│   ├── components/
│   ├── services/
│   │   └── api.ts                  # Next.js API client caller wrapper
│   └── types/
│       └── index.ts                # TypeScript interfaces
│
└── database/
    ├── schema.sql                  # Production DDL PostgreSQL schema
    └── seed_data.sql               # Production seed insert statements
```

---

## 2. API Documentation

All routes reside under the `/api` prefix and require a JWT token (`Authorization: Bearer <token>`) except `/auth/signup` and `/auth/login`.

### Authentication
- `POST /auth/signup`: Registers a new user. Expects `UserCreate` JSON body.
- `POST /auth/login`: Validates credentials, returns JWT token. Expects `UserLogin` JSON body.
- `GET /auth/me`: Retrieves current active profile.

### Delivery Risk Prediction
- `POST /predict`: Evaluates slippage probability.
  - **Request Body**: JSON mapping all operational variables:
    - `committed_delivery_date`: string ("YYYY-MM-DD")
    - `planned_lead_calendar_days`: int
    - `distance_supplier_to_site_km`: int
    - `material_category`: string
    - `supplier_tier`: string
    - `delivery_terms`: string
    - `site_access_restriction_level`: string
    - `project_sector`: string
    - `region_site`: string
    - `order_value_band_gbp`: string
    - `shipment_mode`: string
  - **Response Output**:
    ```json
    {
      "delay_probability": 0.82,
      "risk_score": 82,
      "risk_level": "HIGH",
      "expected_delay_days": 6,
      "shap_features": [
        { "feature": "supplier_tier_Spot / Non-Framework", "display_name": "Supplier Tier: Spot / Non-Framework", "shap_value": 0.185 }
      ],
      "ai_explanation": "This delivery is likely to be delayed because..."
    }
    ```

### Supplier Risk Intelligence
- `GET /suppliers`: Lists all suppliers sorted by reliability rating.
- `GET /suppliers/materials`: Lists the material product catalog.
- `GET /suppliers/rankings`: Returns Top 5 Performers and High-Risk Suppliers.
- `GET /suppliers/{supplier_id}`: Retrieves detailed OTIF metrics for a specific partner.

### Procurement Planner
- `POST /planner/calculate`: Computes scheduled order dates.
  - **Request Body**: `required_delivery_date`, `predicted_delay_days`, `safety_buffer_days`, `planned_lead_days`.
  - **Response**: `recommended_order_date`.
- `GET /planner/defaults`: Fetch default values (estimated lead time & delay predictions) for a material/supplier.

### Scenario Simulator
- `POST /what-if/simulate`: Compares baseline operational parameters vs simulated target values. Returns delta cost impacts, risk drop percentages, and days saved.

### AI Procurement Copilot
- `POST /copilot/chat`: Process natural language questions using available project and delivery records. Returns structured procurement-support responses.

### Report Downloads (Streaming Excel)
- `GET /reports/suppliers`: Streams the Supplier Performance spreadsheet.
- `GET /reports/risk-assessment`: Streams the Active Risk logs spreadsheet.
- `GET /reports/planning`: Streams the Procurement Scheduling spreadsheet.
- `GET /reports/project-delays`: Streams the Project sites health registers spreadsheet.

---

## 3. Local Execution Guide

### Prerequisites
Make sure Python 3.10+ is installed along with the required libraries:
```bash
pip install -r requirements.txt
```

### Start Server
Run the application from the root directory:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8050 --reload
```
Open [http://127.0.0.1:8050](http://127.0.0.1:8050) on your web browser to access the complete, interactive SPA interface.

### Running Unit Tests
Validate database connections, prediction algorithms, and REST routes:
```bash
python -m pytest backend/tests/test_api.py
```

---

## 4. Deployment Guide

### A. Backend Deployment (Render)
1. Register a PostgreSQL database instance on Render.
2. Create a new **Web Service** on Render and connect your GitHub repository.
3. Configure the environment variables:
   - `DATABASE_URL`: Set to your Render PostgreSQL connection string.
   - `JWT_SECRET`: Define a secure secret string.
   - `OPENAI_API_KEY`: Paste your OpenAI API token (optional; triggers fallbacks if empty).
4. Define build and start commands:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### B. Database Initialization in Production
During application startup, SQLAlchemy automatically queries the active database. If deploying on PostgreSQL, it runs `Base.metadata.create_all` to verify tables exist, and seeds user profiles and materials automatically if the records are blank.
Alternatively, you can run the DDL declarations in `database/schema.sql` and seeding insert rows in `database/seed_data.sql` directly on your database client.

### C. Frontend Deployment (Vercel)
1. Push the repository to GitHub.
2. In the Vercel dashboard, click **Add New Project** and import the repository.
3. Set the root directory of the deployment to `frontend`.
4. Configure environment variables:
   - `NEXT_PUBLIC_API_URL`: Paste the URL of your active Render FastAPI backend (e.g. `https://your-backend.onrender.com/api`).
5. For the current version, run the FastAPI application locally using Uvicorn. The active user interface is served from `backend/static`.


## Updated Model Integration

This version uses the newly trained Logistic Regression pipeline exported from the updated notebook. The active model files are placed in `backend/ml/`:

- `final_model_pipeline.joblib`
- `feature_columns.json`
- `metadata.json`

The selected classification threshold is `0.45`. The backend derives the new notebook date features (`order_month`, `order_dayofweek`, `committed_month`, `committed_dayofweek`, and `committed_is_weekend`) before calling the model.

## Date and Lead-Time Validation

The model predicts whether a delivery will arrive more than three working days after the committed delivery date. A committed date far in the future does not automatically mean the delivery is safe, because supplier reliability, customs risk, access restrictions, market shortage stress, shipment mode, and other operational factors still matter.

To avoid misleading predictions, the dashboard and backend now check whether the committed delivery date is consistent with the entered `planned_lead_calendar_days`.

Example: if the committed delivery date is 365 days from today but the planned lead time is only 30 days, the app will block the prediction and ask the user to correct the lead time or provide a consistent order placed date. This prevents the model from treating a one-year future date as a normal 30-day operational delivery.

For VS Code setup and run commands, see `RUN_INSTRUCTIONS.md`.
