import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# src import fix
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.privacy.anonymizer import anonymize_dataframe
from src.privacy.k_anonymity import check_k_anonymity
from src.privacy.l_diversity import check_l_diversity  

# 1. veri oku
df = pd.read_csv("data/engineered_customers.csv")

print(" ANONYMIZATION PIPELINE STARTED")

print("Kolonlar:", df.columns.tolist())

original_size = len(df)
print(f"Veri boyutu (önce): {original_size}")

# 2. anonimleştir
anon_df = anonymize_dataframe(df)

print("Anonim kolonlar:", anon_df.columns.tolist())

# 3. k-anonymity
quasi_identifiers = [
    col for col in [
        "age_group",
        "monthly_income",
        "spending_ratio",
        "account_age_months"
    ]
    if col in anon_df.columns
]

if not quasi_identifiers:
    print(" Uygun quasi-identifier bulunamadı")
    violations = pd.DataFrame()
else:
    K_VALUE = 3

    violations = check_k_anonymity(anon_df, quasi_identifiers, k=K_VALUE)

    print(f"\n K-ANONYMITY ANALİZİ (k={K_VALUE})")
    print(f"İhlal sayısı: {len(violations)}")

    if not violations.empty:
        violation_ratio = len(violations) / len(anon_df)
        print(f"İhlal oranı: %{round(violation_ratio * 100, 2)}")

        # 🔥 FIX 1: threshold artırıldı (0.10 → 0.20)
        if violation_ratio > 0.20:

            if "spending_ratio" in anon_df.columns:
                anon_df["spending_ratio"] = anon_df["spending_ratio"].apply(
                    lambda x: round(float(x), -1) if pd.notna(x) else x
                )

            if "monthly_income" in anon_df.columns:
                anon_df["monthly_income"] = anon_df["monthly_income"].apply(
                    lambda x: (
                        int(x.split("-")[0]) // 20000 * 20000
                    ) if isinstance(x, str) else x
                )

            violations = check_k_anonymity(anon_df, quasi_identifiers, k=K_VALUE)

    # suppression
    if not violations.empty:
        before_suppression = len(anon_df)

        merged = anon_df.merge(
            violations[quasi_identifiers],
            on=quasi_identifiers,
            how="left",
            indicator=True
        )

        anon_df = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])

        after_suppression = len(anon_df)

        print(f"Suppression kaldırılan: {before_suppression - after_suppression}")

# =========================
# ✅ L-DIVERSITY FIXED
# =========================
if quasi_identifiers and "risk_score" in anon_df.columns:

    # 🔥 FIX 2: L=2 → L=3
    L_VALUE = 3

    l_violations, stats = check_l_diversity(
        anon_df,
        quasi_identifiers,
        sensitive_col="risk_score",
        l=L_VALUE
    )

    print(f"L-Diversity ihlal: {len(l_violations)}")

    if not l_violations.empty:
        before_l = len(anon_df)

        merged = anon_df.merge(
            l_violations[quasi_identifiers],
            on=quasi_identifiers,
            how="left",
            indicator=True
        )

        anon_df = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])

        after_l = len(anon_df)

        print(f"L-suppression: {before_l - after_l}")

# =========================
# VERİ KALİTESİ
# =========================
final_size = len(anon_df)

loss_ratio = 0
if original_size > 0:
    loss_ratio = 1 - (final_size / original_size)

print("\n METRİKLER")

group_sizes = anon_df.groupby(quasi_identifiers).size()

avg_group = round(group_sizes.mean(), 2)
min_group = int(group_sizes.min())

# ================================
# RISK MODEL
# ================================
singleton_ratio = (group_sizes == 1).sum() / len(group_sizes)
small_group_ratio = (group_sizes < 3).sum() / len(group_sizes)
unique_ratio = len(group_sizes.unique()) / len(group_sizes)

risk = (
    0.5 * singleton_ratio +
    0.3 * small_group_ratio +
    0.2 * (1 - unique_ratio)
)

distinct_risk_score = int(anon_df["risk_score"].nunique())

print(avg_group, min_group, risk, distinct_risk_score)

# =========================
# TABLO
# =========================
report_df = pd.DataFrame([
    ["Original Records", int(original_size)],
    ["Final Records", int(final_size)],
    ["Data Loss (%)", round(loss_ratio * 100, 2)],
    ["Average Group Size", avg_group],
    ["Minimum Group Size", min_group],
    ["Re-identification Risk (%)", round(risk * 100, 2)],
    ["Distinct risk_score", distinct_risk_score],
    ["K value", K_VALUE],
    ["L value", L_VALUE]
], columns=["Metric", "Value"])

print(report_df)

Path("reports").mkdir(exist_ok=True)
report_df.to_csv("reports/final_metrics_table.csv", index=False)

# =========================
# GRAFİK
# =========================
plt.figure(figsize=(10, 5))

metrics_to_plot = {
    "Original": original_size,
    "Final": final_size,
    "Risk (%)": risk * 100,
    "Distinct Risk Score": distinct_risk_score
}

plt.bar(metrics_to_plot.keys(), metrics_to_plot.values())
plt.title("Anonymization Pipeline Summary")
plt.ylabel("Value")

plt.savefig("reports/metrics_plot.png")
plt.close()

# =========================
# SAVE
# =========================
anon_df.to_csv("data/anonymized_customers.csv", index=False)

print("\n Pipeline tamamlandı")
print(" Grafik: reports/metrics_plot.png")
print(" Tablo: reports/final_metrics_table.csv")