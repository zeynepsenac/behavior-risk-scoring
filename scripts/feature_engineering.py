import pandas as pd


df = pd.read_csv("data/synthetic_customers.csv")

print(" Ham veri örneği:")
print(df.head())


df["payment_discipline_score"] = (
    100
    - (df["bill_payment_delay_avg"] * 5)
    - (df["missed_payments_6m"] * 10)
)

df["payment_discipline_score"] = df["payment_discipline_score"].clip(0, 100)


df["income_stability_index"] = (
    (1 - df["income_variance"]) * 100
).clip(0, 100)


df["financial_resilience_score"] = (
    (df["savings_rate"] * 100)
    - ((df["spending_ratio"] - 0.5) * 50)
)

df["financial_resilience_score"] = df["financial_resilience_score"].clip(0, 100)


print("\n Üretilen feature örnekleri:")
print(
    df[
        [
            "payment_discipline_score",
            "income_stability_index",
            "financial_resilience_score"
        ]
    ].head()
)


df.to_csv("data/engineered_customers.csv", index=False)

print("\n Feature engineering tamamlandı.")
print(" data/engineered_customers.csv oluşturuldu.")
