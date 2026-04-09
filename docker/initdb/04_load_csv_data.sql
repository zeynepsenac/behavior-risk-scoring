DROP TABLE IF EXISTS staging_engineered_features;
DROP TABLE IF EXISTS staging_synthetic_customers;

-- ===============================
-- STAGING TABLES
-- ===============================

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

CREATE TABLE IF NOT EXISTS staging_engineered_features (
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
    risk_band TEXT,
    payment_discipline_score NUMERIC,
    income_stability_index NUMERIC,
    financial_resilience_score NUMERIC
);

-- ===============================
-- LOAD synthetic_customers.csv
-- ===============================

COPY staging_synthetic_customers
FROM '/data/synthetic_customers.csv'
DELIMITER ','
CSV HEADER;

-- FK parent safety
INSERT INTO customers(customer_id)
SELECT DISTINCT customer_id
FROM staging_synthetic_customers
ON CONFLICT DO NOTHING;

-- ===============================
-- STAGING → synthetic_customers
-- ===============================

INSERT INTO synthetic_customers(
    customer_id,
    monthly_income,
    income_variance,
    bill_payment_delay_avg,
    missed_payments_6m,
    spending_ratio,
    savings_rate,
    employment_duration_months,
    account_age_months
)
SELECT
    customer_id,
    monthly_income,
    income_variance,
    bill_payment_delay_avg,
    missed_payments_6m,
    spending_ratio,
    savings_rate,
    employment_duration_months,
    account_age_months
FROM staging_synthetic_customers
ON CONFLICT (customer_id) DO UPDATE SET
    monthly_income = EXCLUDED.monthly_income,
    income_variance = EXCLUDED.income_variance,
    bill_payment_delay_avg = EXCLUDED.bill_payment_delay_avg,
    missed_payments_6m = EXCLUDED.missed_payments_6m,
    spending_ratio = EXCLUDED.spending_ratio,
    savings_rate = EXCLUDED.savings_rate,
    employment_duration_months = EXCLUDED.employment_duration_months,
    account_age_months = EXCLUDED.account_age_months;

-- ===============================
-- LOAD engineered_customers.csv
-- ===============================

COPY staging_engineered_features
FROM '/data/engineered_customers.csv'
DELIMITER ','
CSV HEADER;

-- FK safety
INSERT INTO customers(customer_id)
SELECT DISTINCT customer_id
FROM staging_engineered_features
ON CONFLICT DO NOTHING;

-- ===============================
-- STAGING → engineered_features
-- ===============================

INSERT INTO engineered_features(
    customer_id,
    payment_discipline_score,
    income_stability_index,
    financial_resilience_score,
    risk_score,
    risk_band
)
SELECT
    customer_id,
    payment_discipline_score,
    income_stability_index,
    financial_resilience_score,
    CASE
        WHEN risk_score > 1 THEN risk_score / 100.0
        ELSE risk_score
    END,
    NULL::risk_level
FROM staging_engineered_features
WHERE risk_band IN ('Low','Medium','High')

ON CONFLICT (customer_id)
DO UPDATE SET
    payment_discipline_score = EXCLUDED.payment_discipline_score,
    income_stability_index = EXCLUDED.income_stability_index,
    financial_resilience_score = EXCLUDED.financial_resilience_score,
    risk_score = EXCLUDED.risk_score,
    risk_band = EXCLUDED.risk_band;

-- ===============================
-- OPTIONAL updated_at SAFE UPDATE
-- (only if column exists)
-- ===============================

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='engineered_features'
        AND column_name='updated_at'
    ) THEN
        EXECUTE '
            UPDATE engineered_features
            SET updated_at = NOW()
        ';
    END IF;
END $$;

-- ===============================
-- CLEAN STAGING
-- ===============================

TRUNCATE staging_synthetic_customers;
TRUNCATE staging_engineered_features;