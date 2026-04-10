# src/rules.py

def _safe_num(value, default=0.0):
    try:
        if value is None:
            return default
        if value != value:
            return default
        return float(value)
    except Exception:
        return default


def _get(row, key, default=0.0):
    try:
        if isinstance(row, dict):
            return _safe_num(row.get(key, default))

        if hasattr(row, "__getitem__"):
            return _safe_num(row[key])

        return _safe_num(getattr(row, key, default))

    except Exception:
        return default


def rule_engine(row):
    """
    🔥 HYBRID RULE ENGINE

    Returns:
    {
        "rules": List[str],              # eski sistem (bozulmaz)
        "detailed_rules": List[dict],    # yeni sistem (impact ile)
        "score": float                  # rule-based score
    }
    """

    rules = []
    detailed_rules = []

    # -------------------------------------------------
    # FEATURE EXTRACTION (SAFE)
    # -------------------------------------------------
    missed_payments = _get(row, "missed_payments_6m")
    savings_rate = _get(row, "savings_rate")
    income_variance = _get(row, "income_variance")
    spending_ratio = _get(row, "spending_ratio")
    payment_delay = _get(row, "bill_payment_delay_avg")
    employment_duration = _get(row, "employment_duration_months")

    # -------------------------------------------------
    # 🔴 NEGATIVE RULES
    # -------------------------------------------------
    if spending_ratio > 0.8:
        rules.append("High spending ratio")
        detailed_rules.append({
            "rule": "High spending ratio",
            "impact": 0.15
        })

    if payment_delay > 3:
        rules.append("Frequent payment delay")
        detailed_rules.append({
            "rule": "Frequent payment delay",
            "impact": 0.20
        })

    if missed_payments > 2:
        rules.append("Multiple missed payments")
        detailed_rules.append({
            "rule": "Multiple missed payments",
            "impact": 0.25
        })

    if income_variance > 0.3:
        rules.append("Unstable income pattern")
        detailed_rules.append({
            "rule": "Unstable income pattern",
            "impact": 0.15
        })

    # -------------------------------------------------
    # 🟢 POSITIVE RULES
    # -------------------------------------------------
    if savings_rate > 0.2:
        rules.append("Strong savings behavior")
        detailed_rules.append({
            "rule": "Strong savings behavior",
            "impact": -0.15
        })

    if employment_duration > 60:
        rules.append("Stable employment")
        detailed_rules.append({
            "rule": "Stable employment",
            "impact": -0.10
        })

    if savings_rate < 0.1:
        rules.append("Low savings behavior")
        detailed_rules.append({
            "rule": "Low savings behavior",
            "impact": 0.10
        })

    # -------------------------------------------------
    # FALLBACK (UX)
    # -------------------------------------------------
    if not rules:
        rules.append("No significant behavioral risk detected")
        detailed_rules.append({
            "rule": "No significant behavioral risk detected",
            "impact": 0.0
        })

    # -------------------------------------------------
    # 🔥 RULE SCORE CALCULATION
    # -------------------------------------------------
    rule_score = round(sum(r["impact"] for r in detailed_rules), 3)

    # -------------------------------------------------
    # RETURN HYBRID STRUCTURE
    # -------------------------------------------------
    return {
        "rules": rules,                   # eski sistem
        "detailed_rules": detailed_rules, # yeni sistem
        "score": rule_score               # skor kartı
    }