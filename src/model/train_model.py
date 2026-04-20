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

# 🔥 FIX 1: TRAIN DATA PATH FIX
X_train_scaled = joblib.load("models/X_train_scaled_v2.pkl")

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
# 🔥 LIME FIXED
# ================================

# FIX 2: CLEAN TRAIN DATA
X_train_scaled = pd.DataFrame(X_train_scaled)
X_train_scaled = X_train_scaled.select_dtypes(include=[np.number]).to_numpy(dtype=float)

explainer = LimeTabularExplainer(
    training_data=X_train_scaled,
    feature_names=feature_cols,
    mode="regression"
)

# FIX 3: SAFE PREDICT FUNCTION
def predict_fn(x):
    x = np.asarray(x, dtype=float)
    preds = model.predict(x)
    preds = preds / 25.0
    return np.clip(preds, 0, 1)

# ================================
# 🔥 LIME LOOP (DOĞRU HALİ)
# ================================
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

            # 🔥 string gelirse skip (impact hatasını bitirir)
            if isinstance(v, str):
                continue

            v = float(v)

            feature_name = str(f)

            matched = False
            for col in feature_cols:
                if col in feature_name:
                    feature_name = col
                    matched = True
                    break

            if matched:
                cleaned.append({
                    "feature": feature_name,
                    "impact": v
                })

        except Exception as e:
            print("⚠ LIME row skip:", e)
            continue

    lime_results_all.append(cleaned)

# ================================
# JSON OUTPUT
# ================================
df["lime_explanation"] = [
    json.dumps(x, ensure_ascii=False) for x in lime_results_all
]

# ================================
# BASE VALUE
# ================================
base_preds = model.predict(X_train_scaled)
base_preds = base_preds / 25.0
base_preds = np.clip(base_preds, 0, 1)

df["base_value"] = float(np.mean(base_preds))

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

print("✅ predictions.csv başarıyla oluşturuldu (FULL LIME FIX + SCALE SAFE)")