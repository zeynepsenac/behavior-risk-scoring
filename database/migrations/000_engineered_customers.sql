CREATE TABLE IF NOT EXISTS engineered_customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    risk_score NUMERIC,
    risk_band VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);