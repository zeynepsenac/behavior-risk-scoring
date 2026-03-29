from sqlalchemy import create_engine
import pandas as pd
import urllib
import psycopg2
import os
import socket


# =====================================================
# DATABASE HOST AUTO DETECT (Docker + Local SMART MODE)
# =====================================================

def detect_db_host():
    """
    Öncelik sırası:
     ENV varsa onu kullan
     Docker network'te risk_postgres erişilebiliyorsa onu kullan
     fallback localhost
    """

    # ENV override (en güvenlisi)
    env_host = os.getenv("DB_HOST")
    if env_host:
        return env_host

    # Docker container DNS test
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


print(f" Using DB host: {DB_HOST}")


# =====================================================
# SQL SERVER (ŞU AN KAPALI — DOKUNULMADI)
# =====================================================

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=riskdb;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# sqlserver_engine = create_engine(
#     f"mssql+pyodbc:///?odbc_connect={params}"
# )


# =====================================================
# POSTGRES CONNECTION STRING
# =====================================================

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

postgres_engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # connection drop fix
    pool_size=5,
    max_overflow=10
)

TABLE_NAME = "engineered_customers"


# =====================================================
# DATA LOADERS
# =====================================================

def load_customers_postgres():
    query = f"SELECT * FROM {TABLE_NAME}"
    return pd.read_sql(query, postgres_engine)


def load_customers():
    """
    Projenin ana veri kaynağı.
    """
    return load_customers_postgres()


# =====================================================
# RAW CONNECTION (psycopg2)
# =====================================================

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )