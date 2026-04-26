import numpy as np
import pandas as pd

np.random.seed(42)

N = 1200  

monthly_income = np.random.normal(30000, 9000, N).clip(12000, 120000)
income_variance = np.random.uniform(0.05, 0.4, N)

bill_payment_delay_avg = np.random.exponential(
    scale=2 + income_variance * 5, size=N
).clip(0, 30)

missed_payments_6m = (
    bill_payment_delay_avg / 5 + np.random.poisson(0.8, N)
).astype(int).clip(0, 6)

spending_ratio = np.random.uniform(0.3, 1.1, N)
savings_rate = (1 - spending_ratio + np.random.normal(0, 0.05, N)).clip(0, 0.4)

employment_duration = np.random.randint(3, 300, N)  
account_age = np.random.randint(6, 240, N)  

# ----------------------------
# 🔥 RISK SCORE (unchanged logic)
# ----------------------------
risk_score = (
    (missed_payments_6m * 12) +
    (bill_payment_delay_avg * 1.5) +
    (spending_ratio * 20) -
    (savings_rate * 30) -
    (employment_duration / 12)
).clip(0, 100)

risk_band = pd.cut(
    risk_score,
    bins=[-0.01, 33, 66, 100],
    labels=["Low", "Medium", "High"]
)

# ----------------------------
# 🔥 NEW FEATURE: financial_resilience_score (FIX)
# ----------------------------
financial_resilience_score = (
    (savings_rate * 100) +
    (employment_duration / 12 * 5) +
    (account_age / 24 * 3) -
    (missed_payments_6m * 8) -
    (bill_payment_delay_avg * 2)
)

# normalize 0-100
financial_resilience_score = (
    (financial_resilience_score - financial_resilience_score.min()) /
    (financial_resilience_score.max() - financial_resilience_score.min() + 1e-9)
) * 100

financial_resilience_score = financial_resilience_score.round(2)

# ----------------------------
# DATASET
# ----------------------------
data = {
    "customer_id": range(1, N + 1),
    "monthly_income": monthly_income.round(2),
    "income_variance": income_variance.round(3),
    "bill_payment_delay_avg": bill_payment_delay_avg.round(2),
    "missed_payments_6m": missed_payments_6m,
    "spending_ratio": spending_ratio.round(2),
    "savings_rate": savings_rate.round(2),
    "employment_duration_months": employment_duration,
    "account_age_months": account_age,
    "risk_score": risk_score.round(0),
    "risk_band": risk_band,

    # 🔥 FIXED FEATURE ADDED
    "financial_resilience_score": financial_resilience_score
}

df = pd.DataFrame(data)

df.to_csv("data/synthetic_customers.csv", index=False)

print(f"{N} adet açıklanabilir sentetik müşteri verisi üretildi (resilience FIX dahil).")