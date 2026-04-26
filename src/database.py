from sqlalchemy import create_engine, text
import pandas as pd
import psycopg2
import os
import socket
import numpy as np   

from src.config.settings import DATABASE_TABLES


# =========================
# DB HOST AUTO DETECT
# =========================
def detect_db_host():

    env_host = os.getenv("DB_HOST")
    if env_host:
        return env_host

    try:
        socket.gethostbyname("risk_postgres")
        return "risk_postgres"
    except socket.error:
        return "localhost"


DB_HOST = detect_db_host()

DB_NAME = os.getenv("DB_NAME", "riskdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")

print(f"Using DB host: {DB_HOST}")


# =========================
# CONNECTION STRING
# =========================
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

postgres_engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)


DEFAULT_ENGINEERED_TABLE = DATABASE_TABLES["ENGINEERED"]


# =========================
# RAW CONNECTION
# =========================
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# =========================
# TABLE CHECK
# =========================
def verify_table_exists(conn, table_name: str):

    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            );
        """, (table_name,))

        exists = cur.fetchone()[0]

    if not exists:
        raise RuntimeError(f"Table not found: {table_name}")


# =========================
# DATA LOADER (FIXED + SAFE ML VERSION)
# =========================
def load_customers_postgres(table_name: str = DEFAULT_ENGINEERED_TABLE):

    conn = get_db_connection()
    try:
        verify_table_exists(conn, table_name)
    finally:
        conn.close()

    query = f"""
        SELECT 
            customer_id,
            payment_discipline_score,
            income_stability_index,
            financial_resilience_score
        FROM {table_name}
    """

    df = pd.read_sql(query, postgres_engine)

    # =========================
    # 🔥 ML SAFETY LAYER (IMPROVED)
    # =========================

    feature_cols = [
        "payment_discipline_score",
        "income_stability_index",
        "financial_resilience_score"
    ]

    # ❗ FIX 1: inf -> NaN
    df[feature_cols] = df[feature_cols].replace([np.inf, -np.inf], np.nan)

    # ❗ FIX 2: smarter imputation (median instead of 0 bias)
    df[feature_cols] = df[feature_cols].fillna(df[feature_cols].median())

    # ❗ FIX 3: type safety
    df[feature_cols] = df[feature_cols].astype(float)

    # ❗ FIX 4: hard lower bound (no negative ML noise)
    for col in feature_cols:
        df[col] = df[col].clip(lower=0, upper=100)

    return df


def load_customers(table_name: str = DEFAULT_ENGINEERED_TABLE):
    return load_customers_postgres(table_name)


# =========================
# SCHEMA CHECK (UNCHANGED)
# =========================
REQUIRED_COLUMNS = {
    "risk_score",
    "model_version",
    "feature_version",
    "dataset_version",
    "original_band",
    "predicted_band",
}


def verify_schema(conn):

    cur = conn.cursor()

    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'prediction_history'
    """)

    existing_columns = {row[0] for row in cur.fetchall()}
    missing = REQUIRED_COLUMNS - existing_columns

    cur.close()

    if missing:
        raise RuntimeError(
            f"Database schema mismatch! Missing columns: {missing}"
        )


# =========================
# SCORE NORMALIZATION
# =========================
def normalize_risk_score(score: float) -> float:
    return float(1 / (1 + np.exp(-score)))


# =========================
# SAVE PREDICTIONS (IMPROVED SAFETY)
# =========================
def save_predictions_to_db(df):

    print("Saving predictions to database...")

    required_cols = [
        "customer_id",
        "risk_score",
        "original_band",
        "predicted_band",
    ]

    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns for DB insert: {missing}")

    insert_query = text("""
        INSERT INTO prediction_history (
            customer_id,
            risk_score,
            original_band,
            predicted_band,
            model_version,
            feature_version,
            dataset_version,
            prediction_time,
            created_by
        )
        VALUES (
            :customer_id,
            :risk_score,
            :original_band,
            :predicted_band,
            :model_version,
            :feature_version,
            :dataset_version,
            NOW(),
            'batch_pipeline'
        )
    """)

    with postgres_engine.begin() as conn:
        conn.execute(
            insert_query,
            [
                {
                    "customer_id": int(row["customer_id"]),
                    "risk_score": normalize_risk_score(float(row["risk_score"])),
                    "original_band": row["original_band"],
                    "predicted_band": row["predicted_band"],
                    "model_version": row.get("model_version", "offline"),
                    "feature_version": row.get("feature_version", "v1"),
                    "dataset_version": row.get("dataset_version", "v1"),
                }
                for _, row in df.iterrows()
            ]
        )

    print("Predictions saved to DB.")