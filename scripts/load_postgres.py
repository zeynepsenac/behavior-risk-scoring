import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from src.database import postgres_engine


# =====================================================
# SAFE ABSOLUTE PATH (FIX)
# =====================================================
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "engineered_customers.csv"

print("Dataset path:", DATA_PATH)

df = pd.read_csv(DATA_PATH)

print("Dataset okundu:", df.shape)


# =====================================================
# POSTGRES LOAD
# =====================================================
df.to_sql(
    "engineered_customers",
    postgres_engine,
    if_exists="replace",
    index=False
)

print("Dataset PostgreSQL'e yüklendi.")
print("engineered_customers PostgreSQL'e başarıyla yüklendi.")