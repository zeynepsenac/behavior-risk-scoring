# =====================================================
# IMPORTS
# =====================================================
from fastapi.middleware.cors import CORSMiddleware
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
from src.explain_pipeline import build_explanation
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
from src.database import load_customers

# =====================================================
# PATHS
# =====================================================
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_METADATA_PATH = BASE_DIR / "models" / "metadata.json"
MODEL_PATH = BASE_DIR / "models" / "risk_model_v2.pkl"   # ✅ TEK MODEL PATH
MODEL_METRICS_PATH = BASE_DIR / "models" / "model_metrics_v2.json"
# =====================================================
# V2 MODEL CONFIG (SAFE - YENİ)
# =====================================================
FEATURES_V2 = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

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
    print("MODEL PATH:", MODEL_PATH)          # ✅ debug
    print("MODEL VERSION:", MODEL_VERSION)    # ✅ debug

    if not MODEL_PATH.exists():
        print("⚠ fallback scoring active")
        return None

    print("✅ ML model loaded")
    return joblib.load(MODEL_PATH)

MODEL = load_model()

print("MODEL:", MODEL)

# -----------------------------------------------------
# EXPLAINABILITY (LIME)
# -----------------------------------------------------
# -----------------------------------------------------
# SIMPLE EXPLAINABILITY (FALLBACK)
# -----------------------------------------------------
def generate_simple_explanation(features):
    explanations = []

    if features.get("income_stability_index", 0) > 70:
        explanations.append({
            "feature": "income_stability_index",
            "impact": -0.07
        })

    if features.get("payment_discipline_score", 0) > 70:
        explanations.append({
            "feature": "payment_discipline_score",
            "impact": -0.05
        })

    if features.get("financial_resilience_score", 0) < 20:
        explanations.append({
            "feature": "financial_resilience_score",
            "impact": 0.06
        })

    # 🔥 SMART FALLBACK (DAHA MANTIKLI)
    if not explanations:
        explanations.append({
            "feature": "general_behavior",
            "impact": 0.01
        })

    return explanations
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

    return round(float(score), 4)

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için serbest
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
# V2 FEATURE FETCH (YENİ)
# =====================================================
def fetch_customer_features_v2(customer_id: int):

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                payment_discipline_score,
                income_stability_index,
                financial_resilience_score
            FROM engineered_features
            WHERE customer_id = %s
            LIMIT 1
        """, (customer_id,))

        row = cur.fetchone()

        if not row:
            return None

        return dict(zip(FEATURES_V2, row))

    finally:
        conn.close()


# =====================================================
# V2 MODEL LOAD
# =====================================================
def load_model_v2():
    if not MODEL_PATH.exists():
        raise HTTPException(500, "V2 model not found")

    return joblib.load(MODEL_PATH)
# =====================================================
# ORIGINAL RISK
# =====================================================
def fetch_original_risk(customer_id: int):

    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # 🔥 SADECE SCORE AL (band ignore)
        cur.execute("""
            SELECT risk_score
            FROM engineered_features
            WHERE customer_id = %s
            LIMIT 1
        """, (customer_id,))

        row = cur.fetchone()

        if not row:
            return None, None

        # 🔥 artık tek değer var
        raw_score = row[0]

        # ⚠️ DB zaten 0-1 scale ise normalize etme
        original_score = float(raw_score)

        # ❌ band DB'den alınmıyor
        original_band = None

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
        return {
            "band": "Low",
            "color": "#16a34a",
            "label": "Düşük Risk"
        }

    elif score < 0.66:
        return {
            "band": "Medium",
            "color": "#f59e0b",
            "label": "Orta Risk"
        }

    else:
        return {
            "band": "High",
            "color": "#dc2626",
            "label": "Yüksek Risk"
        }
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

def calculate_risk(customer_id: int, explain: bool = True) -> RiskResponse:

    import numpy as np
    import joblib

    try:
        X_TRAIN_SCALED = joblib.load("models/X_train_scaled_v2.pkl")
    except Exception as e:
        print("⚠ X_train_scaled yüklenemedi:", e)
        X_TRAIN_SCALED = None

    # =====================================================
    # FEATURES
    # =====================================================
    try:
        features = fetch_customer_features(customer_id)
        if not features:
            raise ValueError("Empty features")
    except Exception as e:
        print("⚠ müşteri bulunamadı:", e)
        raise ValueError("Customer not found")

    feature_hash = compute_feature_hash(features)

    input_vector = np.array([[float(features.get(f, 0) or 0) for f in FEATURES]])

    # =====================================================
    # NORMALIZATION
    # =====================================================
    def normalize_100_to_1(v):
        try:
            return max(0.0, min(1.0, v / 100))
        except:
            return 0.0

    payment_raw = float(features.get("payment_discipline_score", 0) or 0)
    income_raw = float(features.get("income_stability_index", 0) or 0)
    resilience_raw = float(features.get("financial_resilience_score", 0) or 0)

    payment_norm = normalize_100_to_1(payment_raw)
    income_norm = normalize_100_to_1(income_raw)
    resilience_norm = normalize_100_to_1(resilience_raw)

    # =====================================================
    # RULE ENGINE
    # =====================================================
    try:
        rule_result = rule_engine(features)
        rules = rule_result.get("detailed_rules", [])
        rule_score = float(rule_result.get("score", 0.0))

        if rule_score > 1:
            rule_score = rule_score / 100.0

        rule_score = max(0.0, min(1.0, rule_score))

    except Exception as e:
        print("⚠ rule engine failed:", e)
        rules = []
        rule_score = 0.0

    # =====================================================
    # ORIGINAL SCORE
    # =====================================================
    try:
        original_score, _ = fetch_original_risk(customer_id)
    except Exception:
        original_score = None

    if original_score is None:
        original_score = rule_score

    original_band = calculate_risk_band(original_score)["band"]

    # =====================================================
    # ML PREDICTION
    # =====================================================
    predicted_score = fetch_latest_prediction(customer_id, feature_hash)

    if predicted_score is None:

        try:
            if hasattr(MODEL, "predict_proba"):
                ml_score = MODEL.predict_proba(input_vector)[0][1]
            else:
                ml_score = MODEL.predict(input_vector)[0]

            ml_score = float(ml_score)

            if ml_score > 1:
                ml_score = ml_score / 100.0

            ml_score = max(0.0, min(1.0, ml_score))

        except Exception as e:
            print("⚠ ML prediction failed:", e)
            raise ValueError("Model prediction failed")

        predicted_score = ml_score
        predicted_band = calculate_risk_band(predicted_score)["band"]

        try:
            save_prediction(
                customer_id,
                float(predicted_score),
                original_band,
                predicted_band,
                feature_hash
            )
        except Exception as e:
            print("⚠ save_prediction başarısız:", e)

    else:
        ml_score = float(predicted_score)
        ml_score = max(0.0, min(1.0, ml_score))
        predicted_score = ml_score

        predicted_band = calculate_risk_band(predicted_score)["band"]

    # =====================================================
    # FINAL SCORE
    # =====================================================
    final_score = (0.7 * ml_score) + (0.3 * rule_score)
    final_score = max(0.0, min(1.0, final_score))

    risk_info = calculate_risk_band(final_score)

    band = risk_info["band"]
    color = risk_info["color"]
    label = risk_info["label"]

    # =====================================================
    # LABEL COMPARISON
    # =====================================================
    label_comparison = LabelComparison(
        original_band=original_band,
        predicted_band=band,
        agreement=(original_band.lower() == band.lower())
    )

    # =====================================================
    # BASE VALUE
    # =====================================================
    try:
        if X_TRAIN_SCALED is not None:
            if hasattr(MODEL, "predict_proba"):
                base_value = float(np.mean(MODEL.predict_proba(X_TRAIN_SCALED)[:, 1]))
            else:
                base_value = float(np.mean(MODEL.predict(X_TRAIN_SCALED)))
        else:
            base_value = float(ml_score) * 0.8

        base_value = max(0.0, min(1.0, base_value))

    except Exception as e:
        print("⚠ base_value hesaplanamadı:", e)
        base_value = float(ml_score)

    # =====================================================
    # COMPONENTS
    # =====================================================
    components = RiskComponents(
        payment_discipline_score=round(payment_norm, 3),
        income_stability_index=round(income_norm, 3),
        financial_resilience_score=round(resilience_norm, 3),
    )

    model_info = {
        "model_version": MODEL_VERSION,
        "model_hash": MODEL_HASH
    }

    # =====================================================
    # FINAL RESPONSE (🔥 FIX HERE)
    # =====================================================

    response_data = {
        "customer_id": customer_id,

        "ml_score": float(ml_score),
        "rule_score": float(rule_score),
        "final_score": float(final_score),
        "base_value": float(base_value),

        "predicted_risk_score": float(predicted_score),
        "original_risk_score": float(original_score),

        "risk_band": band,
        "risk_color": color,
        "risk_label": label,

        "components": components,
        "label_comparison": label_comparison,

        "explanations": [],
        "rule_explanations": rules,
        "rule_based_score": float(rule_score),

        "feature_contributions": {},
        "feature_importance": {},

        "model_info": model_info,

        "model_confidence": float(ml_score),
        "explanation": None,

        "score_metadata": {
            "scale": "final_score_based_band_only"
        }
    }

    # 🚨 CRITICAL FIX: duplicate risk_band bug prevention
    return RiskResponse(**response_data)
# =====================================================
# MAIN ENDPOINT
# =====================================================
# =====================================================
# MAIN ENDPOINT
# =====================================================
from fastapi import Query

@app.get(
    "/risk-score/{customer_id}",
    response_model=RiskResponse,
    tags=["Scoring"],
    summary="Calculate behavioral risk score",
    description="Returns explainable ML-based financial risk score for a single customer."
)
def risk_score(customer_id: int, explain: bool = Query(True)):

    try:
        return calculate_risk(customer_id, explain)

    except Exception as e:
        print("🔥 GLOBAL ERROR:", e)

        # 🔥 FULL FALLBACK (response_model uyumlu!)
        return RiskResponse(
            customer_id=customer_id,

            ml_score=0.0,
            rule_score=0.0,
            final_score=0.0,
            base_value=0.0,

            predicted_risk_score=0.0,
            original_risk_score=0.0,

            risk_band="Low",
            risk_color="#16a34a",
            risk_label="Düşük Risk",

            components=RiskComponents(
                payment_discipline_score=0.0,
                income_stability_index=0.0,
                financial_resilience_score=0.0
            ),

            label_comparison=LabelComparison(
                original_band="Low",
                predicted_band="Low",
                agreement=True
            ),

            explanations=[],
            rule_explanations=[],
            rule_based_score=0.0,

            feature_contributions={},
            feature_importance={},

            model_info={
                "model_version": "fallback",
                "model_hash": "none"
            },

            model_confidence=0.0,
            explanation="Fallback response (customer not found)",

            score_metadata={
                "status": "fallback"
            }
        )


# =====================================================
# SIMPLE ENDPOINT (🔥 BURASI DA EKLENDİ)
# =====================================================
@app.get("/risk-score-simple/{customer_id}", response_model=SimpleRiskResponse)
def simple_risk(customer_id: int):

    try:
        result = calculate_risk(customer_id, explain=False)

        return SimpleRiskResponse(
            risk_score=result.final_score,
            risk_band=result.risk_band,
            risk_label=result.risk_label,
            confidence="Model-based prediction"
        )

    except Exception as e:
        print("🔥 SIMPLE ENDPOINT ERROR:", e)

        # 🔥 SIMPLE FALLBACK
        return SimpleRiskResponse(
            risk_score=0.0,
            risk_band="Low",
            risk_label="Düşük Risk",
            confidence="Fallback response"
        )
# =====================================================
# BATCH SCORING
# =====================================================
# =====================================================
# HELPERS (EKLENDİ - MINIMAL FIX)
# =====================================================

def normalize_rule_score(rule_score: float) -> float:
    """
    Rule engine genelde 0-1 üstü şişebilir.
    Burada güvenli şekilde 0-1 aralığına çekiyoruz.
    """
    return max(0.0, min(1.0, rule_score))


def clamp(value: float, min_v=0.0, max_v=1.0) -> float:
    return max(min_v, min(max_v, value))


# =====================================================
# BATCH SCORING
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
                    risk_score=r.predicted_risk_score,  # ✅ FIX
                    risk_segment=r.risk_band,
                    risk_label=r.risk_label,
                    risk_color=r.risk_color
                )
            )

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
            # 🔥 SAFE SCORE
            try:
                score = float(r[1])
            except:
                score = 0.0

            model_version = r[4] or ""

            # =====================================================
            # ✅ FIX → TEK DOĞRU BAND HESABI
            # =====================================================
            recalculated_band = calculate_risk_band(score).get("band", "Unknown")

            history.append({
                "customer_id": r[0],
                "predicted_risk_score": score,
                "original_band": r[2],

                # ✅ ARTIK HER ZAMAN DOĞRU SCALE
                "predicted_band": recalculated_band,

                "model_version": model_version,
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


# =====================================================
# V2 ENDPOINT (FIXED - STABLE)
# =====================================================
@app.get("/risk-score-v2/{customer_id}", tags=["Scoring V2"])
def risk_score_v2(customer_id: int):

    try:
        features = fetch_customer_features_v2(customer_id)

        if not features:
            raise HTTPException(
                status_code=404,
                detail="Customer features not found"
            )

        model_v2 = load_model_v2()

        if model_v2 is None:
            raise HTTPException(
                status_code=501,
                detail="V2 model not available (under development)"
            )

        missing = [f for f in FEATURES_V2 if f not in features]

        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Missing features: {missing}"
            )

        values = np.array([[float(features[f]) for f in FEATURES_V2]])

        raw_score = float(model_v2.predict(values)[0])
        score = clamp(normalize_ml_score(raw_score))

        risk_info = calculate_risk_band(score)

        return {
            "customer_id": customer_id,
            "v2_score": round(score, 3),

            "risk_band": risk_info["band"],
            "risk_color": risk_info["color"],
            "risk_label": risk_info["label"]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"V2 scoring failed: {str(e)}"
        )


# =====================================================
# HYBRID ENDPOINT (🔥 FIXED CORE ISSUE)
# =====================================================
@app.get("/risk-score-hybrid/{customer_id}", tags=["Scoring Hybrid"])
def hybrid_score(customer_id: int):

    features = fetch_customer_features(customer_id)

    ml_score = predict_with_model(features)

    try:
        rule_result = rule_engine(features)
        rule_score = normalize_rule_score(
            float(rule_result.get("score", 0.0))
        )
    except:
        rule_score = 0.0

    # ==============================
    # 🔥 FIXED FUSION STRATEGY
    # ==============================
    if ml_score is None:
        final_score = rule_score
    else:
        ml_score = clamp(float(ml_score))

        final_score = (
            0.7 * ml_score +
            0.3 * rule_score
        )

    final_score = clamp(final_score)

    risk_info = calculate_risk_band(final_score)

    return {
        "customer_id": customer_id,
        "hybrid_score": round(final_score, 3),

        "risk_band": risk_info["band"],
        "risk_color": risk_info["color"],
        "risk_label": risk_info["label"],

        "ml_score": ml_score,
        "rule_score": rule_score
    }


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

        # ✅ 🔥 EN KRİTİK SATIR
        result = calculate_risk(customer_id)

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

            # ✅ ARTIK MODEL İLE SENKRON
            "prediction": result.risk_band,

            # 🔥 bonus (istersen ekle)
            "prediction_score": result.predicted_risk_score,

            "top_positive_factors": positives,
            "top_negative_factors": negatives,

            "explanation_summary":
                "Risk mainly influenced by behavioral financial patterns."
        }

    finally:
        conn.close()