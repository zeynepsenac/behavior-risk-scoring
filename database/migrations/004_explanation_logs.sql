CREATE TABLE IF NOT EXISTS explanation_logs (
    explanation_id BIGSERIAL PRIMARY KEY,
    prediction_id BIGINT,
    feature_importance JSONB,
    rules_triggered JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE explanation_logs
DROP CONSTRAINT IF EXISTS fk_prediction;

ALTER TABLE explanation_logs
ADD CONSTRAINT fk_prediction
FOREIGN KEY (prediction_id)
REFERENCES prediction_history(prediction_id);