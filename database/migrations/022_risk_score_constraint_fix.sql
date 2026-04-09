-- 022_risk_score_constraint_fix.sql

-- prediction_history
ALTER TABLE prediction_history
DROP CONSTRAINT IF EXISTS prediction_history_risk_score_check;

ALTER TABLE prediction_history
ADD CONSTRAINT prediction_history_risk_score_check
CHECK (risk_score BETWEEN 0 AND 1);


-- engineered_features
ALTER TABLE engineered_features
DROP CONSTRAINT IF EXISTS risk_score_range;

ALTER TABLE engineered_features
ADD CONSTRAINT risk_score_range
CHECK (risk_score BETWEEN 0 AND 1);