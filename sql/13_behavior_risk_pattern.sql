SELECT
    missed_payments_6m,
    AVG(risk_score) AS average_risk_score
FROM engineered_customers
GROUP BY missed_payments_6m
ORDER BY missed_payments_6m;