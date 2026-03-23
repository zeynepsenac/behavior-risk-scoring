-- 08_risk_percentile_analysis.sql

SELECT
    customer_id,
    risk_score,
    NTILE(5) OVER (ORDER BY risk_score DESC) AS risk_percentile_group
FROM engineered_customers;