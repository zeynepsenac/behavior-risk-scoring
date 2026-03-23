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
    version="1.6.5"
)

# =====================================================
# MODEL
# =====================================================
model = joblib.load("models/risk_model.pkl")

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

# =====================================================
# BUFFER
# =====================================================
_prediction_buffer = np.zeros((1, FEATURE_COUNT), dtype=np.float32)
buffer_lock = Lock()

prediction_cache = {}
cache_lock = Lock()


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
# DB LOGGER
# =====================================================
def log_prediction(customer_id, values, score, segment, endpoint):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO prediction_history(
                customer_id,
                endpoint,
                features,
                predicted_score,
                risk_band,
                created_at
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            customer_id,
            endpoint,
            json.dumps(values),
            score,
            segment,
            datetime.utcnow()
        ))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print("Audit log failed:", e)


# =====================================================
# STARTUP
# =====================================================
@app.on_event("startup")
def startup_event():

    global df

    print("Loading customers from DB...")

    df = load_customers()

    if df is None or df.empty:
        print("⚠️ No customers loaded!")
        return

    print(f"✅ Loaded {len(df)} customers")

    initialize_explainer(df, FEATURES)

    try:
        _prediction_buffer[0, :] = df.iloc[0][FEATURES].values
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
            detail="Customer dataset not loaded"
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

    values = np.array(
        [float(row[f]) for f in FEATURES],
        dtype=np.float32
    )

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
            "payment_discipline_score": float(values[0]),
            "income_stability_index": float(values[1]),
            "financial_resilience_score": float(values[2]),
        },
        "timestamp": datetime.utcnow()
    }


# =====================================================
# EXPLAIN  ✅ FINAL FIX
# =====================================================
@app.get("/explain/{customer_id}", response_model=ExplainResponse)
def explain_customer(customer_id: int):

    ensure_data_loaded()

    customer = df[df["customer_id"] == customer_id]

    if customer.empty:
        raise HTTPException(404, "Customer not found")

    row = customer.iloc[0]

    values = np.array(
        [float(row[f]) for f in FEATURES],
        dtype=np.float32
    )

    score = fast_predict(values)
    segment = risk_segment(score)

    lime_exp = explain_instance(row[FEATURES], model)

    if hasattr(lime_exp, "as_list"):
        lime_exp = lime_exp.as_list()

    # ✅ SAFE LIME PARSER (CRASH FIX)
    contributions = []

    for item in lime_exp:

        if isinstance(item, tuple) and len(item) == 2:
            feature_text, impact = item

        elif isinstance(item, dict):
            feature_text = item.get("feature", "")
            impact = item.get("impact", 0)

        else:
            continue

        try:
            impact_value = float(impact)
        except (ValueError, TypeError):
            impact_value = 0.0

        contributions.append({
            "feature": str(feature_text),
            "impact": impact_value
        })

    # ✅ SCHEMA FIX (OBJECT LIST)
    top_risk_factors = contributions[:3]

    explanation_text = ", ".join(rule_engine(row))

    log_prediction(customer_id, values.tolist(), score, segment, "explain")

    return {
        "customer_id": customer_id,
        "risk_score": round(score, 2),
        "risk_segment": segment,
        "risk_label": segment,
        "risk_color": risk_color(segment),
        "feature_contributions": contributions,
        "top_risk_factors": top_risk_factors,
        "natural_language_explanation": explanation_text
    }