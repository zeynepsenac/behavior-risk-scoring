# ==========================================
# PROJECT ROOT PATH FIX (VERY IMPORTANT)
# ==========================================
import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(PROJECT_ROOT)

# ==========================================
# CENTRAL CONFIG (PRODUCTION SAFE ✅)
# ==========================================
from src.config.settings import DATABASE_TABLES
from src.database import load_customers

TABLE_NAME = DATABASE_TABLES["ENGINEERED"]

# ==========================================
# IMPORTS
# ==========================================
import json
from pathlib import Path
import pandas as pd
import joblib

from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

from utils.model_versioning import create_metadata


# ==========================================
# PATHS
# ==========================================
data_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "engineered_customers.csv"
)

model_dir = os.path.join(PROJECT_ROOT, "models")
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "risk_model.pkl")
metrics_path = os.path.join(model_dir, "model_metrics.json")


# ==========================================
# LOAD DATA (DB FIRST → CSV FALLBACK ✅)
# ==========================================
try:
    print("📦 Loading data from PostgreSQL...")
    df = load_customers()
    print(f"✅ Loaded {len(df)} rows from DB table: {TABLE_NAME}")

except Exception as e:
    print("⚠ Database load failed — switching to CSV fallback")
    print(e)

    df = pd.read_csv(data_path)
    print(f"✅ Loaded {len(df)} rows from CSV")


# ==========================================
# FEATURE SELECTION
# ==========================================
FEATURES = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

X = df[FEATURES]
y = df["risk_score"]


# ==========================================
# TRAIN / TEST SPLIT
# ==========================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ==========================================
# TRAIN MODEL
# ==========================================
model = XGBRegressor(
    n_estimators=120,
    max_depth=4,
    learning_rate=0.05,
    random_state=42
)

print("🚀 Training model...")
model.fit(X_train, y_train)


# ==========================================
# VALIDATION METRICS
# ==========================================
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)

print(f"📊 Validation MAE: {round(mae, 4)}")


# ==========================================
# SAVE MODEL
# ==========================================
joblib.dump(model, model_path)
print(f"✅ Model saved at: {model_path}")


# ==========================================
# SAVE MODEL METRICS (SINGLE SOURCE ⭐)
# ==========================================
metrics = {
    "model_type": "XGBRegressor",
    "problem_type": "regression",
    "metric": "MAE",
    "mae": float(mae),
    "training_samples": int(len(X_train)),
    "validation_samples": int(len(X_test)),
    "feature_count": len(FEATURES),
    "features": FEATURES
}

with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=4)

print("✅ model_metrics.json created")


# ==========================================
# CREATE MODEL METADATA (AUTO VERSIONING)
# ==========================================
create_metadata(
    features=FEATURES,
    feature_version="v1"
)

print("✅ Model trained, metadata and metrics generated")