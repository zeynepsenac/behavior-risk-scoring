SELECT
    risk_band,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS percentage
FROM engineered_customers
GROUP BY risk_band;