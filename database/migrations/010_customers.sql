CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS synthetic_customers (
    customer_id INT PRIMARY KEY
        REFERENCES customers(customer_id),

    monthly_income NUMERIC(12,2),
    income_variance NUMERIC(5,3),
    bill_payment_delay_avg NUMERIC(5,2),
    missed_payments_6m INT,
    spending_ratio NUMERIC(4,2),
    savings_rate NUMERIC(4,2),
    employment_duration_months INT,
    account_age_months INT
);