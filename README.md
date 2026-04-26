# 🧠 Behavior Risk Scoring System

![Project Banner](https://img.shields.io/badge/AI-Risk%20Scoring-blue?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=for-the-badge\&logo=docker)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?style=for-the-badge\&logo=fastapi)
![ML](https://img.shields.io/badge/Machine%20Learning-XGBoost-orange?style=for-the-badge)

---

## 🚀 Proje Hakkında

**Behavior Risk Scoring System**, kullanıcı davranış verilerini analiz ederek bireylerin risk seviyesini tahmin eden ve bu tahmini **açıklanabilir yapay zeka (LIME)** ile destekleyen uçtan uca bir veri bilimi ve backend sistemidir.

Bu proje;

* Veri işleme
* Makine öğrenmesi
* Veri gizliliği (KVKK / GDPR)
* API geliştirme
* Docker containerization

bileşenlerini tek bir sistemde birleştirir.

---

## 🎯 Temel Amaç

Kullanıcı davranışlarını analiz ederek:

* 📊 Risk skorunu tahmin etmek
* 🧠 Tahminlerin nedenlerini açıklamak
* 🔐 Veriyi anonimleştirerek gizliliği korumak
* ⚡ Gerçek zamanlı API üzerinden sonuç sunmak

---

## 🧱 Sistem Mimarisi

```
Synthetic Data
      ↓
Feature Engineering
      ↓
PostgreSQL Database
      ↓
ML Model Training
      ↓
Risk Prediction Engine
      ↓
LIME Explainability Layer
      ↓
FastAPI Service
      ↓
Reports & Visualization
```

---
graph TD


## 📁 Proje Yapısı

```
BEHAVIOR-RISK-SCORING/
│
├── data/            → Ham ve işlenmiş veriler
├── models/          → ML modelleri ve scaler
├── reports/         → Grafikler ve analiz çıktıları
├── scripts/         → Veri işleme pipeline
├── src/             → API + model + privacy layer
├── sql/             → SQL sorguları
├── docker/          → Container yapılandırmaları
├── tests/           → Test scriptleri
├── utils/           → Yardımcı fonksiyonlar
```

---

## ⚙️ Özellikler

### 🧠 Machine Learning

* Risk skoru tahmini
* Feature engineering pipeline
* Model performans metrikleri

### 🔍 Explainable AI

* LIME tabanlı açıklamalar
* Karar nedenlerinin görselleştirilmesi

### 🔐 Privacy Layer

* K-Anonymity
* L-Diversity
* Veri anonimleştirme

### 🐳 DevOps

* Docker Compose desteği
* PostgreSQL entegrasyonu
* Otomatik schema migration

### 🌐 API

* FastAPI tabanlı REST API
* Swagger UI desteği

---

## 🚀 Kurulum

### 📦 Clone

```bash
git clone https://github.com/YOUR_USERNAME/behavior-risk-scoring.git
cd behavior-risk-scoring
```

---

### 🐳 Docker ile Çalıştır (Önerilen)

```bash
docker compose up --build
```

---

## 🌍 API Erişim

| Servis     | URL                                                      |
| ---------- | -------------------------------------------------------- |
| Swagger UI | [http://localhost:8000/docs](http://localhost:8000/docs) |
| API Base   | [http://localhost:8000](http://localhost:8000)           |

---

## 📊 Veri Akışı

```
Raw Synthetic Data
      ↓
Anonymization Layer
      ↓
Feature Engineering
      ↓
Database Storage
      ↓
Model Prediction
      ↓
Explainability (LIME)
      ↓
Visualization & Reports
```

---

## 📈 Model Performansı

* Anlaşılabilirlik: 8.14 / 10
* Kullanılabilirlik: 6.29 / 10
* Model Güveni: 6.86 / 10
* Karar Güveni: 8.43 / 10
* Final AI Score: 6.59 / 10

---

## 🛑 Servisleri Durdurma

```bash
docker compose down
```

---

## 🔄 Sıfırlama

```bash
docker compose down -v
docker compose up --build
```

---

## 👩‍💻 Geliştirici

**Software Engineering Project — Behavior Risk Scoring System**

---

## ⭐ Not

Bu proje tamamen **sentetik veri** kullanır ve gerçek kullanıcı verisi içermez. KVKK & GDPR uyumludur.

