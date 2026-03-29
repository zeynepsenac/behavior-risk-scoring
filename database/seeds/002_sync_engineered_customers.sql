INSERT INTO engineered_customers (
    customer_id,
    risk_score,
    risk_band
)
SELECT
    customer_id,
    risk_score,
    risk_band
FROM engineered_features
ON CONFLICT (customer_id) DO UPDATE
SET
    risk_score = EXCLUDED.risk_score,
    risk_band = EXCLUDED.risk_band;