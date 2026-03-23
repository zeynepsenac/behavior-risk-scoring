import pandas as pd
from xgboost import XGBRegressor
import joblib


df = pd.read_csv("data/engineered_customers.csv")

features = [
    "payment_discipline_score",
    "income_stability_index",
    "financial_resilience_score"
]

X = df[features]
y = df["risk_score"]

model = XGBRegressor(
    n_estimators=120,
    max_depth=4,
    learning_rate=0.05,
    random_state=42
)

model.fit(X, y)


joblib.dump(model, "models/risk_model.pkl")

print("Model trained and saved")