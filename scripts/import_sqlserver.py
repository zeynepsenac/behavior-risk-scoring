import pandas as pd
from sqlalchemy import create_engine
import urllib

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=riskdb;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# CSV okunuyor (AYNI KALIYOR)
df = pd.read_csv("data/engineered_customers.csv")

# ✅ SADECE BURASI DEĞİŞTİ
df.to_sql(
    "engineered_features",   # ← düzeltildi
    engine,
    if_exists="replace",
    index=False
)

print("Data imported successfully!")