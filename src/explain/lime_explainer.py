import numpy as np
import joblib
import pandas as pd

# ❌ LIME IMPORT KALDIRILDI (istersen tamamen silebilirsin)
# from lime.lime_tabular import LimeTabularExplainer

FEATURES = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

# -------------------------------------------------
# TRAIN DATA LOAD
# -------------------------------------------------
try:
    X_TRAIN_SCALED = joblib.load("models/X_train_scaled_v2.pkl")
except Exception as e:
    print("⚠ X_train_scaled yüklenemedi:", e)
    X_TRAIN_SCALED = None

# -------------------------------------------------
# SCALER LOAD
# -------------------------------------------------
try:
    scaler = joblib.load("models/scaler_v2.pkl")
except Exception as e:
    print("⚠ scaler yüklenemedi:", e)
    scaler = None


# -------------------------------------------------
# SAFE FLOAT
# -------------------------------------------------
def safe_float(v, default=0.0):
    try:
        if v is None:
            return default
        return float(v)
    except:
        return default


# -------------------------------------------------
# 🔥 LIME DISABLED (NO-OP FUNCTION)
# -------------------------------------------------
def explain_instance(feature_vector, model):
    """
    LIME explainability is disabled.
    This function intentionally returns empty output
    to keep system stable and avoid runtime errors.
    """

    # İstersen debug için log bırakabilirsin
    # print("ℹ explain_instance çağrıldı ama LIME devre dışı")

    return []