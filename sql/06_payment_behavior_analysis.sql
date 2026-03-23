-- 06_payment_behavior_analysis.sql
SELECT 
    AVG(bill_payment_delay_avg) AS average_payment_delay,
    AVG(missed_payments_6m) AS average_missed_payments
FROM engineered_customers;