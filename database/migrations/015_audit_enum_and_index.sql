DROP VIEW IF EXISTS engineered_customers_dataset;



-- 1. AUDIT COLUMN


ALTER TABLE prediction_history
ADD COLUMN IF NOT EXISTS created_by TEXT DEFAULT current_user;

UPDATE prediction_history
SET created_by = current_user
WHERE created_by IS NULL;

ALTER TABLE prediction_history
ALTER COLUMN created_by SET NOT NULL;





-- 3. ENUM CONVERSION


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'risk_level'
    ) THEN
        CREATE TYPE risk_level AS ENUM ('Low', 'Medium', 'High');
    END IF;
END$$;


ALTER TABLE engineered_features
ADD COLUMN IF NOT EXISTS risk_band_new risk_level;


--UPDATE engineered_features
--SET risk_band_new =
  --  CASE risk_band
    --    WHEN 'Low' THEN 'Low'::risk_level
      --  WHEN 'Medium' THEN 'Medium'::risk_level
        --WHEN 'High' THEN 'High'::risk_level
    --END;


ALTER TABLE engineered_features
DROP COLUMN IF EXISTS risk_band;

ALTER TABLE engineered_features
RENAME COLUMN risk_band_new TO risk_band;

ALTER TABLE engineered_features
ALTER COLUMN risk_band SET NOT NULL;


-- 4. ANALYTICS INDEX


CREATE INDEX IF NOT EXISTS idx_prediction_model_time
ON prediction_history(model_version, prediction_time DESC);


-- 5. RECREATE VIEW


CREATE VIEW engineered_customers_dataset AS
SELECT
    ec.customer_id,
    ef.risk_score,
    ef.risk_band,
    ef.feature_version
FROM engineered_customers ec
JOIN engineered_features ef
    ON ec.customer_id = ef.customer_id;