-- 07_high_risk_customers_report.sql
SELECT 
    customer_id,
    risk_score,
    missed_payments_6m,
    spending_ratio,
    savings_rate
FROM engineered_customers
ORDER BY risk_score DESC
LIMIT 10;