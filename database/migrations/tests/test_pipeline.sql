\echo '=== DB PIPELINE TEST STARTED ==='

-- tablo boş mu
SELECT COUNT(*) FROM engineered_customers;

-- test müşteri ekle
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

-- trigger test
SELECT * FROM prediction_history;

-- materialized view refresh
REFRESH MATERIALIZED VIEW risk_portfolio_summary;

SELECT * FROM risk_portfolio_summary;

-- updated_at trigger test
UPDATE engineered_customers
SET risk_score = risk_score
WHERE customer_id = 1;

SELECT customer_id, updated_at
FROM engineered_customers
WHERE customer_id = 1;

\echo '=== DB PIPELINE TEST FINISHED ==='