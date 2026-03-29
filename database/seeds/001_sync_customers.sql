-- Sync customer identities from raw dataset

INSERT INTO customers(customer_id)
SELECT customer_id
FROM synthetic_customers
ON CONFLICT (customer_id) DO NOTHING;