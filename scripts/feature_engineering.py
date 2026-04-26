import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# =========================
# IMPORTS
# =========================
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from src.config.settings import DATABASE_TABLES
from src.database import postgres_engine

from scripts.validation import validate_features
from scripts.load_postgres import promote_to_production

STAGING_TABLE = DATABASE_TABLES["STAGING_ENGINEERED"]

# =========================
# LOAD RAW DATA
# =========================
df = pd.read_csv("data/synthetic_customers.csv")

print("Ham veri örneği:")
print(df.head())

# =========================
# FEATURE ENGINEERING
# =========================

df["payment_discipline_score"] = (
    100
    - (df["bill_payment_delay_avg"] * 5)
    - (df["missed_payments_6m"] * 10)
).clip(0, 100)

df["income_stability_index"] = (
    (1 - df["income_variance"]) * 100
).clip(0, 100)

# =========================
# 🔥 FIXED RESILIENCE (FLOOR EKLENDİ)
# =========================

def calculate_financial_resilience(row):
    savings = row["savings_rate"]
    spending = row["spending_ratio"]
    missed = row["missed_payments_6m"]

    savings_component = savings * 50
    spending_component = (1 - spending) * 30
    payment_component = (1 - min(missed, 5) / 5) * 20

    score = savings_component + spending_component + payment_component

    # ✅ KRİTİK FIX: 0'ı engelle (information loss önleme)
    score = max(score, 5)

    return min(100, score)


df["financial_resilience_score"] = df.apply(
    calculate_financial_resilience, axis=1
)

# =========================
# SAFE NUMERIC HANDLING
# =========================

df["financial_resilience_score"] = df["financial_resilience_score"].replace(
    [np.inf, -np.inf], np.nan
)

# median fallback (mevcut yapı korunuyor)
df["financial_resilience_score"] = df["financial_resilience_score"].fillna(
    df["financial_resilience_score"].median()
)

# strict bounds (model stability)
df["financial_resilience_score"] = df["financial_resilience_score"].clip(0, 100)

# type safety
df["financial_resilience_score"] = df["financial_resilience_score"].astype(float)

print("\nResilience min/max kontrol:")
print(df["financial_resilience_score"].describe())

# =========================
# MODEL FEATURE CHECK
# =========================

MODEL_FEATURES = [
    "monthly_income",
    "income_variance",
    "bill_payment_delay_avg",
    "missed_payments_6m",
    "spending_ratio",
    "savings_rate",
    "employment_duration_months",
    "account_age_months",
]

missing_features = [f for f in MODEL_FEATURES if f not in df.columns]

if missing_features:
    raise ValueError(f"Eksik model feature'ları: {missing_features}")

print("\nModel feature set doğrulandı")

# =========================
# RISK SCORE NORMALIZATION
# =========================

if "risk_score" in df.columns:
    print("\nRisk score kontrol ediliyor...")

    df["risk_score"] = df["risk_score"].clip(0, 100)

    if df["risk_score"].max() > 1:
        print("Risk score normalize ediliyor (0–1)...")
        df["risk_score"] = df["risk_score"] / 100.0

    print(df["risk_score"].describe())

    assert df["risk_score"].between(0, 1).all(), "risk_score 0-1 değil!"

# =========================
# SAFE CLEANING
# =========================

df = df.replace([np.inf, -np.inf], np.nan)

feature_cols = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

# median fill (mevcut yapı korunuyor)
df[feature_cols] = df[feature_cols].fillna(df[feature_cols].median())

# diğer kolonlar
other_cols = [c for c in df.columns if c not in feature_cols]
df[other_cols] = df[other_cols].fillna(0)

# =========================
# CONSISTENCY CHECK
# =========================

print("\nFeature range check:")

for col in feature_cols:
    print(f"{col}: min={df[col].min()}, max={df[col].max()}")

# =========================
# SAVE LOCAL
# =========================

df.to_csv("data/engineered_customers.csv", index=False)
print("\nFeature engineering tamamlandı.")

# =========================
# POSTGRES WRITE
# =========================

print(f"\nStaging tabloya yazılıyor → {STAGING_TABLE}")

df.to_sql(
    STAGING_TABLE,
    postgres_engine,
    if_exists="replace",
    index=False,
)

print("Veri staging'e yazıldı.")

# =========================
# VALIDATION
# =========================

print("\nValidation başlıyor...")
validate_features(df)
print("Validation başarılı.")

# =========================
# PROMOTION
# =========================

print("\nProduction'a promote ediliyor...")
promote_to_production()
print("Pipeline tamamlandı.")