## Installation

python -m venv venv
source venv/bin/activate  # Windows için: .\venv\Scripts\Activate
pip install -r requirements.txt
## Synthetic Data

Synthetic data was generated using statistically controlled distributions
to simulate realistic financial behavior patterns.

No real customer data was used in this project.
All data is fully synthetic and compliant with KVKK and GDPR regulations.


Dataset is anonymized and contains no personally identifiable information (PII).
KVKK/GDPR compliant processing is applied.


Raw Data
synthetic_customers.csv
        │
        │ Data Loading
        ▼
PostgreSQL
customers (raw table)
        │
        │ Feature Engineering (Python)
        ▼
engineered_customers.csv
        │
        │ Database Loading
        ▼
PostgreSQL
engineered_customers (processed table)
        │
        │ SQL Analytics
        ▼
Risk Analysis Queries
        │
        ▼
Visualization / Reports



## Run Project

```bash
git clone REPO_LINK
cd behavior-risk-scoring
docker-compose up --build
```

Open:

http://localhost:8000/docs


# Behavior Risk Scoring API

A Dockerized FastAPI project that predicts customer behavioral risk scores using machine learning and explainable AI (LIME).

---

## 🚀 Project Overview

This project provides:

* Behavioral risk prediction API
* PostgreSQL database
* Automated schema creation
* LIME explainability integration
* Fully containerized environment using Docker

No local Python or PostgreSQL installation is required.

---

## 📦 Requirements

You only need:

* Docker Desktop
  https://www.docker.com/products/docker-desktop/

Make sure Docker Desktop is **running** before starting.

---

## ⚡ Quick Start (Recommended)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/behavior-risk-scoring.git
cd behavior-risk-scoring
```

---

### 2️⃣ Start the project

```bash
docker compose up --build
```

That’s it ✅

Docker will automatically:

* build the API image
* start PostgreSQL
* create database schema
* run migrations
* start FastAPI server

---

## 🌐 API Access

After startup:

Swagger Documentation:

```
http://localhost:8000/docs
```

API Base URL:

```
http://localhost:8000
```

---

## 🗄️ Services

| Service    | Port | Description |
| ---------- | ---- | ----------- |
| FastAPI    | 8000 | REST API    |
| PostgreSQL | 5432 | Database    |

---

## 🧱 Project Structure

```
behavior-risk-scoring/
│
├── src/
│   ├── api.py
│   ├── schemas.py
│   └── explain/
│       └── lime_explainer.py
│
├── database/
│   └── migrations.sql
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🛑 Stop Containers

```bash
docker compose down
```

---

## 🔄 Reset Database (Optional)

```bash
docker compose down -v
docker compose up --build
```

---

## 👩‍💻 Author

Software Engineering Project — Behavior Risk Scoring System
