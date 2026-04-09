from pydantic import BaseModel
from typing import List, Optional, Dict


# =====================================================
# LABEL COMPARISON (ENTERPRISE AUDIT MODEL)
# =====================================================

class LabelComparison(BaseModel):
    original_band: Optional[str] = None
    predicted_band: str
    agreement: bool


# =====================================================
# RISK COMPONENTS
# =====================================================

class RiskComponents(BaseModel):
    payment_discipline_score: float
    income_stability_index: float
    financial_resilience_score: float


# =====================================================
# FEATURE CONTRIBUTION MODEL (EXPLAINABILITY)
# =====================================================

class FeatureContribution(BaseModel):
    feature: str
    impact: float


# =====================================================
# MAIN RISK RESPONSE (✅ EXTENDED — BACKWARD SAFE)
# =====================================================

class RiskResponse(BaseModel):
    customer_id: int
    original_risk_score: float
    predicted_risk_score: float
    risk_band: str
    risk_color: str
    risk_label: str
    components: RiskComponents
    label_comparison: LabelComparison

    # ✅ EXISTING (bozulmadı)
    lime_explanation: Optional[List[Dict]] = None

    # ✅ YENİ EKLENEN (scale açıklaması)
    score_metadata: Optional[Dict[str, str]] = None


# =====================================================
# EXPLAIN RESPONSE (OPTIONAL SEPARATE ENDPOINT MODEL)
# =====================================================

class ExplainResponse(BaseModel):
    customer_id: int
    risk_score: float

    risk_segment: str
    risk_color: str
    risk_label: str

    # tüm feature etkileri
    feature_contributions: List[FeatureContribution]

    # en önemli risk faktörleri
    top_risk_factors: List[FeatureContribution]

    # insan okunabilir açıklama
    natural_language_explanation: str


# =====================================================
# ✅ BATCH SCORING INPUT
# =====================================================

class BatchRequest(BaseModel):
    customer_ids: List[int]


# =====================================================
# SINGLE BATCH RESULT
# =====================================================

class BatchResult(BaseModel):
    customer_id: int
    risk_score: float
    risk_segment: str
    risk_label: str
    risk_color: str


# =====================================================
# FINAL BATCH RESPONSE
# =====================================================

class BatchRiskResponse(BaseModel):
    results: List[BatchResult]
    total_processed: int