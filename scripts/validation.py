import pandas as pd
from sklearn.metrics import mean_absolute_error

# -----------------------------------
# Load prediction results
# -----------------------------------
df = pd.read_csv("data/predictions.csv")

# -----------------------------------
# Model accuracy (MAE)
# -----------------------------------
mae = mean_absolute_error(
    df["risk_score"],
    df["predicted_risk_score"]
)

print("MAE:", round(mae, 3))

# -----------------------------------
# Fairness / Bias Check
# -----------------------------------
print("\nIncome Group Bias Check:")

bias_check = (
    df.groupby(pd.qcut(df["monthly_income"], 4))
      ["predicted_risk_score"]
      .mean()
)

print(bias_check)