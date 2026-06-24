import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ML_DIR = BASE_DIR / "backend" / "ml"
DATABASE_DIR = BASE_DIR / "database"

# Database Configuration
# Fallback to SQLite locally, using absolute path to avoid cwd confusion
LOCAL_SQLITE_URL = f"sqlite:///{DATABASE_DIR}/supply_chain.db"
DATABASE_URL = os.getenv("DATABASE_URL", LOCAL_SQLITE_URL)
if DATABASE_URL.startswith("postgres://"):
    # Fix Render/Heroku PostgreSQL urls starting with postgres:// instead of postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Security & JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-construction-platform-key-99881122")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours session

# OpenAI API Configuration (For Explanation & Copilot RAG)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Machine Learning Assets
# Updated to the new notebook-exported Logistic Regression Pipeline.
MODEL_PATH = os.getenv("MODEL_PATH", str(ML_DIR / "final_model_pipeline.joblib"))
FEATURE_COLUMNS_PATH = os.getenv("FEATURE_COLUMNS_PATH", str(ML_DIR / "feature_columns.json"))
METADATA_PATH = os.getenv("METADATA_PATH", str(ML_DIR / "metadata.json"))
CLASSIFICATION_THRESHOLD = float(os.getenv("CLASSIFICATION_THRESHOLD", "0.45"))
