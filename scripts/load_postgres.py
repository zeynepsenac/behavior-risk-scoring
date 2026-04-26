import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from sqlalchemy import text
from src.database import postgres_engine
from src.config.settings import DATABASE_TABLES


STAGING_TABLE = DATABASE_TABLES["STAGING_ENGINEERED"]
PROD_TABLE = DATABASE_TABLES["ENGINEERED"]


print("===================================")
print("POSTGRES PROMOTION PIPELINE START")
print("STAGING TABLE :", STAGING_TABLE)
print("PRODUCTION TABLE :", PROD_TABLE)
print("===================================")


# =========================
# VALIDATION
# =========================
def validate_staging(conn):

    result = conn.execute(
        text(f"SELECT COUNT(*) FROM {STAGING_TABLE}")
    ).scalar()

    if result == 0:
        raise ValueError("Staging table is empty — promotion aborted")

    # 🔥 STRONG VALIDATION
    bad_rows = conn.execute(text(f"""
        SELECT COUNT(*) FROM {STAGING_TABLE}
        WHERE financial_resilience_score IS NULL
           OR financial_resilience_score <= 1   -- 🔥 threshold eklendi
    """)).scalar()

    print(f"⚠️ Rows with NULL/invalid resilience: {bad_rows}")

    # 🔥 HARD FAIL (production-grade behavior)
    if bad_rows > 0:
        raise ValueError(
            f"Invalid financial_resilience_score detected ({bad_rows} rows). Pipeline stopped."
        )

    print(f"Staging validation passed ({result} rows)")


# =========================
# PROMOTION
# =========================
def promote_to_production():

    print("Promoting staging → production...")

    with postgres_engine.begin() as conn:

        validate_staging(conn)

        conn.execute(text(f"TRUNCATE TABLE {PROD_TABLE}"))

        conn.execute(text(f"""
            INSERT INTO {PROD_TABLE} (
                customer_id,
                payment_discipline_score,
                income_stability_index,
                financial_resilience_score,
                risk_score,
                risk_band
            )
            SELECT
                customer_id,
                payment_discipline_score,
                income_stability_index,

                -- 🔥 SAFE PASS (low-quality values filtered)
                CASE 
                    WHEN financial_resilience_score IS NULL THEN NULL
                    WHEN financial_resilience_score <= 1 THEN NULL
                    ELSE financial_resilience_score
                END AS financial_resilience_score,

                risk_score,
                risk_band

            FROM {STAGING_TABLE}
        """))

        # =========================
        # 🔥 POST-CHECK (CRITICAL)
        # =========================
        null_count = conn.execute(text(f"""
            SELECT COUNT(*) FROM {PROD_TABLE}
            WHERE financial_resilience_score IS NULL
        """)).scalar()

        print(f"📊 Production NULL resilience count: {null_count}")

        if null_count > 0:
            print("⚠️ WARNING: Production contains NULL resilience values")

    print("Data successfully promoted to production")


# =========================
# RUN
# =========================
def run():
    promote_to_production()

    print("===================================")
    print("Promotion pipeline completed")
    print("===================================")


if __name__ == "__main__":
    run()