CREATE TABLE IF NOT EXISTS engineered_customers (
    customer_id INT PRIMARY KEY,

    monthly_income NUMERIC(12,2),
    income_variance NUMERIC(5,3),

    bill_payment_delay_avg NUMERIC(5,2),
    missed_payments_6m INT,

    spending_ratio NUMERIC(4,2),
    savings_rate NUMERIC(4,2),

    employment_duration_months INT,
    account_age_months INT,

    payment_discipline_score NUMERIC(5,2),
    income_stability_index NUMERIC(5,2),
    financial_resilience_score NUMERIC(5,2),

    risk_score NUMERIC(5,2),
    risk_band VARCHAR(20)
);

CREATE INDEX IF NOT EXISTS idx_risk_band
ON engineered_customers(risk_band);

CREATE INDEX IF NOT EXISTS idx_risk_score
ON engineered_customers(risk_score);

CREATE INDEX IF NOT EXISTS idx_risk_band_score
ON engineered_customers(risk_band, risk_score DESC);