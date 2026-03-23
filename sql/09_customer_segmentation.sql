-- 09_customer_segmentation.sql

SELECT
    CASE
        WHEN spending_ratio > 0.8 THEN 'High Spender'
        WHEN spending_ratio BETWEEN 0.5 AND 0.8 THEN 'Moderate Spender'
        ELSE 'Low Spender'
    END AS spending_segment,
    COUNT(*) AS customer_count
FROM engineered_customers
GROUP BY spending_segment
ORDER BY customer_count DESC;