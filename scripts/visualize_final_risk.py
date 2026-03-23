import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


data_path = BASE_DIR / "data" / "engineered_customers.csv"

df = pd.read_csv(data_path)


def calculate_risk_score(row):
    return (
        0.4 * row["payment_discipline_score"]
        + 0.3 * row["income_stability_index"]
        + 0.3 * row["financial_resilience_score"]
    )


df["predicted_risk_score"] = df.apply(calculate_risk_score, axis=1)

scores = df["predicted_risk_score"]


mean_score = scores.mean()


plt.figure(figsize=(10,6))


plt.hist(scores, bins=30, alpha=0.8)

plt.axvspan(0, 50, alpha=0.2, label="High Risk Zone")
plt.axvspan(50, 75, alpha=0.2, label="Medium Risk Zone")
plt.axvspan(75, 100, alpha=0.2, label="Low Risk Zone")


plt.axvline(50, linestyle="--")
plt.axvline(75, linestyle="--")


plt.axvline(
    mean_score,
    linestyle="-.",
    linewidth=2,
    label=f"Average Risk Score ({mean_score:.2f})"
)


plt.text(
    mean_score + 1,
    plt.ylim()[1]*0.8,
    "Portfolio Risk Level",
    rotation=90
)


high_pct = (scores < 50).mean()*100
med_pct = ((scores >= 50) & (scores < 75)).mean()*100
low_pct = (scores >= 75).mean()*100

ymax = plt.ylim()[1]

plt.text(5, ymax*0.9, f"High Risk: %{high_pct:.1f}")
plt.text(55, ymax*0.9, f"Medium Risk: %{med_pct:.1f}")
plt.text(80, ymax*0.9, f"Low Risk: %{low_pct:.1f}")


plt.title("Predicted Customer Risk Score Distribution")
plt.xlabel("Predicted Risk Score")
plt.ylabel("Number of Customers")

plt.grid(alpha=0.3)
plt.legend()


plt.savefig("risk_distribution_final.png", dpi=300, bbox_inches="tight")

plt.show()