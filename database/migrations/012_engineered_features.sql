-- =====================================================
-- ENGINEERED FEATURES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS engineered_features (

    customer_id INT PRIMARY KEY
        REFERENCES customers(customer_id),

    payment_discipline_score NUMERIC(5,2),
    income_stability_index NUMERIC(5,2),
    financial_resilience_score NUMERIC(5,2),

    risk_score NUMERIC(5,2),
    risk_band VARCHAR(20),

    -- PRODUCTION FIX
    -- feature_version artık table seviyesinde
    feature_version TEXT NOT NULL DEFAULT 'v1',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Risk band + score analytics index
CREATE INDEX IF NOT EXISTS idx_risk_band_score
ON engineered_features (risk_band, risk_score DESC);

-- Partial index for high risk queries
CREATE INDEX IF NOT EXISTS idx_high_risk
ON engineered_features (risk_score DESC)
WHERE risk_band = 'High';