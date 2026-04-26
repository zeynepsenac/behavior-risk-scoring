import hashlib
import pandas as pd
import os

#  SALT (env varsa onu kullan, yoksa default)
SALT = os.getenv("HASH_SALT", "kvkk_project_2026")

# Hashing is considered pseudonymization, NOT anonymization.
# It does not fully prevent re-identification due to potential linkability.
# True anonymity in this pipeline is achieved via:
# - k-anonymity
# - generalization of quasi-identifiers
#  HASH (pseudonymization - KVKK açısından tek başına anonimlik sağlamaz)
def hash_value(value):
    return hashlib.sha256((str(value) + SALT).encode()).hexdigest()

#  EMAIL MASK
# Amaç: Doğrudan tanımlayıcıyı kısmen gizlemek (masking)
def mask_email(email):
    if pd.isna(email):
        return email
    if "@" in str(email):
        name, domain = email.split("@")
        return name[0] + "***@" + domain
    return email

#  PHONE MASK
# Amaç: Kişisel veriyi kısmi olarak gizlemek
def mask_phone(phone):
    if pd.isna(phone):
        return phone
    phone = str(phone)
    if len(phone) < 5:
        return "****"
    return phone[:2] + "****" + phone[-3:]

#  AGE GENELLEŞTİRME
# Amaç: Yaş bilgisinden yeniden tanımlanabilirliği azaltmak
# Strateji: 5 yıllık aralıklarla gruplama
def generalize_age(age):
    if pd.isna(age):
        return age
    age = int(age)
    return f"{(age//5)*5}-{(age//5)*5 + 5}"

#  GELİR GENELLEŞTİRME
# Amaç: KVKK kapsamında yeniden tanımlanabilirliği azaltmak
# Strateji: 10k aralık ile privacy-utility dengesi sağlanır
def generalize_income(income):
    if pd.isna(income):
        return income
    income = int(income)
    return f"{(income//10000)*10000}-{(income//10000)*10000 + 10000}"

#  SPENDING GENELLEŞTİRME
# Amaç: Hassas davranış verisini bulanıklaştırmak
# Strateji: Yuvarlama ile noise reduction
def generalize_spending(ratio):
    if pd.isna(ratio):
        return ratio
    return round(float(ratio), 0)

#  ACCOUNT AGE GENELLEŞTİRME
# Amaç: Zamansal kimliklenebilirliği azaltmak
# Strateji: 60 aylık gruplama (temporal grouping)
def generalize_account_age(age):
    if pd.isna(age):
        return age
    age = int(age)
    return f"{(age//60)*60}-{(age//60)*60 + 60}"


def anonymize_dataframe(df: pd.DataFrame):
    df = df.copy()

    #  ID HASH (pseudonymization)
    if "customer_id" in df.columns:
        df["customer_id"] = df["customer_id"].apply(hash_value)

    #  EMAIL MASK
    if "email" in df.columns:
        df["email"] = df["email"].apply(mask_email)

    #  PHONE MASK
    if "phone" in df.columns:
        df["phone"] = df["phone"].apply(mask_phone)

    #  GENELLEŞTİRME (quasi-identifiers)
    if "monthly_income" in df.columns:
        df["monthly_income"] = df["monthly_income"].apply(generalize_income)

    if "spending_ratio" in df.columns:
        df["spending_ratio"] = df["spending_ratio"].apply(generalize_spending)

    if "account_age_months" in df.columns:
        df["account_age_months"] = df["account_age_months"].apply(generalize_account_age)

    #  AGE → age_group (direkt yaş kaldırılır)
    if "age" in df.columns:
        df["age_group"] = df["age"].apply(generalize_age)
        df = df.drop(columns=["age"])  # doğrudan tanımlayıcıyı kaldır

    #  EKSTRA GÜVENLİK: tamamen boş kolonları kaldır
    df = df.dropna(axis=1, how="all")

    return df