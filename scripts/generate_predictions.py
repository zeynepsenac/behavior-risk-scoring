# ==========================================
# PROJECT ROOT PATH FIX (ALWAYS FIRST)
# ==========================================
import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.append(PROJECT_ROOT)

# ==========================================
# IMPORTS
# ==========================================
import json
import pandas as pd
import joblib
from datetime import datetime

from src.database import load_customers
from src.database import save_predictions_to_db


# ==========================================
# MODEL METADATA READER (VERSIONING)
# ==========================================
def get_model_metadata():
    metadata_path = os.path.join(
        PROJECT_ROOT,
        "models",
        "metadata.json"
    )

    if not os.path.exists(metadata_path):
        raise FileNotFoundError("metadata.json not found!")

    with open(metadata_path, "r") as f:
        return json.load(f)


# ==========================================
# ✅ RISK BAND CALCULATOR (NEW)
# ==========================================
def calculate_risk_band(score: float) -> str:
    if score < 5:
        return "Low"
    elif score < 15:
        return "Medium"
    else:
        return "High"


# ==========================================
# LOAD DATA
# ==========================================
print("Loading customer data...")

df = load_customers()

print("Columns from DB:", df.columns)

if "customer_id" not in df.columns:
    raise ValueError(
        "customer_id column missing! "
        "Add it to load_customers() SQL query."
    )

FEATURES = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

# ==========================================
# LOAD MODEL
# ==========================================
print("Loading trained model...")

model_path = os.path.join(PROJECT_ROOT, "models", "risk_model.pkl")

if not os.path.exists(model_path):
    raise FileNotFoundError("risk_model.pkl not found!")

model = joblib.load(model_path)

# ==========================================
# LOAD MODEL VERSION INFO
# ==========================================
metadata = get_model_metadata()

model_hash = metadata["model_hash"]
training_timestamp = metadata.get(
    "training_timestamp",
    datetime.now().strftime("%Y%m%d")
)

FEATURE_VERSION = metadata.get("feature_version", "features_v1")

MODEL_VERSION = (
    f"{FEATURE_VERSION}_"
    f"{model_hash[:8]}_"
    f"{training_timestamp}"
)

print(f"Using model hash: {model_hash}")
print(f"Model version: {MODEL_VERSION}")

# ==========================================
# GENERATE PREDICTIONS
# ==========================================
print("Generating predictions...")

df["predicted_risk_score"] = model.predict(df[FEATURES])

# ==========================================
# ✅ PREDICTED BAND (NEW - NOT NULL FIX)
# ==========================================
df["predicted_band"] = df["predicted_risk_score"].apply(
    calculate_risk_band
)

if df["predicted_band"].isnull().any():
    raise ValueError("predicted_band contains NULL values!")

# ==========================================
# ORIGINAL BAND (NOT NULL FIX)
# ==========================================
if "risk_band" not in df.columns:
    raise ValueError(
        "risk_band column missing from engineered_features table!"
    )

# audit trail
df["original_band"] = df["risk_band"]

if df["original_band"].isnull().any():
    raise ValueError("original_band contains NULL values!")

# tracking fields
df["model_hash"] = model_hash
df["model_version"] = MODEL_VERSION

# ==========================================
# DB SCHEMA ALIGNMENT
# ==========================================
df["risk_score"] = df["predicted_risk_score"]

# ==========================================
# SAVE PREDICTIONS TO DATABASE
# ==========================================
print("Saving predictions to database...")

save_predictions_to_db(
    df[
        [
            "customer_id",
            "risk_score",
            "original_band",
            "predicted_band",   # ✅ NEW COLUMN
            "model_hash",
            "model_version"
        ]
    ]
)

print("Predictions saved to DB.")

# ==========================================
# CREATE VALIDATION DATASET
# ==========================================
output = df[
    [
        "risk_score",
        "predicted_risk_score",
        "predicted_band",   # ✅ added for validation visibility
        "model_hash",
        "model_version"
    ]
]

# ==========================================
# SAVE CSV
# ==========================================
output_path = os.path.join(PROJECT_ROOT, "data", "predictions.csv")
output.to_csv(output_path, index=False)

print("✅ predictions.csv created successfully!")
print(f"Saved at: {output_path}")