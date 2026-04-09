import sys
import os
from pathlib import Path

# =====================================================
# ✅ PYTHON PATH FIX (PRODUCTION SAFE)
# =====================================================
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# =====================================================
# IMPORTS
# =====================================================
from sqlalchemy import text
from src.database import postgres_engine
from src.config.settings import DATABASE_TABLES


# =====================================================
# TABLE CONFIG (SINGLE SOURCE OF TRUTH)
# =====================================================
STAGING_TABLE = DATABASE_TABLES["STAGING_ENGINEERED"]
PROD_TABLE = DATABASE_TABLES["ENGINEERED"]


print("===================================")
print("POSTGRES PROMOTION PIPELINE START")
print("STAGING TABLE :", STAGING_TABLE)
print("PRODUCTION TABLE :", PROD_TABLE)
print("===================================")


# =====================================================
# VALIDATION — STAGING CHECK
# =====================================================
def validate_staging(conn):

    result = conn.execute(
        text(f"SELECT COUNT(*) FROM {STAGING_TABLE}")
    ).scalar()

    if result == 0:
        raise ValueError("❌ Staging table is empty — promotion aborted")

    print(f"✅ Staging validation passed ({result} rows)")


# =====================================================
# PROMOTION LOGIC (PRODUCTION SAFE)
# =====================================================
def promote_to_production():
    """
    Promote staging → production using transactional engine
    """

    print("🔄 Promoting staging → production...")

    # ✅ transactional execution
    with postgres_engine.begin() as conn:

        # staging validation
        validate_staging(conn)

        # clear production table
        conn.execute(text(f"TRUNCATE TABLE {PROD_TABLE}"))

        # explicit column mapping (schema safety)
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
                financial_resilience_score,
                risk_score,
                risk_band
            FROM {STAGING_TABLE};
        """))

    print("✅ Data successfully promoted to production")


# =====================================================
# MAIN PIPELINE
# =====================================================
def run():

    promote_to_production()

    print("===================================")
    print("✅ Promotion pipeline completed")
    print("===================================")


# =====================================================
# ENTRYPOINT
# =====================================================
if __name__ == "__main__":
    run()