import pandas as pd
import os

FORM_PATH = "data/user_form_responses.csv"
TERMINAL_PATH = "reports/user_test_results.csv"


# FORM VERİSİNİ TEMİZLE
def process_form():
    if not os.path.exists(FORM_PATH):
        print(" Form verisi yok")
        return pd.DataFrame()

    df = pd.read_csv(FORM_PATH)
    df.columns = df.columns.str.strip()

    understanding_map = {
        "Evet": 10,
        "Kısmen": 7,
        "Hayır": 3
    }

    decision_map = {
        "Evet": 10,
        "Hayır": 5,
        "Emin Değilim": 7
    }

    try:
        form_clean = pd.DataFrame({
            "understanding_score": df["Bu risk skorunun neden oluştuğunu anladınız mı?"].map(understanding_map),
            "usability_score": pd.to_numeric(df["Açıklamayı ne kadar yeterli buldunuz?"], errors='coerce') * 2,
            "trust_score": pd.to_numeric(df["Modelin verdiği risk skoruna ne kadar güveniyorsunuz?"], errors='coerce') * 2,
            "decision_score": df["Bu risk skoruna dayanarak finansal bir karar verir miydiniz?"].map(decision_map),
            "prediction": df["Sizce bu müşteri hangi risk grubundadır?"]
        })
    except KeyError as e:
        print(f" Kolon bulunamadı: {e}")
        return pd.DataFrame()

    form_clean = form_clean.dropna(how="all")

    print(" Form verisi yüklendi")
    return form_clean



# TERMINAL VERİSİ
def process_terminal():
    if not os.path.exists(TERMINAL_PATH):
        print(" Terminal verisi yok")
        return pd.DataFrame()

    df = pd.read_csv(TERMINAL_PATH, on_bad_lines='skip')

    cols = ["understanding_score", "usability_score", "trust_score", "decision_score", "prediction_score"]
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    print(" Terminal verisi yüklendi")
    return df


# BİRLEŞTİR
def combine_data():
    form_df = process_form()
    terminal_df = process_terminal()

    combined = pd.concat([form_df, terminal_df], ignore_index=True)
    combined = combined.dropna(how="all")

    return combined


# ANALİZ
def analyze(df):
    if df.empty:
        print(" Veri yok")
        return

    # 🔥 FIX 1: 0 artık "missing" sayılmayacak
    for col in ["understanding_score", "usability_score", "trust_score", "decision_score", "prediction_score"]:
        if col not in df.columns:
            df[col] = pd.NA   # ❌ 0 DEĞİL → TRUE missing

    # 🔥 FIX 2: fillna(0) kaldırıldı → veri kaybını engelliyoruz
    df = df.fillna(df.median(numeric_only=True))

    # 🔥 FIX 3: güvenli numeric conversion
    for col in ["understanding_score", "usability_score", "trust_score", "decision_score", "prediction_score"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    understanding = df["understanding_score"].mean()
    usability = df["usability_score"].mean()
    trust = df["trust_score"].mean()
    decision = df["decision_score"].mean()
    accuracy = df["prediction_score"].mean()

    print("\n BİRLEŞİK ANALİZ SONUÇLARI\n")

    print(" Anlaşılabilirlik:", round(understanding, 2))
    print(" Kullanılabilirlik:", round(usability, 2))
    print(" Model Güveni:", round(trust, 2))
    print(" Karar Güveni:", round(decision, 2))

    print("\n Toplam veri:", len(df))

    print("\n GENEL DEĞERLENDİRME")
    print(f"- Anlaşılabilirlik: {round(understanding,2)} / 10")
    print(f"- Model Güveni: {round(trust,2)} / 10")
    print(f"- Kullanılabilirlik: {round(usability,2)} / 10")

    # 🔥 FIX 4: skor stabilizasyonu (NaN koruma)
    final_score = (
        0.25 * (understanding or 0) +
        0.25 * (trust or 0) +
        0.20 * (usability or 0) +
        0.15 * (decision or 0) +
        0.15 * (accuracy or 0)
    )

    print(f"\n FINAL AI SCORE: {round(final_score,2)} / 10")


# MAIN
def main():
    print(" VERİLER BİRLEŞTİRİLİYOR...")

    df = combine_data()
    analyze(df)


if __name__ == "__main__":
    main()