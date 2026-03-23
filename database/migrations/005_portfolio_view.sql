CREATE MATERIALIZED VIEW risk_portfolio_summary AS
SELECT
    risk_band,
    COUNT(*) AS customer_count,
    AVG(risk_score) AS avg_score
FROM engineered_customers
GROUP BY risk_band;