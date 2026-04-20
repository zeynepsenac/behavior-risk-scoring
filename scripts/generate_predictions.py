import pandas as pd
import joblib
import numpy as np
import json
from lime.lime_tabular import LimeTabularExplainer

print("🔄 Generating predictions...")

# ================================
# MODEL + SCALER LOAD
# ================================
model = joblib.load("models/risk_model_v2.pkl")
scaler = joblib.load("models/scaler_v2.pkl")

# ================================
# TRAIN DATA LOAD (🔥 CLEAN FIX)
# ================================
X_train_scaled = joblib.load("models/X_train_scaled_v2.pkl")

# 🔥 CLEAN TRAIN DATA (CRITICAL FIX)
X_train_scaled = pd.DataFrame(X_train_scaled)
X_train_scaled = X_train_scaled.select_dtypes(include=[np.number]).to_numpy(dtype=float)

# ================================
# DATA LOAD
# ================================
df = pd.read_csv("data/engineered_customers.csv")

feature_cols = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

X = df[feature_cols].copy()

# ================================
# SCALE INPUT
# ================================
X_scaled = scaler.transform(X)

# ================================
# PREDICTION
# ================================
raw_preds = model.predict(X_scaled)

preds = raw_preds / 25.0
preds = np.clip(preds, 0, 1)

df["predicted_risk_score"] = preds

# ================================
# BAND
# ================================
df["predicted_band"] = pd.cut(
    df["predicted_risk_score"],
    bins=[0, 0.33, 0.66, 1],
    labels=["Low", "Medium", "High"],
    include_lowest=True
)

# ================================
# LIME EXPLAINER (FIXED)
# ================================
explainer = LimeTabularExplainer(
    training_data=X_train_scaled,
    feature_names=feature_cols,
    mode="regression",
    discretize_continuous=True
)

# ================================
# PREDICT FUNCTION (SAFE FIX)
# ================================
def predict_fn(x):
    x = np.asarray(x, dtype=float)
    raw = model.predict(x)
    scaled = raw / 25.0
    return np.clip(scaled, 0, 1)

# ================================
# BASE VALUE
# ================================
base_preds = predict_fn(X_train_scaled)
base_value = float(np.mean(base_preds))

# ================================
# LIME LOOP (SAFE VERSION)
# ================================
lime_results_all = []

for i in range(len(X_scaled)):
    exp = explainer.explain_instance(
        X_scaled[i],
        predict_fn,
        num_features=3
    )

    lime_result = exp.as_list()

    cleaned_explanation = []

    for item in lime_result:
        f, v = item

        # 🔥 SAFE FEATURE PARSING
        feature_name = str(f)
        feature_name = feature_name.split("=")[0].split("<")[0].split(">")[0].strip()

        cleaned_explanation.append({
            "feature": feature_name,
            "impact": float(v)
        })

    lime_results_all.append(cleaned_explanation)

# ================================
# JSON FORMAT
# ================================
df["lime_explanation"] = [
    json.dumps(row, ensure_ascii=False) for row in lime_results_all
]

df["base_value"] = base_value

# ================================
# MODEL INFO
# ================================
df["model_hash"] = "b02a4b90e9feb18d0ef31562d8c2fa4a46c7b5812790cc777c6110e8a87b7c65"
df["model_version"] = "v1_fixed_scale"

# ================================
# OUTPUT
# ================================
output_cols = [
    "predicted_risk_score",
    "predicted_band",
    "model_hash",
    "model_version",
    "base_value",
    "lime_explanation"
]

df[output_cols].to_csv("data/predictions.csv", index=False)

print("✅ predictions.csv başarıyla oluşturuldu (LIME FULL FIXED)")