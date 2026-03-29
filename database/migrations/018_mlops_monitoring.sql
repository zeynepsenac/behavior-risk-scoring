-- Migration: 017_mlops_monitoring
-- Purpose: Add MLOps monitoring capabilities
-- Includes:
--  - Drift monitoring (PSI)
--  - Prediction latency tracking
--  - Explainability versioning

---------------------------------------------------
-- 1️⃣ Drift Monitoring
---------------------------------------------------
CREATE TABLE IF NOT EXISTS model_drift_metrics (
    metric_id SERIAL PRIMARY KEY,
    metric_date TIMESTAMP DEFAULT NOW(),
    feature_name TEXT NOT NULL,
    psi_score NUMERIC(6,4) NOT NULL
);

---------------------------------------------------
-- 2️⃣ Prediction Latency Log
---------------------------------------------------
CREATE TABLE IF NOT EXISTS prediction_latency_log (
    latency_id SERIAL PRIMARY KEY,
    prediction_time TIMESTAMP DEFAULT NOW(),
    prediction_latency_ms INTEGER NOT NULL
);

---------------------------------------------------
-- 3️⃣ Explainability Version
---------------------------------------------------
ALTER TABLE prediction_history
ADD COLUMN IF NOT EXISTS explanation_version TEXT;