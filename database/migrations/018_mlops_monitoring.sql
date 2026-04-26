-- Migration: 017_mlops_monitoring
-- Amaç: MLOps izleme (monitoring) özelliklerini eklemek
-- İçerik:
--  - Veri kayması (drift) izleme (PSI)
--  - Tahmin gecikmesi (latency) takibi
--  - Açıklanabilirlik (explainability) versiyonlama

--  Veri Kayması (Drift) İzleme
CREATE TABLE IF NOT EXISTS model_drift_metrics (
    metric_id SERIAL PRIMARY KEY,
    metric_date TIMESTAMP DEFAULT NOW(),
    feature_name TEXT NOT NULL,
    psi_score NUMERIC(6,4) NOT NULL
);

--  Tahmin Gecikmesi (Prediction Latency) Log Kayıtları
CREATE TABLE IF NOT EXISTS prediction_latency_log (
    latency_id SERIAL PRIMARY KEY,
    prediction_time TIMESTAMP DEFAULT NOW(),
    prediction_latency_ms INTEGER NOT NULL
);

--  Açıklanabilirlik (Explainability) Versiyonlama
ALTER TABLE prediction_history
ADD COLUMN IF NOT EXISTS explanation_version TEXT;