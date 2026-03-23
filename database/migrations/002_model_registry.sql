CREATE TABLE model_registry (
    model_version VARCHAR(20) PRIMARY KEY,
    model_name VARCHAR(50),
    trained_at TIMESTAMP,
    training_rows INT,
    mae NUMERIC(6,4),
    features JSONB,
    is_active BOOLEAN DEFAULT FALSE
);