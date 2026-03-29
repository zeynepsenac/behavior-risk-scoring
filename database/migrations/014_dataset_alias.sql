-- engineered_customers.csv görünümü
CREATE OR REPLACE VIEW engineered_customers_dataset AS
SELECT *
FROM engineered_features;

-- synthetic_customers.csv görünümü
CREATE OR REPLACE VIEW synthetic_customers_dataset AS
SELECT *
FROM synthetic_customers;