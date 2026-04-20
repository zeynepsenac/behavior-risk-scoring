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
# RULE-BASED EXPLAINABILITY MODEL
# =====================================================

class RuleItem(BaseModel):
    rule: str
    impact: float


# =====================================================
# MODEL INFO
# =====================================================

class ModelInfo(BaseModel):
    model_version: str
    model_hash: str


# =====================================================
# MAIN RISK RESPONSE (🔥 FINAL CLEAN VERSION)
# =====================================================

class RiskResponse(BaseModel):
    customer_id: int

    # 🔹 mevcut alanlar (DEĞİŞMEDİ)
    original_risk_score: float
    predicted_risk_score: float
    risk_band: str
    risk_color: str
    risk_label: str

    components: RiskComponents
    label_comparison: LabelComparison

    # 🔥 LIME KALDIRILDI → YENİ ALAN
    explanations: Optional[List[FeatureContribution]] = None

    rule_based_score: Optional[float] = None
    rule_explanations: Optional[List[RuleItem]] = None

    model_info: Optional[ModelInfo] = None
    score_metadata: Optional[Dict[str, str]] = None

    # =====================================================
    # 🔥 EK ALANLAR (DEĞİŞMEDİ)
    # =====================================================

    ml_score: Optional[float] = None
    rule_score: Optional[float] = None
    final_score: Optional[float] = None
    base_value: Optional[float] = None


# =====================================================
# SIMPLE RESPONSE
# =====================================================

class SimpleRiskResponse(BaseModel):
    risk_score: float
    risk_band: str
    risk_label: str
    confidence: str


# =====================================================
# EXPLAIN RESPONSE
# =====================================================

class ExplainResponse(BaseModel):
    customer_id: int
    risk_score: float

    risk_segment: str
    risk_color: str
    risk_label: str

    feature_contributions: List[FeatureContribution]
    top_risk_factors: List[FeatureContribution]

    natural_language_explanation: str


# =====================================================
# BATCH INPUT
# =====================================================

class BatchRequest(BaseModel):
    customer_ids: List[int]


# =====================================================
# BATCH RESULT
# =====================================================

class BatchResult(BaseModel):
    customer_id: int

    risk_score: Optional[float] = None
    risk_segment: Optional[str] = None
    risk_label: Optional[str] = None
    risk_color: Optional[str] = None

    error: Optional[str] = None


# =====================================================
# FINAL BATCH RESPONSE
# =====================================================

class BatchRiskResponse(BaseModel):
    results: List[BatchResult]
    total_processed: int