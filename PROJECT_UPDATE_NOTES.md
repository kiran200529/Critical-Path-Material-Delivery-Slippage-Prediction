# Project Update Notes

## Application type confirmed

The uploaded project is a FastAPI application serving an HTML/CSS/JavaScript single-page interface from:

- `backend/main.py`
- `backend/static/index.html`
- `backend/static/app.js`
- `backend/static/styles.css`

The `frontend/` folder contains Next.js template files, but the local VS Code run command serves the active static UI from `backend/static/`.

## Active ML model integration

The active model integration uses:

- `backend/ml/final_model_pipeline.joblib`
- `backend/ml/feature_columns.json`
- `backend/ml/metadata.json`

The backend loads these files through `backend/config.py` and `backend/ml/predictor.py`. The model is a scikit-learn pipeline with `predict_proba()` support. The active threshold is loaded from `metadata.json` and defaults to `0.45`.

No active backend/frontend code references old files such as `model.pkl`, `preprocessor.pkl`, or `metadata.pkl`.

## Files changed in this fix

### `backend/static/app.js`

- Added safe local date parsing.
- Added robust date picker normalization for `YYYY-MM-DD` and display-style `DD-MM-YYYY` fallback values.
- Avoided `toISOString()` completely.
- Ensured prediction payload sends committed delivery date in `YYYY-MM-DD`.
- Added clear required-date validation message.
- Added lead-time number validation.
- Moved date control initialization into `DOMContentLoaded` so the active date input exists before min/max are applied.
- Applied the same safe date normalization to planner and what-if date inputs.

### `backend/schemas/schemas.py`

- Kept backend date acceptance consistent with ISO `YYYY-MM-DD`.
- Added clearer missing committed-date message.
- Kept business validation that blocks far-future committed dates when planned lead time is unrealistically short.

### `backend/api/routes/predict.py`

- Replaced deprecated Pydantic `.dict()` usage with `.model_dump()`.

### `frontend/app/prediction/page.tsx`

- Updated the Next.js prediction template with the same local date parsing and normalization logic for consistency, even though this is not the active local UI served by FastAPI.

### `RUN_INSTRUCTIONS.md`

- Added final verification notes and exact local run/test commands.

## Verified behavior

The following checks were performed successfully:

- Project imports from root.
- `backend.main:app` imports successfully.
- `requirements.txt` exists.
- Model path resolves to `backend/ml/final_model_pipeline.joblib`.
- Feature columns load from `backend/ml/feature_columns.json`.
- Metadata loads from `backend/ml/metadata.json`.
- ML pipeline loads successfully.
- Model feature count is 26.
- Classification threshold is 0.45.
- FastAPI root UI loads successfully.
- Prediction API returns a valid prediction for a valid date.
- Far-future date with short lead time is blocked.
- Far-future date with matching lead time is accepted.
- Empty committed delivery date is rejected clearly.
- Existing API tests pass.

## Test result

```text
python -m pytest -q backend/tests/test_api.py
7 passed
```
