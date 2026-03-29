ALTER TABLE prediction_history
ADD COLUMN dataset_version TEXT,
ADD COLUMN pipeline_run_id UUID;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE prediction_history
ALTER COLUMN pipeline_run_id
SET DEFAULT gen_random_uuid();