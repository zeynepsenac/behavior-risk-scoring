# =====================================================
# IMPORTS
# =====================================================
from src.config.settings import DATABASE_TABLES
TABLE_NAME = DATABASE_TABLES["ENGINEERED"]
from fastapi import FastAPI, HTTPException
import json
from pathlib import Path
import numpy as np
import joblib
import hashlib
from typing import List
from datetime import datetime
from src.explain.lime_explainer import build_explanation
from src.database import get_db_connection, verify_schema
from src.schemas import (
    RiskResponse,
    RiskComponents,
    LabelComparison,
    BatchRequest,
    BatchRiskResponse,
    BatchResult
)
from src.schemas import SimpleRiskResponse
from src.rules import rule_engine
from src.explain_pipeline import calculate_rule_scorecard


from src.explain.lime_explainer import initialize_explainer
from src.database import load_customers
# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_METADATA_PATH = BASE_DIR / "models" / "metadata.json"
MODEL_PATH = BASE_DIR / "models" / "risk_model.pkl"
MODEL_METRICS_PATH = BASE_DIR / "models" / "model_metrics.json"
# =====================================================
# MODEL METADATA
# =====================================================
def load_model_metadata():
    if not MODEL_METADATA_PATH.exists():
        raise HTTPException(500, "Model metadata file not found")

    with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

MODEL_METADATA = load_model_metadata()

FEATURES = MODEL_METADATA["features"]

MODEL_VERSION = MODEL_METADATA.get(
    "model_version",
    f"v_unknown_{MODEL_METADATA.get('model_hash','nohash')[:8]}"
)

MODEL_HASH = MODEL_METADATA["model_hash"]
FEATURE_VERSION = MODEL_METADATA.get("feature_version", "v1")
DATASET_VERSION = MODEL_METADATA.get("dataset_version", "v1")

# =====================================================
# LOAD MODEL
# =====================================================
def load_model():
    if not MODEL_PATH.exists():
        print("⚠ fallback scoring active")
        return None

    print("✅ ML model loaded")
    return joblib.load(MODEL_PATH)

MODEL = load_model()




# -----------------------------------------------------
# EXPLAINABILITY (LIME)
# -----------------------------------------------------


# =====================================================
# FEATURE HASH
# =====================================================
def compute_feature_hash(features: dict):
    normalized = json.dumps(features, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()

# =====================================================
# NORMALIZER
# =====================================================
def normalize_ml_score(score: float):

    if score is None:
        return None

    MODEL_MAX_SCORE = 25.0
    normalized = float(score) / MODEL_MAX_SCORE
    normalized = max(0.0, min(1.0, normalized))

    return round(normalized, 4)

# =====================================================
# FASTAPI
# =====================================================

app = FastAPI(
    title="Explainable AI Behavioral Risk Scoring API",
    description="""
Production-style Machine Learning API for behavioral financial risk analysis.

This system provides an enterprise-oriented risk scoring service powered by
Explainable Artificial Intelligence principles.

Core Capabilities:
• Individual customer risk scoring
• Batch prediction processing
• Model version and dataset traceability
• Prediction audit history tracking
• Explainability-based decision insights
• System health monitoring

Architecture Goals:
• Reproducible ML inference
• Transparent risk evaluation
• Audit-ready prediction lifecycle
• Production-grade API design

Designed as a scalable and explainable machine learning service.
""",
    version="3.4.2",
    contact={
        "name": "AI Risk Analytics Team"
    },
    license_info={
        "name": "Academic Use License"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)
# =====================================================
# STARTUP CHECK
# =====================================================
@app.on_event("startup")
def startup_check():

    conn = get_db_connection()
    try:
        verify_schema(conn)
        print("✅ Database schema verified")
    finally:
        conn.close()
    # ==========================================
    # LIME INITIALIZATION (CRITICAL FIX)
    # ==========================================
    try:
        df = load_customers()
        initialize_explainer(
            df,
            FEATURES
        )
    except Exception as e:
        print("⚠️ LIME init failed:", e)
# =====================================================
# FEATURE FETCH
# =====================================================
def fetch_customer_features(customer_id: int):

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        query = f"""
            SELECT {",".join(FEATURES)}
            FROM engineered_features
            WHERE customer_id = %s
            LIMIT 1;
        """

        cur.execute(query, (customer_id,))
        row = cur.fetchone()

        if not row:
            raise HTTPException(404, "Customer not found")

        return dict(zip(FEATURES, row))

    finally:
        conn.close()

# =====================================================
# ORIGINAL RISK
# =====================================================
def fetch_original_risk(customer_id: int):

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT risk_score, risk_band
            FROM engineered_features
            WHERE customer_id = %s
            LIMIT 1
        """, (customer_id,))

        row = cur.fetchone()

        if not row:
            return None, None

        raw_score, raw_band = row

        # ⚠️ önemli: senin DB zaten 0-1 arasıysa normalize etme!
        original_score = float(raw_score)

        BAND_MAP = {
            "low": "Low",
            "medium": "Medium",
            "high": "High"
        }

        original_band = (
            BAND_MAP.get(str(raw_band).strip().lower())
            if raw_band else None
        )

        return original_score, original_band

    finally:
        conn.close()




# =====================================================
# ML PREDICTION
# =====================================================
def predict_with_model(features: dict):

    if MODEL is None:
        return None

    values = np.array([[
        float(features.get(f, 0) or 0)
        for f in FEATURES
    ]])

    raw_prediction = float(MODEL.predict(values)[0])

    return normalize_ml_score(raw_prediction)

# =====================================================
# RISK BAND
# =====================================================
def calculate_risk_band(score: float):

    if score < 0.33:
        return "Low", "green", "Low Risk"
    elif score < 0.66:
        return "Medium", "yellow", "Moderate Risk"
    else:
        return "High", "red", "High Risk"

# =====================================================
# CACHE CHECK
# =====================================================
def fetch_latest_prediction(customer_id: int, feature_hash: str):

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT risk_score,
                   model_version,
                   feature_version,
                   dataset_version,
                   feature_hash
            FROM prediction_history
            WHERE customer_id = %s
            ORDER BY prediction_time DESC
            LIMIT 1
        """, (customer_id,))

        row = cur.fetchone()

        if row is None:
            return None

        stored_score, mv, fv, dv, fh = row

        if (
            mv != MODEL_VERSION or
            fv != FEATURE_VERSION or
            dv != DATASET_VERSION or
            fh != feature_hash
        ):
            return None

        return float(stored_score)

    finally:
        conn.close()

# =====================================================
# SAVE PREDICTION
# =====================================================
def save_prediction(
    customer_id: int,
    score: float,
    original_band: str,
    predicted_band: str,
    feature_hash: str
):

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO prediction_history(
                customer_id,
                risk_score,
                original_band,
                predicted_band,
                model_version,
                feature_version,
                dataset_version,
                feature_hash,
                prediction_time,
                created_by
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW(),'api_inference')
        """, (
            customer_id,
            float(score),
            original_band,
            predicted_band,
            MODEL_VERSION,
            FEATURE_VERSION,
            DATASET_VERSION,
            feature_hash
        ))

        conn.commit()

    finally:
        conn.close()

# =====================================================
# ✅ CORE LOGIC (YENİ — ENDPOINTTEN AYRILDI)
# =====================================================


def calculate_risk(customer_id: int) -> RiskResponse:

    features = fetch_customer_features(customer_id)
    feature_hash = compute_feature_hash(features)

    rule_result = rule_engine(features)

    rules = rule_result["detailed_rules"]   # ✅ LIST
    rule_score = rule_result["score"]       # ✅ FLOAT

    #  DB’den hem score hem band al
    original_score, _ = fetch_original_risk(customer_id)

    # BAND'I YENİDEN HESAPLA
    original_band, _, _ = calculate_risk_band(original_score)

    if original_score is None:
        original_score = rule_score

    if original_band is None:
        original_band, _, _ = calculate_risk_band(original_score)

    # 🔥 prediction cache kontrol
    predicted_score = fetch_latest_prediction(
        customer_id,
        feature_hash
    )

    if predicted_score is None:

        ml_score = predict_with_model(features)

        predicted_score = (
         ml_score if ml_score is not None
         else rule_score
)
        predicted_band, _, _ = calculate_risk_band(predicted_score)

        save_prediction(
            customer_id,
            predicted_score,
            original_band,
            predicted_band,
            feature_hash
        )

    # ✅ final band (response için)
    band, color, label = calculate_risk_band(predicted_score)

    # ✅ comparison
    label_comparison = LabelComparison(
        original_band=original_band,
        predicted_band=band,
        agreement=(original_band.lower() == band.lower())
    )


    # -----------------------------------------------------
    # EXPLAINABILITY (LIME)
    # -----------------------------------------------------
    lime_explanation = None

    if MODEL is not None:
        try:
            row_features = {
                f: float(features.get(f, 0) or 0)
                for f in FEATURES
            }

            print("LIME INPUT:", row_features)

            lime_explanation = build_explanation(
                row_features,
                MODEL
            )

        except Exception as e:
            print("⚠ explainability failed:", e)

    # -----------------------------------------------------
    # COMPONENTS
    # -----------------------------------------------------
    components = RiskComponents(
        payment_discipline_score=float(features["payment_discipline_score"]),
        income_stability_index=float(features["income_stability_index"]),
        financial_resilience_score=float(features["financial_resilience_score"]),
    )

    # -----------------------------------------------------
    # RESPONSE (TEK RETURN)
    # -----------------------------------------------------
    return RiskResponse(
    customer_id=customer_id,
    predicted_risk_score=round(predicted_score, 3),
    original_risk_score=float(original_score),

    risk_band=band,
    risk_color=color,
    risk_label=label,

    components=components,
    label_comparison=label_comparison,

    lime_explanation=lime_explanation,

    rule_based_score=rule_score,
    rule_explanations=rules,

    # ✅ BURAYA EKLE
    score_metadata={
        "original_scale": "0-1 (historical dataset)",
        "predicted_scale": "0-1 (normalized ML output)"
    }
)
#===================================
# MAIN ENDPOINT (DEĞİŞMEDİ — SADECE FONKSİYON ÇAĞIRIYOR)
# =====================================================
@app.get(
    "/risk-score/{customer_id}",
    response_model=RiskResponse,
    tags=["Scoring"],
    summary="Calculate behavioral risk score",
    description="Returns explainable ML-based financial risk score for a single customer."
)
def risk_score(customer_id: int):
    return calculate_risk(customer_id)


@app.get("/risk-score-simple/{customer_id}", response_model=SimpleRiskResponse)
def simple_risk(customer_id: int):

    result = calculate_risk(customer_id)

    return SimpleRiskResponse(
        risk_score=result.predicted_risk_score,
        risk_band=result.risk_band,
        risk_label=result.risk_label,
        confidence="Model-based prediction"
    )

# =====================================================
# ✅ BATCH SCORING (YENİ ENDPOINT)
# =====================================================

@app.post(
    "/risk-score/batch",
    response_model=BatchRiskResponse,
    response_model_exclude_none=True,
    tags=["Scoring"],
    summary="Batch risk scoring",
    description="Calculates risk scores for multiple customers in a single request."
)
def batch_risk_score(request: BatchRequest):

    results = []

    for customer_id in request.customer_ids:
        try:
            r = calculate_risk(customer_id)

            results.append(
    BatchResult(
        customer_id=r.customer_id,
        risk_score=round(r.predicted_risk_score, 3),
        risk_segment=r.risk_band,
        risk_label=r.risk_label,
        risk_color=r.risk_color
    )
)

        # ✅ Partial failure handling (API bozulmaz)
        except Exception as e:
            results.append(
                BatchResult(
                    customer_id=customer_id,
                    error=str(e)
                )
            )

    return BatchRiskResponse(
        results=results,
        total_processed=len(results)
    )
# =====================================================
# HEALTH
# =====================================================

@app.get(
    "/health",
    tags=["System"],
    summary="API health check",
    description="Checks API status and model availability."
)
def health():
    return {
        "status": "ok",
        "model_loaded": MODEL is not None,
        "model_version": MODEL_VERSION
    }

# =====================================================
# MODEL INFO
# =====================================================
@app.get("/model-info", tags=["Model"])
def model_info():
    return {
        "model_version": MODEL_VERSION,
        "model_hash": MODEL_HASH,
        "feature_version": FEATURE_VERSION,
        "dataset_version": DATASET_VERSION,
        "features": FEATURES
    }



# =====================================================
# HISTORY
# =====================================================
@app.get(
    "/history/{customer_id}",
    tags=["Audit"],
    summary="Prediction audit history",
    description="Returns historical predictions for auditability and model traceability."
)
def get_prediction_history(customer_id: int):

    conn = get_db_connection()

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                customer_id,
                risk_score,
                original_band,
                predicted_band,
                model_version,
                feature_version,
                dataset_version,
                prediction_time,
                created_by
            FROM prediction_history
            WHERE customer_id = %s
            ORDER BY prediction_time DESC
            LIMIT 50
        """, (customer_id,))

        rows = cur.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No prediction history found"
            )

        history = []

        for r in rows:
            history.append({
                "customer_id": r[0],
                "predicted_risk_score": float(r[1]),
                "original_band": r[2],
                "predicted_band": r[3],
                "model_version": r[4],
                "feature_version": r[5],
                "dataset_version": r[6],
                "prediction_time": r[7],
                "created_by": r[8]
            })

        return {
            "customer_id": customer_id,
            "total_records": len(history),
            "history": history
        }

    finally:
        conn.close()



# =====================================================
# MODEL METRICS
# =====================================================
@app.get(
    "/model-metrics",
    tags=["Model"],
    summary="Model performance metrics",
    description="Returns evaluation metrics collected during model training."
)
def get_model_metrics():

    try:
        if not MODEL_METRICS_PATH.exists():
            raise HTTPException(
                status_code=404,
                detail="Model metrics file not found"
            )

        with open(MODEL_METRICS_PATH, "r", encoding="utf-8") as f:
            metrics = json.load(f)

        return {
            "model_version": MODEL_VERSION,
            "model_hash": MODEL_HASH,
            "metrics": metrics
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load metrics: {str(e)}"
        )
    

from psycopg2.extras import RealDictCursor


# =====================================================
# EXPLAINABILITY
# =====================================================


@app.get(
    "/explain/{customer_id}",
    tags=["Explainability"],
    summary="Explain prediction factors",
    description="Provides rule-based explanation of factors influencing risk prediction."
)
def explain_prediction(customer_id: int):

    conn = get_db_connection()

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT *
            FROM synthetic_customers
            WHERE customer_id = %s
        """, (customer_id,))

        row = cur.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        positives = []
        negatives = []

        if row["spending_ratio"] > 0.8:
            positives.append("high_spending_ratio")

        if row["bill_payment_delay_avg"] > 3:
            positives.append("payment_delay")

        if row["savings_rate"] > 0.2:
            negatives.append("high_savings_rate")

        if row["employment_duration_months"] > 60:
            negatives.append("long_employment_duration")

        return {
            "customer_id": customer_id,
            "prediction": row["risk_band"],
            "top_positive_factors": positives,
            "top_negative_factors": negatives,
            "explanation_summary":
                "Risk mainly influenced by behavioral financial patterns."
        }

    finally:
        conn.close()