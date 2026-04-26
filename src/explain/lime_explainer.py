import numpy as np
import joblib
import pandas as pd


# =========================
# FEATURES (TEK KAYNAK)
# =========================
FEATURES = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]


# =========================
# TRAIN DATA LOAD (SAFE)
# =========================
try:
    X_TRAIN_SCALED = joblib.load("models/X_train_scaled_v2.pkl")
except Exception as e:
    print("⚠️ X_train_scaled yüklenemedi:", e)
    X_TRAIN_SCALED = None


# =========================
# SCALER LOAD (SAFE)
# =========================
try:
    scaler = joblib.load("models/scaler_v2.pkl")
except Exception as e:
    print("⚠️ scaler yüklenemedi:", e)
    scaler = None


# =========================
# SAFE FLOAT (IMPROVED)
# =========================
def safe_float(v, default=0.0):
    try:
        if v is None:
            return default

        if isinstance(v, str):
            v = v.strip()
            if v == "":
                return default

        val = float(v)

        # NaN / inf koruması
        if not np.isfinite(val):
            return default

        return val

    except Exception:
        return default


# =========================
# FEATURE VECTOR BUILDER
# (UI / API mismatch fix için)
# =========================
def build_feature_vector(data: dict):
    """
    Eksik feature olsa bile sistemi kırmaz
    """
    return np.array([
        safe_float(data.get("payment_discipline_score")),
        safe_float(data.get("income_stability_index")),
        safe_float(data.get("financial_resilience_score")),
    ]).reshape(1, -1)


# =========================
# LIME DISABLED (SAFE NO-OP)
# =========================
def explain_instance(feature_vector, model):
    """
    LIME disabled but SAFE structured output
    UI bozulmasın diye boş değil, kontrollü çıktı döner
    """

    return {
        "status": "disabled",
        "explanations": [],
        "note": "LIME temporarily disabled for stability"
    }