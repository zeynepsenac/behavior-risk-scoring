from fastapi import FastAPI, HTTPException
from datetime import datetime
import pandas as pd
import numpy as np
import joblib
import json

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from typing import List

from src.schemas import (
    RiskResponse,
    ExplainResponse,
    BatchCustomer,
    BatchRiskResponse
)

from src.explain.lime_explainer import (
    explain_instance,
    initialize_explainer
)

from src.rules import rule_engine
from src.database import load_customers, get_db_connection


# =====================================================
# FASTAPI
# =====================================================
app = FastAPI(
    title="Explainable AI Behavioral Risk Scoring API",
    version="2.0.0"
)

# =====================================================
# MODEL
# =====================================================
model = joblib.load("models/risk_model.pkl")

MODEL_VERSION = "1.0.0"
FEATURE_VERSION = "1.0.0"

# =====================================================
# THREAD POOL
# =====================================================
executor = ThreadPoolExecutor(max_workers=4)

# =====================================================
# GLOBAL DATA
# =====================================================
df = None

FEATURES = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

FEATURE_COUNT = len(FEATURES)

_prediction_buffer = np.zeros((1, FEATURE_COUNT), dtype=np.float32)
buffer_lock = Lock()

prediction_cache = {}
cache_lock = Lock()


# =====================================================
# FEATURE BUILDER
# =====================================================
def build_features(row, features):

    values = []

    for f in features:
        v = row.get(f, 0)

        if v is None or (isinstance(v, float) and np.isnan(v)):
            v = 0

        try:
            v = float(v)
        except Exception:
            v = 0.0

        values.append(v)

    return np.array(values, dtype=np.float32)


def cache_key(values):
    return tuple(round(float(v), 4) for v in values)


# =====================================================
# FAST PREDICT
# =====================================================
def fast_predict(values):

    key = cache_key(values)

    cached = prediction_cache.get(key)
    if cached is not None:
        return cached

    with buffer_lock:
        _prediction_buffer[0, :] = values
        prediction = float(model.predict(_prediction_buffer)[0])

    with cache_lock:
        prediction_cache[key] = prediction

    return prediction


# =====================================================
# AUDIT LOGGER
# =====================================================
def log_prediction(customer_id, values, score, segment, endpoint):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO prediction_history(
                customer_id,
                risk_score,
                risk_band,
                model_version,
                feature_version,
                endpoint,
                features,
                created_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            customer_id,
            float(score),
            segment,
            MODEL_VERSION,
            FEATURE_VERSION,
            endpoint,
            json.dumps(values),
            datetime.utcnow()
        ))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print("Audit log failed:", e)


# =====================================================
# 🔥 LOAD ENGINEERED FEATURES (CRITICAL FIX)
# =====================================================
def load_engineered_features():

    conn = get_db_connection()

    query = """
        SELECT
            customer_id,
            payment_discipline_score,
            income_stability_index,
            financial_resilience_score
        FROM engineered_features
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# =====================================================
# STARTUP
# =====================================================
@app.on_event("startup")
def startup_event():

    global df

    print("\nLoading engineered features from DB...")

    df = load_engineered_features()

    if df is None or df.empty:
        print("⚠️ No engineered features loaded!")
        return

    print(f"✅ Loaded {len(df)} customers")

    # ✅ LIME NOW USES CORRECT DATA
    initialize_explainer(df, FEATURES)

    # warmup prediction
    try:
        sample = build_features(df.iloc[0], FEATURES)
        _prediction_buffer[0, :] = sample
        model.predict(_prediction_buffer)
    except Exception:
        pass


# =====================================================
# HELPERS
# =====================================================
def ensure_data_loaded():
    if df is None or df.empty:
        raise HTTPException(
            status_code=500,
            detail="Dataset not loaded"
        )


def risk_segment(score: float):
    if score >= 75:
        return "Low Risk"
    elif score >= 50:
        return "Medium Risk"
    return "High Risk"


def risk_band_from_score(score: float):
    if score >= 70:
        return "Low"
    elif score >= 40:
        return "Medium"
    return "High"


def risk_color(label: str):
    return (
        "green" if label == "Low Risk"
        else "orange" if label == "Medium Risk"
        else "red"
    )


# =====================================================
# SINGLE SCORE
# =====================================================
@app.get("/risk-score/{customer_id}", response_model=RiskResponse)
def get_risk_score(customer_id: int):

    ensure_data_loaded()

    customer = df[df["customer_id"] == customer_id]

    if customer.empty:
        raise HTTPException(404, "Customer not found")

    row = customer.iloc[0]

    values = build_features(row, FEATURES)

    score = fast_predict(values)
    segment = risk_segment(score)
    band = risk_band_from_score(score)

    log_prediction(customer_id, values.tolist(), score, segment, "risk-score")

    return {
        "customer_id": customer_id,
        "original_risk_score": round(score, 2),
        "predicted_risk_score": round(score, 2),
        "risk_label": segment,
        "risk_color": risk_color(segment),
        "risk_band": band,
        "components": {
            FEATURES[i]: float(values[i])
            for i in range(len(FEATURES))
        },
        "timestamp": datetime.utcnow()
    }


# =====================================================
# EXPLAIN
# =====================================================
@app.get("/explain/{customer_id}", response_model=ExplainResponse)
def explain_customer(customer_id: int):

    ensure_data_loaded()

    customer = df[df["customer_id"] == customer_id]

    if customer.empty:
        raise HTTPException(404, "Customer not found")

    row = customer.iloc[0]

    values = build_features(row, FEATURES)

    score = fast_predict(values)
    segment = risk_segment(score)

    lime_exp = explain_instance(row[FEATURES], model)

    contributions = [
        {
            "feature": str(item["feature"]),
            "impact": float(item["impact"])
        }
        for item in lime_exp
    ]

    explanation_text = ", ".join(rule_engine(row))

    log_prediction(customer_id, values.tolist(), score, segment, "explain")

    return {
        "customer_id": customer_id,
        "risk_score": round(score, 2),
        "risk_segment": segment,
        "risk_label": segment,
        "risk_color": risk_color(segment),
        "feature_contributions": contributions,
        "top_risk_factors": contributions[:3],
        "natural_language_explanation": explanation_text
    }