CREATE OR REPLACE FUNCTION log_prediction()
RETURNS TRIGGER AS $$
BEGIN

    INSERT INTO prediction_history (
        customer_id,
        risk_score,
        risk_band,
        model_version,
        created_by,
        dataset_version
    )
    VALUES (
        NEW.customer_id,
        NEW.risk_score,
        NEW.risk_band,
        'v1',
        'ml_pipeline',
        'dataset_v1'
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;