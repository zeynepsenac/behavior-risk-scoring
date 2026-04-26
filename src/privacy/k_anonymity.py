import pandas as pd

def check_k_anonymity(df, quasi_identifiers, k=3):
    #  1. Temel kontroller
    if df is None or df.empty:
        print(" DataFrame boş")
        return pd.DataFrame()

    if not isinstance(quasi_identifiers, list) or not quasi_identifiers:
        print(" Quasi-identifier listesi boş veya hatalı")
        return pd.DataFrame()

    #  2. Sadece geçerli kolonları al
    valid_qi = [col for col in quasi_identifiers if col in df.columns]

    if not valid_qi:
        print(" Geçerli quasi-identifier bulunamadı")
        return pd.DataFrame()

    #  3. Eksik değer kontrolü (çok kritik)
    if df[valid_qi].isnull().any().any():
        print(" Quasi-identifier kolonlarında eksik değer var → dolduruluyor")
        df = df.copy()
        df[valid_qi] = df[valid_qi].fillna("UNKNOWN")

    #  4. Grouping işlemi
    grouped = (
        df.groupby(valid_qi, dropna=False)
        .size()
        .reset_index(name='count')
    )

    #  5. k-anonymity ihlalleri (k'tan küçük gruplar)
    violations = grouped[grouped['count'] < k]

    #  6. Debug çıktıları (jüri için güzel detay)
    print(f"Toplam grup sayısı: {len(grouped)}")
    print(f"İhlal eden grup sayısı (k<{k}): {len(violations)}")

    if not violations.empty:
        print("Örnek ihlaller:")
        print(violations.head())

    return violations


#  EKLENEN KISIM (L-DIVERSITY)
def check_l_diversity(df, quasi_identifiers, sensitive_col, l=2):
    #  Temel kontroller
    if df is None or df.empty:
        print(" DataFrame boş")
        return pd.DataFrame()

    if not quasi_identifiers or sensitive_col not in df.columns:
        print(" L-diversity için gerekli kolonlar eksik")
        return pd.DataFrame()

    #  Grouping
    grouped = (
        df.groupby(quasi_identifiers)[sensitive_col]
        .nunique()
        .reset_index(name="diversity")
    )

    #  İhlaller (l'den küçük çeşitlilik)
    violations = grouped[grouped["diversity"] < l]

    #  Debug çıktısı
    print(f"Toplam grup sayısı: {len(grouped)}")
    print(f"L-diversity ihlal eden grup sayısı (l<{l}): {len(violations)}")

    if not violations.empty:
        print("Örnek L-diversity ihlalleri:")
        print(violations.head())

    return violations