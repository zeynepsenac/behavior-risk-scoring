ALTER TABLE engineered_customers
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS '
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
';

DROP TRIGGER IF EXISTS trg_update_timestamp
ON engineered_customers;

CREATE TRIGGER trg_update_timestamp
BEFORE UPDATE ON engineered_customers
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();