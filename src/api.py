from fastapi import FastAPI
import pandas as pd



app = FastAPI(
    title="Behavior-Based Micro Risk Scoring API",
    description="Behavioral risk scoring system using explainable rule-based scoring",
    version="1.0"
)



df = pd.read_csv("data/engineered_customers.csv")



def calculate_risk_score(row):
    """
    Explainable weighted risk score
    """
    return (
        0.4 * row["payment_discipline_score"]
        + 0.3 * row["income_stability_index"]
        + 0.3 * row["financial_resilience_score"]
    )

def risk_segment(score):
    """
    Risk segmentation for interpretability
    """
    if score >= 75:
        return "Low Risk"
    elif score >= 50:
        return "Medium Risk"
    else:
        return "High Risk"



@app.get("/risk-score/{customer_id}")
def get_risk_score(customer_id: int):
    """
    Returns explainable risk score for a given customer
    """

    customer = df[df["customer_id"] == customer_id]

    if customer.empty:
        return {"error": "Customer not found"}

    row = customer.iloc[0]
    score = calculate_risk_score(row)

    return {
        "customer_id": int(customer_id),
        "risk_score": round(float(score), 2),
        "risk_segment": risk_segment(score),
        "components": {
            "payment_discipline_score": round(float(row["payment_discipline_score"]), 2),
            "income_stability_index": round(float(row["income_stability_index"]), 2),
            "financial_resilience_score": round(float(row["financial_resilience_score"]), 2)
        }
    }
