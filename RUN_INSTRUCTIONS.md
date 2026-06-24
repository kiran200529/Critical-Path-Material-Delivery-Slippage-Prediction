# Run Instructions

## Project Name

Critical-Path Material Delivery Slippage Prediction

This project is a FastAPI-based machine learning web application for predicting whether a scheduled construction material delivery is likely to be delayed by more than three working days after the committed delivery date.

---

## Recommended Folder Location

To avoid Windows long-path installation issues, keep the project in a short folder path such as:

```text
C:\ML_APP\ML-proj-kiran
```

Avoid running the project from a long OneDrive path such as:

```text
C:\Users\<user>\OneDrive - Company Name\Documents\...\very\long\folder\path
```

Long folder paths may cause package installation errors while installing libraries such as `scikit-learn` and `joblib`.

---

## Folder to Open in VS Code

Open this folder in VS Code:

```text
C:\ML_APP\ML-proj-kiran
```

The folder should contain:

```text
backend
database
frontend
requirements.txt
README.md
RUN_INSTRUCTIONS.md
PROJECT_UPDATE_NOTES.md
```

---

## Create Virtual Environment

From the VS Code terminal, run:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal should show:

```text
(.venv) PS C:\ML_APP\ML-proj-kiran>
```

---

## Install Required Packages

Run:

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

If any package is missing, install the core application dependencies manually:

```powershell
python -m pip install fastapi uvicorn pandas numpy scikit-learn joblib SQLAlchemy email-validator "python-jose[cryptography]" "passlib[bcrypt]" bcrypt python-multipart
```

---

## Run the Application

Run the FastAPI server:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8050
```

Open the application in a browser:

```text
http://127.0.0.1:8050
```

---

## Stop the Application

To stop the server, press:

```text
Ctrl + C
```

in the VS Code terminal.

---

## Important Notes

* The active backend entry point is:

```text
backend/main.py
```

* The active frontend is served from:

```text
backend/static/index.html
backend/static/app.js
backend/static/styles.css
```

* The deployed ML model is stored at:

```text
backend/ml/final_model_pipeline.joblib
```

* The model feature list is stored at:

```text
backend/ml/feature_columns.json
```

* The model metadata is stored at:

```text
backend/ml/metadata.json
```

* The application uses a Logistic Regression pipeline with a decision threshold of `0.45`.

* The prediction target is whether the delivery is delayed by more than three working days after the committed delivery date.

---

## Common Errors and Fixes

### Error: No module named backend

Reason: The command was run from the wrong folder.

Fix: Make sure the terminal is inside the project root folder where `backend` and `requirements.txt` are visible.

Correct folder:

```text
C:\ML_APP\ML-proj-kiran
```

Correct command:

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8050
```

---

### Error: No module named sqlalchemy

Fix:

```powershell
python -m pip install SQLAlchemy
```

---

### Error: No module named email_validator

Fix:

```powershell
python -m pip install email-validator
```

---

### Error: No module named jose

Fix:

```powershell
python -m pip install "python-jose[cryptography]"
```

---

### Error: No module named sklearn

Fix:

```powershell
python -m pip install scikit-learn
```

---

### Windows Long Path Error While Installing Packages

Reason: The project is inside a very long folder path.

Fix: Move the project to a short path such as:

```text
C:\ML_APP\ML-proj-kiran
```

Then create a new virtual environment and install requirements again.

---

## Final Run Command Summary

Use these commands whenever you want to run the app:

```powershell
cd C:\ML_APP\ML-proj-kiran
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8050
```

Then open:

```text
http://127.0.0.1:8050
```
