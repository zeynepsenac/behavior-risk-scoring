import pandas as pd
from sklearn.metrics import mean_absolute_error


# =====================================================
# FEATURE VALIDATION (PIPELINE SAFETY LAYER)
# =====================================================
def validate_features(df: pd.DataFrame):

    if df.empty:
        raise ValueError("Dataset empty")

    if df.isnull().sum().sum() > 0:
        raise ValueError("Null values detected")

    if "customer_id" not in df.columns:
        raise ValueError("customer_id missing")

    print("✅ Feature validation passed")


# =====================================================
# MODEL VALIDATION SCRIPT
# =====================================================
if __name__ == "__main__":

    # -----------------------------------
    # Load prediction results
    # -----------------------------------
    df = pd.read_csv("data/predictions.csv")

    print("Columns detected:", list(df.columns))

    # -----------------------------------
    # Model accuracy (MAE)
    # -----------------------------------
    mae = mean_absolute_error(
        df["risk_score"],
        df["predicted_risk_score"]
    )

    print("MAE:", round(mae, 3))

    # -----------------------------------
    # Fairness / Bias Check (SAFE VERSION)
    # -----------------------------------
    print("\nIncome Group Bias Check:")

    if "monthly_income" in df.columns:

        bias_check = (
            df.groupby(pd.qcut(df["monthly_income"], 4))
              ["predicted_risk_score"]
              .mean()
        )

        print(bias_check)

    else:
        print("⚠ monthly_income column not found — bias check skipped")