import pandas as pd
import json
import os
import sys

DATA_PATH = "data/predictions.csv"
OUTPUT_PATH = "reports/user_test_results.csv"
METRICS_PATH = "reports/user_test_metrics.csv"

def check_exit(value):
    if isinstance(value, str) and value.lower().strip() in ["q", "quit", "exit"]:
        print("\n Test sonlandırıldı. Mevcut veriler korunmuştur.\n")
        raise SystemExit
    return value

def interpret_score(value):
    if value >= 80:
        return "yüksek"
    elif value >= 60:
        return "orta"
    else:
        return "düşük"

#  GÜÇLENDİRİLMİŞ AÇIKLAMA
def generate_explanation(sample):
    explanations = []

    if sample["payment_discipline_score"] < 60:
        explanations.append(f"ödeme disiplini düşük (%{round(sample['payment_discipline_score'],1)})")

    if sample["financial_resilience_score"] < 20:
        explanations.append(f"finansal dayanıklılık çok düşük (%{round(sample['financial_resilience_score'],1)})")

    if sample["income_stability_index"] > 80:
        explanations.append(f"gelir istikrarı yüksek (%{round(sample['income_stability_index'],1)})")

    if len(explanations) == 0:
        return "Müşteri dengeli finansal davranış sergilemektedir."

    return "Bu müşteri için " + ", ".join(explanations) + " olduğu için risk seviyesi etkilenmiştir."

def print_customer_analysis(sample):
    risk_score = int(sample["predicted_risk_score"] * 100)

    print("\n==============================")
    print("   MÜŞTERİ RİSK ANALİZİ")
    print("==============================\n")

    print(f"Risk Skoru       : {risk_score}/100")
    print(f"Risk Seviyesi    : {sample['predicted_band']}")
    print(f"Model Güveni     : %{int(sample['model_confidence'] * 100)}\n")

    print("Müşteri Özellikleri:")
    print(f"- Gelir İstikrarı        : {round(sample['income_stability_index'],1)} ({interpret_score(sample['income_stability_index'])})")
    print(f"- Ödeme Disiplini        : {round(sample['payment_discipline_score'],1)} ({interpret_score(sample['payment_discipline_score'])})")
    print(f"- Finansal Dayanıklılık  : {round(sample['financial_resilience_score'],1)} ({interpret_score(sample['financial_resilience_score'])})")

    print("\nAçıklama (Model Yorumu):")
    print(generate_explanation(sample))
    print("\n Geri bildiriminiz model geliştirme için kullanılacaktır.")
    print(" Çıkmak için 'q' yazabilirsiniz.\n")

def clean_feature_name(feature):
    mapping = {
        "payment_discipline_score": "Ödeme disiplini",
        "income_stability_index": "Gelir istikrarı",
        "financial_resilience_score": "Finansal dayanıklılık"
    }
    return mapping.get(feature, feature)

#  LIME FIX
def print_lime_explanation(sample):
    print("Riski Etkileyen Faktörler:")

    try:
        explanation = json.loads(sample["lime_explanation"])

        for item in explanation:
            feature = item["feature"]
            impact = item["impact"]

            if feature not in ["payment_discipline_score", "income_stability_index", "financial_resilience_score"]:
                continue

            feature_name = clean_feature_name(feature)

            direction = "riski azaltıyor" if impact < 0 else "riski artırıyor"

            print(f"{feature_name} {direction} ({round(impact, 3)})")

    except Exception:
        print("Açıklama verisi okunamadı.")

def map_understanding(q1):
    return {"evet": 10, "kismen": 7, "hayir": 3}.get(q1, 5)

def map_prediction_accuracy(user_pred, model_pred):
    return 10 if user_pred == model_pred else 5

def map_trust(q4):
    return q4 * 2

def map_decision(q5):
    return {"evet": 10, "hayir": 5, "emin_degilim": 7}.get(q5, 5)

def ask_questions():
    print("\n--- KULLANICI TESTİ ---")

    q1 = check_exit(input("Riskin neden oluştuğunu anladınız mı? (evet/kismen/hayir): ").lower().strip())

    while True:
        try:
            q2 = int(check_exit(input("Açıklamayı 1-5 arası puanlayın: ")))
            if 1 <= q2 <= 5:
                break
        except:
            pass
        print("Lütfen 1 ile 5 arasında bir değer girin.")

    while True:
        try:
            q4 = int(check_exit(input("Modele güveniniz (1-5): ")))
            if 1 <= q4 <= 5:
                break
        except:
            pass
        print("Lütfen 1 ile 5 arasında bir değer girin.")

    q3 = check_exit(input("Sizce risk seviyesi ne? (LOW/MEDIUM/HIGH): ").upper().strip())
    q5 = check_exit(input("Bu risk skoruna göre karar verir miydiniz? (evet/hayir/emin_degilim): ").lower().strip())

    return q1, q2, q3, q4, q5

def save_result(q1, q2, q3, q4, q5, model_pred):
    os.makedirs("reports", exist_ok=True)

    new_data = pd.DataFrame([{
        "understood": q1,
        "understanding_score": map_understanding(q1),
        "usability_score": q2 * 2,
        "trust_score": map_trust(q4),
        "decision": q5,
        "decision_score": map_decision(q5),
        "prediction": q3,
        "prediction_score": map_prediction_accuracy(q3, model_pred)
    }])

    if not os.path.exists(OUTPUT_PATH):
        new_data.to_csv(OUTPUT_PATH, index=False)
    else:
        new_data.to_csv(OUTPUT_PATH, mode='a', header=False, index=False)

    print("\n Sonuç kaydedildi!")

def clean_dataframe(df, required_cols):
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=required_cols, how='all')
    df = df[df["understanding_score"].notna()]

    return df

def calculate_metrics():
    if not os.path.exists(OUTPUT_PATH):
        return

    df = pd.read_csv(OUTPUT_PATH, on_bad_lines='skip')

    if df.empty:
        print(" Veri yok.")
        return

    required_cols = [
        "understanding_score",
        "usability_score",
        "trust_score",
        "decision_score",
        "prediction_score"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    df = clean_dataframe(df, required_cols)

    if df.empty:
        print(" Geçerli veri yok.")
        return

    df[required_cols] = df[required_cols].fillna(0)

    understanding = df["understanding_score"].mean()
    trust = df["trust_score"].mean()
    usability = df["usability_score"].mean()
    decision = df["decision_score"].mean()
    accuracy = df["prediction_score"].mean()

    #  DOĞRU FINAL SCORE
    final_score = (
        0.25 * understanding +
        0.25 * trust +
        0.20 * usability +
        0.15 * decision +
        0.15 * accuracy
    )

    metrics = {
        "Anlaşılabilirlik": understanding,
        "Model Güveni": trust,
        "Kullanılabilirlik": usability,
        "Karar Güveni": decision,
        "Tahmin Doğruluğu": accuracy,
        "Final AI Score": final_score
    }

    metrics_df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
    metrics_df.to_csv(METRICS_PATH, index=False)

    print("\n GÜNCEL METRİKLER:")
    print(metrics_df)

    print(f"\n FINAL AI SCORE: {round(final_score,2)} / 10")

def analyze_results():
    if not os.path.exists(OUTPUT_PATH):
        return

    df = pd.read_csv(OUTPUT_PATH, on_bad_lines='skip')

    if df.empty:
        print(" Veri bulunamadı.")
        return

    required_cols = [
        "understanding_score",
        "usability_score",
        "trust_score",
        "decision_score"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    df = clean_dataframe(df, required_cols)

    if df.empty:
        print(" Analiz için veri yok.")
        return

    df[required_cols] = df[required_cols].fillna(0)

    print("\n KULLANICI TEST SONUÇLARI\n")

    print(" Anlaşılabilirlik:", round(df["understanding_score"].mean(), 2))
    print(" Model Güveni:", round(df["trust_score"].mean(), 2))
    print(" Kullanılabilirlik:", round(df["usability_score"].mean(), 2))
    print(" Karar Güveni:", round(df["decision_score"].mean(), 2))

    print("\n TEST ÖZETİ")
    print(f"Toplam kullanıcı: {len(df)}")

def main():
    print(" USER TESTING BAŞLATILIYOR...")

    if not os.path.exists(DATA_PATH):
        print(" predictions.csv bulunamadı.")
        return

    df = pd.read_csv(DATA_PATH)
    df["predicted_band"] = df["predicted_band"].astype(str).str.upper().str.strip()

    try:
        for i in range(10):
            print(f"\n Kullanıcı {i+1}")

            sample = df.sample(1).iloc[0]

            print_customer_analysis(sample)
            print_lime_explanation(sample)

            try:
                q1, q2, q3, q4, q5 = ask_questions()
                save_result(q1, q2, q3, q4, q5, sample["predicted_band"])
            except SystemExit:
                print(" Kullanıcı erken çıktı, veri kaydedilmedi.")
                break

    except KeyboardInterrupt:
        print("\n CTRL+C ile durduruldu.")

    finally:
        calculate_metrics()
        analyze_results()
        print("\n Test tamamlandı.\n")

if __name__ == "__main__":
    main()