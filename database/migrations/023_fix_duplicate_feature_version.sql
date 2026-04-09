-- remove duplicated column if exists

ALTER TABLE prediction_history
DROP COLUMN IF EXISTS feature_version_1;