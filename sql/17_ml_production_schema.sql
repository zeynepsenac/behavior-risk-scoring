-- ==========================================
-- ML PRODUCTION TABLES
-- ==========================================

CREATE TABLE IF NOT EXISTS prediction_history (
    prediction_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    risk_score NUMERIC(5,2) NOT NULL,
    risk_band VARCHAR(10) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);