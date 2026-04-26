import pandas as pd

def check_l_diversity(df, quasi_identifiers, sensitive_col, l=3, suppress=False):
    """
    L-diversity kontrolü
    
    Params:
    - df: dataframe
    - quasi_identifiers: grouping columns
    - sensitive_col: sensitive attribute
    - l: diversity threshold (default 3 -> daha güvenli)
    - suppress: True olursa ihlal eden grupları datasetten çıkarır

    Returns:
    - violations: ihlal eden gruplar
    - stats: özet bilgi (rapor için)
    - df (optional): temizlenmiş dataframe (suppress=True ise)
    """

    grouped = (
        df.groupby(quasi_identifiers)[sensitive_col]
        .nunique()
        .reset_index(name="diversity")
    )

    # ihlal eden gruplar
    violations = grouped[grouped["diversity"] < l]

    # =========================
    # 📊 EKSTRA METRİKLER (rapor için)
    # =========================
    total_groups = len(grouped)
    violating_groups = len(violations)

    violation_rate = (violating_groups / total_groups) * 100 if total_groups > 0 else 0

    stats = {
        "total_groups": total_groups,
        "violating_groups": violating_groups,
        "violation_rate_%": round(violation_rate, 2),
        "l_value": l
    }

    print("\nL-DIVERSITY CHECK")
    print(f"Total groups: {total_groups}")
    print(f"Violating groups: {violating_groups}")
    print(f"Violation rate: %{violation_rate:.2f}")
    print(f"L value: {l}")

    # =========================
    # 🔥 OPSİYONEL: SUPPRESSION
    # =========================
    if suppress and violating_groups > 0:
        print("Applying suppression...")

        # ihlal eden grupları merge ile bul
        df = df.merge(
            violations[quasi_identifiers],
            on=quasi_identifiers,
            how="left",
            indicator=True
        )

        # sadece valid olanları tut
        df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])

        print(f"Remaining records after suppression: {len(df)}")

        return violations, stats, df

    return violations, stats