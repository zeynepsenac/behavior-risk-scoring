-- 10_financial_resilience_ranking.sql

SELECT
    customer_id,
    financial_resilience_score
FROM engineered_customers
ORDER BY financial_resilience_score DESC
LIMIT 10;