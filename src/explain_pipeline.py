"""
Explainability Module
---------------------
Hybrid Explainable AI layer for the
Behavior-Based Micro Risk Scoring System.
"""

from typing import Dict, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

import pandas as pd
import numpy as np

from src.explain.lime_explainer import explain_instance
from src.rules import rule_engine


# FEATURE LIST

FEATURES = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]


# SAFE FLOAT

def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except:
        return default


# FEATURE CONTRIBUTIONS (FIX: scaling + consistency)

def calculate_feature_contributions(row: Union[dict, "pd.Series"]) -> Dict[str, float]:

    payment = safe_float(row.get("payment_discipline_score")) / 100
    income = safe_float(row.get("income_stability_index")) / 100
    resilience = safe_float(row.get("financial_resilience_score")) / 100

    # FIX: weights now consistent with risk model (0.4 / 0.3 / 0.3)
    return {
        "payment_discipline_score": round(payment * 0.4, 4),
        "income_stability_index": round(income * 0.3, 4),
        "financial_resilience_score": round(resilience * 0.3, 4),
    }


# RANK

def rank_risk_factors(contributions: Dict[str, float], top_k: int = 3):

    ranked = sorted(
        contributions.items(),
        key=lambda x: abs(safe_float(x[1])),
        reverse=True
    )

    return [(str(name), float(value)) for name, value in ranked[:top_k]]


# TEXT EXPLANATION (FIX: match risk logic better)

def generate_explanation_text(top_factors):

    if not top_factors:
        return "Risk is influenced by multiple behavioral factors."

    main_factor = top_factors[0][0]

    explanations = {
        "payment_discipline_score": "Payment behavior is the dominant risk driver.",
        "income_stability_index": "Income stability strongly influences risk level.",
        "financial_resilience_score": "Financial resilience is a key risk determinant."
    }

    return explanations.get(
        main_factor,
        "Risk is influenced by multiple behavioral factors."
    )


# FIX: LIME PARSER (CRITICAL BUG FIX)

def format_lime_output(lime_list):

    formatted = []

    for item in lime_list:

        try:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                feature, impact = item

            elif isinstance(item, dict):
                # FIX: correct mapping
                feature = item.get("feature", "")
                impact = item.get("impact", 0)

            elif isinstance(item, str):
                feature = item
                impact = 0

            else:
                continue

            impact = safe_float(impact)

            # FIX: DO NOT BREAK FEATURE NAME
            formatted.append({
                "feature": str(feature),   # ❌ removed .split(" ")[0]
                "impact": round(impact, 4)
            })

        except:
            continue

    return formatted


# RULE SCORE

def calculate_rule_scorecard(rules: List[Dict]) -> float:

    score = 0.0

    for r in rules:
        score += safe_float(r.get("impact", 0))

    return round(score, 3)


# CONFIDENCE

def calculate_explanation_confidence(rule_factors, lime_factors, top_k: int = 3):

    rule_top = {name for name, _ in rule_factors[:top_k]}
    lime_top = {item["feature"] for item in lime_factors[:top_k] if "feature" in item}

    if not rule_top:
        return 0.0

    return round(len(rule_top.intersection(lime_top)) / len(rule_top), 2)


# MAIN PIPELINE

def build_explanation(row: Union[dict, "pd.Series"], model):

    if not isinstance(row, dict):
        row = dict(row)

    row_series = pd.Series(row)

    # FEATURE VECTOR
    feature_vector = np.array([
        [
            safe_float(row_series.get(f, 0))
            for f in FEATURES
        ]
    ])

    # FEATURE CONTRIBUTIONS
    contributions = calculate_feature_contributions(row_series)

    # RANK
    ranked = rank_risk_factors(contributions)

    # TEXT
    explanation_text = generate_explanation_text(ranked)

    # LIME
    lime_explanation = []

    try:
        lime_raw = explain_instance(
            feature_vector[0],
            model
        )

        lime_explanation = format_lime_output(lime_raw)

    except Exception as e:
        print("⚠ LIME FAILED:", e)
        lime_explanation = []

    # RULE ENGINE
    try:
        rule_result = rule_engine(row_series)

        if isinstance(rule_result, dict):
            rules = rule_result.get("detailed_rules", [])
        else:
            rules = rule_result

    except:
        rules = []

    rule_score = calculate_rule_scorecard(rules)

    # CONFIDENCE
    confidence_score = calculate_explanation_confidence(
        ranked,
        lime_explanation
    )

    # FINAL OUTPUT
    return {
        "feature_contributions": contributions,
        "top_risk_factors": ranked,
        "natural_language": explanation_text,
        "lime_explanation": lime_explanation,
        "rule_based_explanations": rules,
        "rule_based_score": rule_score,
        "confidence_score": confidence_score,
        "explanation_method": "Hybrid (Rule Engine + LIME + Feature Attribution)"
    }