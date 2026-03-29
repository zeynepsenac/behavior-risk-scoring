-- ensure risk_score cannot be null

BEGIN;

UPDATE engineered_features
SET risk_score = 0
WHERE risk_score IS NULL;

ALTER TABLE engineered_features
ALTER COLUMN risk_score SET NOT NULL;

COMMIT;