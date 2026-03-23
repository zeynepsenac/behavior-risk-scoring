SELECT
    AVG(payment_discipline_score) AS avg_payment_discipline,
    AVG(income_stability_index) AS avg_income_stability,
    AVG(financial_resilience_score) AS avg_financial_resilience
FROM engineered_customers;