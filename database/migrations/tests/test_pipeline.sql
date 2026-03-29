\echo '=== DB PIPELINE TEST STARTED ==='

-- ==========================================
-- ACTIVE MODEL REGISTRY (ALWAYS FIRST)
-- ==========================================

\echo '--- Setting active model ---'

UPDATE model_registry
SET is_active = FALSE;

INSERT INTO model_registry(
    model_version,
    model_name,
    is_active
)
VALUES (
    'v2.0',
    'xgboost',
    TRUE
)
ON CONFLICT (model_version)
DO UPDATE SET is_active = TRUE;

-- ==========================================
-- TABLE STATE CHECK
-- ==========================================

SELECT COUNT(*) AS customer_count
FROM engineered_customers;

-- ==========================================
-- TEST CUSTOMER INSERT
-- ==========================================

INSERT INTO engineered_customers (
    name,
    risk_score,
    risk_band
)
VALUES (
    'Test Customer',
    0.82,
    'High'
);

-- ==========================================
-- TRIGGER RESULT CHECK
-- ==========================================

SELECT
    prediction_id,
    customer_id,
    risk_score,
    risk_band,
    model_version,
    prediction_time
FROM prediction_history
ORDER BY prediction_id DESC
LIMIT 5;

-- ==========================================
-- MATERIALIZED VIEW TEST
-- ==========================================

REFRESH MATERIALIZED VIEW risk_portfolio_summary;

SELECT *
FROM risk_portfolio_summary;

-- ==========================================
-- UPDATED_AT TEST (REAL CHANGE)
-- ==========================================

UPDATE engineered_customers
SET risk_score = risk_score + 0.01
WHERE customer_id = 1;

SELECT
    customer_id,
    updated_at
FROM engineered_customers
WHERE customer_id = 1;

\echo '=== DB PIPELINE TEST FINISHED ==='