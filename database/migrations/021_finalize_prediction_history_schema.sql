-- =========================================
-- FINALIZE prediction_history SCHEMA
-- Adds ML observability + lineage tracking
-- =========================================

-- 1️⃣ Add missing columns safely
ALTER TABLE prediction_history
ADD COLUMN IF NOT EXISTS created_by TEXT,
ADD COLUMN IF NOT EXISTS dataset_version TEXT,
ADD COLUMN IF NOT EXISTS pipeline_run_id TEXT,
ADD COLUMN IF NOT EXISTS explanation_version TEXT;

-- 2️⃣ Add professional defaults
ALTER TABLE prediction_history
ALTER COLUMN created_by SET DEFAULT 'ml_pipeline';

ALTER TABLE prediction_history
ALTER COLUMN dataset_version SET DEFAULT 'dataset_v1';