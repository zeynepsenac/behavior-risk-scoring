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

df = pd.read_csv("data/engineered_customers.csv")

df.to_sql(
    "engineered_customers",
    engine,
    if_exists="replace",
    index=False
)

print(" Data imported successfully!")