import pandas as pd
import os
import matplotlib.pyplot as plt

DATA_PATH = "reports/user_test_results.csv"
OUTPUT_IMG = "reports/user_test_chart.png"


# VERİ OKUMA

if not os.path.exists(DATA_PATH):
    print(" Veri bulunamadı.")
    exit()

df = pd.read_csv(DATA_PATH)

if df.empty:
    print(" Veri boş.")
    exit()

print("\n KULLANICI TEST SONUÇLARI\n")


#  Ortalama Açıklama / Anlaşılabilirlik

if "score" in df.columns:
    understanding = df["score"].mean()
    print(" Ortalama Açıklama Skoru:", round(understanding, 2))
elif "understanding_score" in df.columns:
    understanding = df["understanding_score"].mean()
    print(" Anlaşılabilirlik Skoru:", round(understanding, 2))
else:
    understanding = None


#  Anlaşılabilirlik Dağılımı

if "understood" in df.columns:
    print("\n Anlaşılma Dağılımı (%):")
    print((df["understood"].value_counts(normalize=True) * 100).round(2))


#  Doğru Tahmin / Güven

if "prediction" in df.columns and "prediction_score" not in df.columns:
    correct = (df["prediction"] == "MEDIUM").mean() * 100
    print(f"\n Doğru Risk Tahmin Oranı: %{round(correct,2)}")
    trust = correct / 10
elif "prediction_score" in df.columns:
    trust = df["prediction_score"].mean()
    print(f"\n Güven Skoru (ortalama): {round(trust,2)} / 10")
else:
    trust = None


#  Kullanılabilirlik

if "usability_score" in df.columns:
    usability = df["usability_score"].mean()
    print(f"\n Kullanılabilirlik Skoru: {round(usability,2)} / 10")
else:
    usability = None


#  GENEL ÖZET

print("\n GENEL DEĞERLENDİRME")

if understanding is not None:
    print(f"- Anlaşılabilirlik: {round(understanding,2)} / 10")

if trust is not None:
    print(f"- Model Güveni: {round(trust,2)} / 10")

if usability is not None:
    print(f"- Kullanılabilirlik: {round(usability,2)} / 10")


#  GRAFİK OLUŞTURMA

metrics = {}

if understanding is not None:
    metrics["Anlaşılabilirlik"] = understanding
if trust is not None:
    metrics["Güven"] = trust
if usability is not None:
    metrics["Kullanılabilirlik"] = usability

if len(metrics) > 0:
    labels = list(metrics.keys())
    values = list(metrics.values())

    plt.figure()
    plt.bar(labels, values)

    #  BAŞLIK
    plt.title("Kullanıcı Deneyimi Değerlendirme Sonuçları")

    plt.xlabel("Metrikler")
    plt.ylabel("Skor (0-10)")

    os.makedirs("reports", exist_ok=True)
    plt.savefig(OUTPUT_IMG)

    print(f"\n Grafik kaydedildi: {OUTPUT_IMG}")

    plt.close()
else:
    print(" Grafik oluşturulamadı (veri eksik).")