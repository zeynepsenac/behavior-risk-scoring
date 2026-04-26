from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# =====================================================
# LABEL COMPARISON
# =====================================================

class LabelComparison(BaseModel):
    original_band: Optional[str] = None
    predicted_band: Optional[str] = None
    agreement: Optional[bool] = None


# =====================================================
# RISK COMPONENTS
# =====================================================

class RiskComponents(BaseModel):
    payment_discipline_score: Optional[float] = None
    income_stability_index: Optional[float] = None
    financial_resilience_score: Optional[float] = None


# =====================================================
# FEATURE CONTRIBUTION
# =====================================================

class FeatureContribution(BaseModel):
    feature: str
    impact: float


# =====================================================
# 🔥 FIX: FULL EXPLANATION MODEL (API İLE UYUMLU)
# =====================================================

class FeatureExplanation(BaseModel):
    feature: str
    value: Optional[float] = None
    impact: float
    text: Optional[str] = None


# =====================================================
# RULE ITEM
# =====================================================

class RuleItem(BaseModel):
    rule: str
    impact: float


# =====================================================
# MODEL INFO
# =====================================================

class ModelInfo(BaseModel):
    model_version: Optional[str] = None
    model_hash: Optional[str] = None


# =====================================================
# MAIN RESPONSE (FIXED)
# =====================================================

class RiskResponse(BaseModel):
    customer_id: int

    original_risk_score: Optional[float] = None
    predicted_risk_score: Optional[float] = None
    risk_band: Optional[str] = None
    risk_color: Optional[str] = None
    risk_label: Optional[str] = None

    components: Optional[RiskComponents] = None
    label_comparison: Optional[LabelComparison] = None

    # 🔥 FIX: mutable default kaldırıldı
    feature_contributions: Optional[List[FeatureContribution]] = Field(default_factory=list)

    feature_importance: Optional[Dict[str, float]] = Field(default_factory=dict)

    # 🔥 FIX: doğru model kullanıldı
    explanations: Optional[List[FeatureExplanation]] = Field(default_factory=list)

    rule_explanations: Optional[List[RuleItem]] = Field(default_factory=list)

    rule_based_score: Optional[float] = None

    model_info: Optional[ModelInfo] = None
    score_metadata: Optional[Dict[str, Any]] = None

    ml_score: Optional[float] = None
    rule_score: Optional[float] = None
    final_score: Optional[float] = None
    base_value: Optional[float] = None

    model_confidence: Optional[float] = None

    # 🔥 FIX: mutable default kaldırıldı
    warnings: Optional[List[str]] = Field(default_factory=list)


# =====================================================
# SIMPLE RESPONSE (UNCHANGED + SAFE)
# =====================================================

class SimpleRiskResponse(BaseModel):
    risk_score: float
    risk_band: str
    risk_label: str

    confidence: Optional[float] = None
    warning: Optional[str] = None


# =====================================================
# EXPLAIN RESPONSE
# =====================================================

class ExplainResponse(BaseModel):
    customer_id: int
    risk_score: float

    risk_segment: Optional[str] = None
    risk_color: Optional[str] = None
    risk_label: Optional[str] = None

    feature_contributions: List[FeatureContribution] = Field(default_factory=list)
    top_risk_factors: List[FeatureContribution] = Field(default_factory=list)

    natural_language_explanation: Optional[str] = None


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