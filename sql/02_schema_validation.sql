-- 02_schema_validation.sql
SELECT 
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'engineered_customers';