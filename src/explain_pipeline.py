"""
Explainability Module
---------------------

Hybrid Explainable AI layer for the
Behavior-Based Micro Risk Scoring System.

Combines:
- Feature contribution scoring
- LIME model explanations
- Rule-based reasoning
- Natural language interpretation
- Explanation confidence scoring
"""

from typing import Dict, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

# =====================================================
# IMPORTS
# =====================================================
import pandas as pd

from src.explain.lime_explainer import explain_instance
from src.rules import rule_engine


# =====================================================
# FEATURE LIST (GLOBAL — ERROR FIX)
# =====================================================
FEATURES = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]


# =====================================================
# FEATURE CONTRIBUTIONS (RULE WEIGHTS)
# =====================================================
def calculate_feature_contributions(
    row: Union[dict, "pd.Series"]
) -> Dict[str, float]:

    payment = float(row["payment_discipline_score"])
    income = float(row["income_stability_index"])
    resilience = float(row["financial_resilience_score"])

    contributions = {
        "payment_discipline_score": round(0.4 * payment, 2),
        "income_stability_index": round(0.3 * income, 2),
        "financial_resilience_score": round(0.3 * resilience, 2),
    }

    return contributions


# =====================================================
# RANK MOST IMPORTANT FACTORS
# =====================================================
def rank_risk_factors(
    contributions: Dict[str, float],
    top_k: int = 3
) -> List[Tuple[str, float]]:

    ranked = sorted(
        contributions.items(),
        key=lambda x: abs(float(x[1])),
        reverse=True
    )

    return [(str(name), float(value)) for name, value in ranked[:top_k]]


# =====================================================
# NATURAL LANGUAGE EXPLANATION
# =====================================================
def generate_explanation_text(
    top_factors: List[Tuple[str, float]]
) -> str:

    if not top_factors:
        return "Risk is influenced by multiple behavioral factors."

    main_factor = top_factors[0][0]

    explanations = {
        "payment_discipline_score":
            "Risk level is mainly driven by payment discipline behavior.",

        "income_stability_index":
            "Income stability has the strongest influence on the risk score.",

        "financial_resilience_score":
            "Financial resilience significantly impacts overall risk.",
    }

    return explanations.get(
        main_factor,
        "Risk is influenced by multiple behavioral factors."
    )


# =====================================================
# FORMAT LIME OUTPUT (FASTAPI SAFE)
# =====================================================
def format_lime_output(
    lime_list: List[Tuple[str, float]]
) -> List[Dict]:

    formatted = []

    for feature, impact in lime_list:
        formatted.append({
            "feature": str(feature),
            "impact": float(round(impact, 4))
        })

    return formatted


# =====================================================
# EXPLANATION CONFIDENCE SCORE
# =====================================================
def calculate_explanation_confidence(
    rule_factors: List[Tuple[str, float]],
    lime_factors: List[Dict],
    top_k: int = 3
) -> float:
    """
    Measures agreement between rule-based
    and LIME explanations.
    """

    rule_top = {name for name, _ in rule_factors[:top_k]}
    lime_top = {item["feature"] for item in lime_factors[:top_k]}

    if not rule_top:
        return 0.0

    overlap = rule_top.intersection(lime_top)

    confidence = len(overlap) / len(rule_top)

    return round(confidence, 2)


# =====================================================
# MAIN EXPLAINABILITY PIPELINE
# =====================================================
def build_explanation(
    row: Union[dict, "pd.Series"],
    model
) -> Dict:
    """
    MASTER EXPLAINABILITY PIPELINE
    """

    # -----------------------------------
    # SAFE ROW CONVERSION (API / DB SAFE)
    # -----------------------------------
    if not isinstance(row, dict):
        row = dict(row)

    row_series = pd.Series(row)

    # -----------------------------------
    # Feature Contributions
    # -----------------------------------
    contributions = calculate_feature_contributions(row_series)

    # -----------------------------------
    # Rank Factors
    # -----------------------------------
    ranked = rank_risk_factors(contributions)

    # -----------------------------------
    # Natural Language Explanation
    # -----------------------------------
    explanation_text = generate_explanation_text(ranked)

    # -----------------------------------
    # LIME Explanation
    # -----------------------------------
    feature_vector = row_series[FEATURES]

    lime_raw = explain_instance(
        feature_vector,
        model
    )

    lime_explanation = format_lime_output(lime_raw)

    # -----------------------------------
    # Rule Engine Explanation
    # -----------------------------------
    rules = rule_engine(row_series)

    # -----------------------------------
    # Explanation Confidence
    # -----------------------------------
    confidence_score = calculate_explanation_confidence(
        ranked,
        lime_explanation
    )

    # -----------------------------------
    # FINAL RESPONSE (API STANDARDIZED)
    # -----------------------------------
    return {
        "feature_contributions": contributions,
        "top_risk_factors": ranked,
        "natural_language": explanation_text,
        "lime_explanation": lime_explanation,
        "rule_based_explanations": rules,
        "confidence_score": confidence_score,
        "explanation_method":
            "Hybrid (Rule Engine + LIME + Feature Attribution)"
    }