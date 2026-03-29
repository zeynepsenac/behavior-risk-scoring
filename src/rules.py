# src/rules.py

def _safe_num(value, default=0.0):
    """
    Converts values safely to numeric.
    Handles:
    - None
    - NaN
    - string numbers
    """
    try:
        if value is None:
            return default

        # pandas NaN check (NaN != NaN)
        if value != value:
            return default

        return float(value)
    except Exception:
        return default


def _get(row, key, default=0.0):
    """
    Safe access for:
    - dict
    - pandas Series
    - ORM objects
    """
    try:
        if isinstance(row, dict):
            return _safe_num(row.get(key, default))

        # pandas Series support
        if hasattr(row, "__getitem__"):
            return _safe_num(row[key])

        # ORM object fallback
        return _safe_num(getattr(row, key, default))

    except Exception:
        return default


def rule_engine(row):
    """
    Rule-based explanation engine.
    Always returns list[str]
    """

    rules = []

    missed_payments = _get(row, "missed_payments_6m")
    savings_rate = _get(row, "savings_rate")
    income_variance = _get(row, "income_variance")

    # Rule 1
    if missed_payments > 3:
        rules.append("Frequent missed payments detected")

    # Rule 2
    if savings_rate < 0.1:
        rules.append("Low savings behavior")

    # Rule 3
    if income_variance > 0.3:
        rules.append("Unstable income pattern")

    # fallback explanation (important for UX)
    if not rules:
        rules.append("No significant behavioral risk detected")

    return rules