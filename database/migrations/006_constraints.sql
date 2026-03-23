DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'chk_risk_score'
    ) THEN
        ALTER TABLE engineered_customers
        ADD CONSTRAINT chk_risk_score
        CHECK (risk_score BETWEEN 0 AND 100);
    END IF;
END $$;