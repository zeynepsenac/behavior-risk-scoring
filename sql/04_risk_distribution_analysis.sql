-- 04_risk_distribution_analysis.sql
SELECT 
    CASE 
        WHEN risk_score < 40 THEN 'Low Risk'
        WHEN risk_score BETWEEN 40 AND 70 THEN 'Medium Risk'
        ELSE 'High Risk'
    END AS risk_category,
    COUNT(*) AS customer_count
FROM engineered_customers
GROUP BY risk_category
ORDER BY customer_count DESC;