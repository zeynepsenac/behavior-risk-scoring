from pydantic import BaseModel
from typing import Dict, List


# =====================================================
# EXISTING SCHEMAS (UNCHANGED)
# =====================================================

class RiskComponents(BaseModel):
    payment_discipline_score: float
    income_stability_index: float
    financial_resilience_score: float


class RiskResponse(BaseModel):
    customer_id: int
    original_risk_score: float
    predicted_risk_score: float
    risk_band: str
    risk_color: str
    risk_label: str
    components: RiskComponents


# =====================================================
# ✅ NEW — FEATURE CONTRIBUTION MODEL (FIX)
# =====================================================

class FeatureContribution(BaseModel):
    feature: str
    impact: float


# =====================================================
# ✅ FIXED EXPLAIN RESPONSE
# =====================================================

class ExplainResponse(BaseModel):
    customer_id: int
    risk_score: float
    risk_segment: str
    risk_color: str
    risk_label: str

    # LIME output → LIST OF OBJECTS
    feature_contributions: List[FeatureContribution]

    # top 3 factors
    top_risk_factors: List[FeatureContribution]

    natural_language_explanation: str


# =====================================================
# BATCH SCORING SCHEMAS (UNCHANGED)
# =====================================================

class BatchCustomer(BaseModel):
    payment_discipline_score: float
    income_stability_index: float
    financial_resilience_score: float


class BatchRiskResponse(BaseModel):
    scores: List[float]