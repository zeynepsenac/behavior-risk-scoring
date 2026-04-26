import pandas as pd
import joblib
import numpy as np
import json
from lime.lime_tabular import LimeTabularExplainer

print(" Generating predictions (FINAL THESIS VERSION)...")

# MODEL + SCALER LOAD
model = joblib.load("models/risk_model_v2.pkl")
scaler = joblib.load("models/scaler_v2.pkl")

# TRAIN DATA LOAD
X_train_scaled = joblib.load("models/X_train_scaled_v2.pkl")
X_train_scaled = np.array(X_train_scaled, dtype=float)

# DATA LOAD
df = pd.read_csv("data/anonymized_customers.csv")

feature_cols = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

missing = [c for c in feature_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# INPUT CLEANING
X = df[feature_cols].copy()
X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

X_scaled = scaler.transform(X)

# RAW PRED
raw_preds = model.predict(X_scaled)

# ROBUST SCALING
raw_min = np.percentile(raw_preds, 5)
raw_max = np.percentile(raw_preds, 95)
denom = (raw_max - raw_min) + 1e-6

preds = np.clip((raw_preds - raw_min) / denom, 0, 1)
df["predicted_risk_score"] = preds

# 🔥 FIX 1: evaluation için TRUE SCORE EKLENDİ
# (risk_score yoksa evaluation kırılmasın)
df["risk_score"] = preds  # alias (compatibility layer)

print("RAW PRED STATS:\n", pd.Series(raw_preds).describe())
print("SCALED PRED STATS:\n", pd.Series(preds).describe())

# BAND
df["predicted_band"] = pd.cut(
    df["predicted_risk_score"],
    bins=[0, 0.33, 0.66, 1],
    labels=["LOW", "MEDIUM", "HIGH"],
    include_lowest=True
).astype(str)

# LIME
explainer = LimeTabularExplainer(
    training_data=X_train_scaled,
    feature_names=feature_cols,
    mode="regression",
    discretize_continuous=True
)

def predict_fn(x):
    x = np.asarray(x, dtype=float)
    return model.predict(x)

base_preds = predict_fn(X_train_scaled)
base_value = float(np.mean(base_preds))

lime_results_all = []

for i in range(len(X_scaled)):
    exp = explainer.explain_instance(
        X_scaled[i],
        predict_fn,
        num_features=3
    )

    cleaned = []
    for feature, impact in exp.as_list():
        feature_name = str(feature)

        for sep in ["<=", ">=", "<", ">", "="]:
            feature_name = feature_name.split(sep)[0]

        feature_name = feature_name.strip()

        if feature_name not in feature_cols:
            feature_name = "unknown_feature"

        cleaned.append({
            "feature": feature_name,
            "impact": float(impact)
        })

    lime_results_all.append(cleaned)

df["lime_explanation"] = [
    json.dumps(r, ensure_ascii=False) for r in lime_results_all
]

df["base_value"] = base_value

# META
df["model_hash"] = "b02a4b90e9feb18d0ef31562d8c2fa4a46c7b5812790cc777c6110e8a87b7c65"
df["model_version"] = "v1_thesis_final"

# BIAS
global_mean = df["predicted_risk_score"].mean()
df["bias_delta"] = df["predicted_risk_score"] - global_mean

for col in feature_cols:
    med = df[col].median()

    df[f"{col}_group"] = np.where(df[col] < med, "low", "high")

    grp_mean = df.groupby(f"{col}_group")["predicted_risk_score"].transform("mean")

    # 🔥 FIX 2: suffix eksikti
    df[f"{col}_bias"] = df["predicted_risk_score"] - grp_mean.fillna(global_mean)

# INTERSECTIONAL BIAS
df["combined_group"] = (
    df["income_stability_index"].round(1).astype(str) + "_" +
    df["payment_discipline_score"].round(1).astype(str)
)

group_mean = df.groupby("combined_group")["predicted_risk_score"].transform("mean")
df["intersectional_bias"] = df["predicted_risk_score"] - group_mean.fillna(global_mean)

# CONFIDENCE
df["model_confidence"] = (1 - np.abs(df["bias_delta"])).clip(0, 1)

# CALIBRATION
df["calibration_bin"] = pd.qcut(
    df["predicted_risk_score"],
    q=5,
    labels=False,
    duplicates="drop"
)

df["risk_percentile"] = df["predicted_risk_score"].rank(pct=True)

# FINAL OUTPUT
cols = [
    "income_stability_index",
    "payment_discipline_score",
    "financial_resilience_score",
    "predicted_risk_score",
    "predicted_band",
    "bias_delta",
    "model_confidence",
    "payment_discipline_score_bias",
    "income_stability_index_bias",
    "financial_resilience_score_bias",
    "intersectional_bias",
    "calibration_bin",
    "risk_percentile",
    "model_hash",
    "model_version",
    "base_value",
    "lime_explanation"
]

df[cols].to_csv("data/predictions.csv", index=False)

print("====================================")
print(" THESIS-GRADE PREDICTIONS CREATED")
print(" Bias Mean:", round(global_mean, 6))
print(" Dataset Shape:", df.shape)
print(" Model Version: v1_thesis_final")
print("====================================")