-- STEP 2: Disable sequential scan (testing only)

SET enable_seqscan = OFF;

EXPLAIN ANALYZE
SELECT *
FROM engineered_customers
WHERE risk_band = 'High'
ORDER BY risk_score DESC;


-- STEP 3: Restore planner settings

SET enable_seqscan = ON;