CREATE TABLE IF NOT EXISTS staging_synthetic_customers (
    customer_id INT,
    monthly_income NUMERIC,
    income_variance NUMERIC,
    bill_payment_delay_avg NUMERIC,
    missed_payments_6m INT,
    spending_ratio NUMERIC,
    savings_rate NUMERIC,
    employment_duration_months INT,
    account_age_months INT,
    risk_score NUMERIC,
    risk_band TEXT
);