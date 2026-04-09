BEGIN;

--------------------------------------------------
-- 0️⃣ SAFE RESET (VIEW / TABLE ambiguity fix)
--------------------------------------------------

-- engineered_customers_dataset (VIEW olabilir)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.views
        WHERE table_name = 'engineered_customers_dataset'
    ) THEN
        EXECUTE 'DROP VIEW engineered_customers_dataset CASCADE';
    END IF;
END $$;


-- engineered_customers (VIEW veya TABLE olabilir)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.views
        WHERE table_name = 'engineered_customers'
    ) THEN
        EXECUTE 'DROP VIEW engineered_customers CASCADE';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'engineered_customers'
    ) THEN
        EXECUTE 'DROP TABLE engineered_customers CASCADE';
    END IF;
END $$;


--------------------------------------------------
-- 1️⃣ FK FIX
--------------------------------------------------

ALTER TABLE IF EXISTS prediction_history
DROP CONSTRAINT IF EXISTS fk_customer;

ALTER TABLE prediction_history
ADD CONSTRAINT fk_customer
FOREIGN KEY (customer_id)
REFERENCES customers(customer_id);


--------------------------------------------------
-- 2️⃣ FEATURE STORE REBUILD
--------------------------------------------------

DROP TABLE IF EXISTS engineered_features CASCADE;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'engineered_customers_backup'
    ) THEN

        EXECUTE $SQL$
            CREATE TABLE engineered_features AS
            SELECT
                customer_id,
                payment_discipline_score,
                income_stability_index,
                financial_resilience_score,
                risk_score,
                risk_band,
                updated_at AS created_at
            FROM engineered_customers_backup
        $SQL$;

    ELSE

        -- ✅ BURASI ANA FIX
        RAISE NOTICE 'engineered_customers_backup not found - empty feature store created';

        EXECUTE $SQL$
            CREATE TABLE engineered_features (
                customer_id INT,
                payment_discipline_score FLOAT,
                income_stability_index FLOAT,
                financial_resilience_score FLOAT,
                risk_score FLOAT,
                risk_band TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        $SQL$;

    END IF;
END $$;


--------------------------------------------------
-- 3️⃣ DATA NORMALIZATION
--------------------------------------------------

UPDATE engineered_features
SET risk_score =
    CASE
        WHEN risk_score < 0 THEN 0
        WHEN risk_score > 1 THEN 1
        ELSE risk_score
    END;

UPDATE engineered_features
SET risk_score = 0
WHERE risk_score IS NULL;

UPDATE engineered_features
SET risk_score = 0
WHERE risk_score != risk_score;


--------------------------------------------------
-- 4️⃣ SEMANTIC VIEW
--------------------------------------------------

CREATE VIEW engineered_customers AS
SELECT
    c.customer_id,
    c.created_at,
    ef.payment_discipline_score,
    ef.income_stability_index,
    ef.financial_resilience_score,
    ef.risk_score,
    ef.risk_band,
    ef.created_at AS feature_created_at
FROM customers c
JOIN engineered_features ef
ON c.customer_id = ef.customer_id;


--------------------------------------------------
-- 5️⃣ INDEXES
--------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_feat_risk_band
ON engineered_features(risk_band);

CREATE INDEX IF NOT EXISTS idx_feat_risk_score
ON engineered_features(risk_score);

CREATE INDEX IF NOT EXISTS idx_feat_risk_band_score
ON engineered_features(risk_band, risk_score DESC);


--------------------------------------------------
-- 6️⃣ RISK CONSTRAINT
--------------------------------------------------

ALTER TABLE engineered_features
DROP CONSTRAINT IF EXISTS chk_risk_score;

ALTER TABLE engineered_features
ADD CONSTRAINT chk_risk_score
CHECK (risk_score BETWEEN 0 AND 1)
NOT VALID;

ALTER TABLE engineered_features
VALIDATE CONSTRAINT chk_risk_score;


--------------------------------------------------
-- 7️⃣ DATASET VIEW
--------------------------------------------------

CREATE OR REPLACE VIEW engineered_customers_dataset AS
SELECT * FROM engineered_customers;

COMMIT;