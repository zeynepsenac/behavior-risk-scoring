-- 05_income_risk_analysis.sql
SELECT 
    CASE 
        WHEN risk_score < 40 THEN 'Low Risk'
        WHEN risk_score BETWEEN 40 AND 70 THEN 'Medium Risk'
        ELSE 'High Risk'
    END AS risk_category,
    AVG(monthly_income) AS average_income
FROM engineered_customers
GROUP BY risk_category
ORDER BY average_income DESC;