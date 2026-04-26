import pandas as pd

df = pd.read_csv("data/user_form_responses.csv")

# kolon isimlerini temizle (KRİTİK)
df.columns = df.columns.str.strip()

print("\n GOOGLE FORM ANALİZİ\n")


#  Anlaşılabilirlik

understanding_col = "Bu risk skorunun neden oluştuğunu anladınız mı?"

mapping = {
    "Evet": 10,
    "Kısmen": 7,
    "Hayır": 3
}

understanding_score = df[understanding_col].map(mapping).mean()

print(" Anlaşılabilirlik:", round(understanding_score, 2), "/10")


#  Açıklama kalitesi (FIX)

explanation_col = "Açıklamayı ne kadar yeterli buldunuz?"

# string → numeric dönüşüm
df[explanation_col] = pd.to_numeric(df[explanation_col], errors='coerce')

# NaN temizleme
df = df.dropna(subset=[explanation_col])

explanation_score = df[explanation_col].mean() * 2

print(" Açıklama Kalitesi:", round(explanation_score, 2), "/10")


#  Model güveni (tahmin doğruluğu)

prediction_col = "Sizce bu müşteri hangi risk grubundadır?"

correct = (df[prediction_col].str.upper() == "MEDIUM").mean() * 10

print(" Model Güveni:", round(correct, 2), "/10")


#  Karar verilebilirlik (FIX)


# kolon adını otomatik bul (birebir eşleşme sorunu çözülür)
decision_col = [col for col in df.columns if "finansal" in col.lower()][0]

decision_map = {
    "Evet": 10,
    "Emin Değilim": 5,
    "Hayır": 2
}

decision_score = df[decision_col].map(decision_map).mean()

print(" Karar Kullanılabilirliği:", round(decision_score, 2), "/10")


# GENEL SKOR

final_score = (understanding_score + explanation_score + correct + decision_score) / 4

print("\n GENEL SKOR:", round(final_score, 2), "/10")