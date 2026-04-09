# =====================================================
# ✅ PROJECT ROOT PATH FIX (MUST BE FIRST)
# =====================================================
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# =====================================================
# IMPORTS
# =====================================================
import pandas as pd
from sqlalchemy import create_engine

# CONFIG
from src.config.settings import DATABASE_TABLES
from src.database import postgres_engine, get_db_connection

# PIPELINE STEPS
from scripts.validation import validate_features
from scripts.load_postgres import promote_to_production

# =====================================================
# TABLE CONFIG
# =====================================================
STAGING_TABLE = DATABASE_TABLES["STAGING_ENGINEERED"]

# =====================================================
# LOAD RAW DATA
# =====================================================
df = pd.read_csv("data/synthetic_customers.csv")

print("Ham veri örneği:")
print(df.head())

# =====================================================
# FEATURE ENGINEERING
# =====================================================

df["payment_discipline_score"] = (
    100
    - (df["bill_payment_delay_avg"] * 5)
    - (df["missed_payments_6m"] * 10)
)

df["payment_discipline_score"] = df["payment_discipline_score"].clip(0, 100)

df["income_stability_index"] = (
    (1 - df["income_variance"]) * 100
).clip(0, 100)

df["financial_resilience_score"] = (
    (df["savings_rate"] * 100)
    - ((df["spending_ratio"] - 0.5) * 50)
)

df["financial_resilience_score"] = df["financial_resilience_score"].clip(0, 100)

# =====================================================
# 🔥 MODEL FEATURE SET GUARANTEE (CRITICAL FIX)
# =====================================================
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
    raise ValueError(f"❌ Eksik model feature'ları: {missing_features}")

print("\n✅ Model feature set doğrulandı")

# =====================================================
# ✅ RISK SCORE NORMALIZATION (SMART FIX)
# =====================================================
# Eğer zaten 0-1 aralığındaysa tekrar normalize ETME

if "risk_score" in df.columns:
    print("\nRisk score kontrol ediliyor...")

    max_val = df["risk_score"].max()

    if max_val > 1:
        print("🔄 Risk score normalize ediliyor (0–1 aralığı)...")

        df["risk_score"] = (
            df["risk_score"]
            .clip(0, 100)
            / 100.0
        )
    else:
        print("✅ Risk score zaten normalize (0–1)")

    print("\nRisk score dağılımı:")
    print(df["risk_score"].describe())

    # Production safety check
    assert df["risk_score"].between(0, 1).all(), \
        "❌ risk_score 0-1 aralığında değil!"

# =====================================================
# 🔥 DATA CLEANING (LIME & MODEL STABILITY)
# =====================================================
df = df.replace([float("inf"), float("-inf")], 0)
df = df.fillna(0)

# =====================================================
# DEBUG OUTPUT
# =====================================================
print("\nÜretilen feature örnekleri:")
print(
    df[
        [
            "payment_discipline_score",
            "income_stability_index",
            "financial_resilience_score",
        ]
    ].head()
)

# =====================================================
# SAVE LOCAL CSV (OPTIONAL ARTIFACT)
# =====================================================
df.to_csv("data/engineered_customers.csv", index=False)

print("\nFeature engineering tamamlandı.")
print("data/engineered_customers.csv oluşturuldu.")

# =====================================================
# WRITE TO POSTGRES STAGING
# =====================================================
print(f"\nStaging tabloya yazılıyor → {STAGING_TABLE}")

df.to_sql(
    STAGING_TABLE,
    postgres_engine,
    if_exists="replace",
    index=False,
)

print("✅ Veri staging_engineered_features tablosuna yazıldı.")

# =====================================================
# VALIDATION STEP
# =====================================================
print("\nValidation başlıyor...")
validate_features(df)
print("✅ Validation başarılı.")

# =====================================================
# PROMOTE TO PRODUCTION
# =====================================================
print("\nProduction'a promote ediliyor...")

promote_to_production()

print("✅ Pipeline tamamlandı (STAGING → PRODUCTION).")