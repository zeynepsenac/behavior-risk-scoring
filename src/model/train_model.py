import pandas as pd
import joblib
import numpy as np
import json
from pathlib import Path
from lime.lime_tabular import LimeTabularExplainer

print(" Generating predictions...")

# =========================
# PATH SETUP (FIXED)
# =========================
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# =========================
# MODEL + SCALER LOAD
# =========================
model = joblib.load(MODEL_DIR / "risk_model_v2.pkl")
scaler = joblib.load(MODEL_DIR / "scaler_v2.pkl")

# TRAIN DATA (FIXED PATH)
X_train_scaled = joblib.load(MODEL_DIR / "X_train_scaled_v2.pkl")

# =========================
# DATA LOAD
# =========================
df = pd.read_csv(DATA_DIR / "engineered_customers.csv")

# =========================
# SAFE CHECK
# =========================
if "financial_resilience_score" not in df.columns:
    raise ValueError("financial_resilience_score missing from dataset")

if df["financial_resilience_score"].isna().sum() > 0:
    print(" WARNING: NaN values found in financial_resilience_score")
    df["financial_resilience_score"] = df["financial_resilience_score"].fillna(0)

zero_ratio = (df["financial_resilience_score"] == 0).mean()
print(f" Resilience zero ratio: {zero_ratio:.2%}")

# =========================
# FEATURES
# =========================
feature_cols = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

X = df[feature_cols].astype(float)

# =========================
# SCALE INPUT
# =========================
X_scaled = scaler.transform(X)

# =========================
# PREDICTION
# =========================
raw_preds = model.predict(X_scaled)

preds = raw_preds / 25.0
preds = np.clip(preds, 0, 1)

df["predicted_risk_score"] = preds

df["predicted_band"] = pd.cut(
    df["predicted_risk_score"],
    bins=[0, 0.33, 0.66, 1],
    labels=["DÜŞÜK", "ORTA", "YÜKSEK"],
    include_lowest=True
)

# =========================
# LIME SETUP
# =========================
X_train_scaled = np.asarray(X_train_scaled, dtype=float)

explainer = LimeTabularExplainer(
    training_data=X_train_scaled,
    feature_names=feature_cols,
    mode="regression"
)

def predict_fn(x):
    x = np.asarray(x, dtype=float)
    preds = model.predict(x)
    preds = preds / 25.0
    return np.clip(preds, 0, 1)

# =========================
# LIME LOOP
# =========================
lime_results_all = []

for i in range(len(X_scaled)):

    exp = explainer.explain_instance(
        X_scaled[i],
        predict_fn,
        num_features=3
    )

    cleaned = []

    for item in exp.as_list():
        try:
            f, v = item

            if isinstance(v, str):
                continue

            v = float(v)
            feature_name = str(f)

            for col in feature_cols:
                if col in feature_name:
                    feature_name = col
                    break

            cleaned.append({
                "feature": feature_name,
                "impact": v
            })

        except Exception:
            continue

    lime_results_all.append(cleaned)

df["lime_explanation"] = [
    json.dumps(x, ensure_ascii=False) for x in lime_results_all
]

# =========================
# BASE VALUE
# =========================
base_preds = model.predict(X_train_scaled)
base_preds = base_preds / 25.0
base_preds = np.clip(base_preds, 0, 1)

df["base_value"] = float(np.mean(base_preds))

# =========================
# METADATA
# =========================
df["model_hash"] = "b02a4b90e9feb18d0ef31562d8c2fa4a46c7b5812790cc777c6110e8a87b7c65"
df["model_version"] = "v1_fixed_scale"

# =========================
# OUTPUT
# =========================
output_cols = [
    "predicted_risk_score",
    "predicted_band",
    "model_hash",
    "model_version",
    "base_value",
    "lime_explanation"
]

df[output_cols].to_csv(DATA_DIR / "predictions.csv", index=False)

print(" predictions.csv başarıyla oluşturuldu (FIXED + CLEAN + STABLE)")