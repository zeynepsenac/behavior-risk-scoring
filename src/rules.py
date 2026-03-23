def rule_engine(row):

    rules = []

    if row["missed_payments_6m"] > 3:
        rules.append("Frequent missed payments detected")

    if row["savings_rate"] < 0.1:
        rules.append("Low savings behavior")

    if row["income_variance"] > 0.3:
        rules.append("Unstable income pattern")

    return rules