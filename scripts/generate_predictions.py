import sys
import os

# --- PROJECT ROOT PATH FIX ---
# scripts klasöründen bir üst dizini Python path'e ekler
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

import pandas as pd
import joblib
from src.database import load_customers


print("Loading customer data...")

# load data from SQL
df = load_customers()

FEATURES = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

print("Loading trained model...")

# load trained model
model_path = os.path.join(PROJECT_ROOT, "models", "risk_model.pkl")
model = joblib.load(model_path)

print("Generating predictions...")

# predict risk score
df["predicted_risk_score"] = model.predict(df[FEATURES])

# validation dataset
output = df[
    [
        "risk_score",
        "predicted_risk_score",
        "monthly_income"
    ]
]

# save CSV
output_path = os.path.join(PROJECT_ROOT, "data", "predictions.csv")
output.to_csv(output_path, index=False)

print(" predictions.csv created successfully!")
print(f"Saved at: {output_path}")