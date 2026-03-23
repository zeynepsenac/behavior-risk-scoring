CREATE OR REPLACE FUNCTION log_prediction()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO prediction_history(
        customer_id,
        risk_score,
        risk_band,
        model_version
    )
    VALUES (
        NEW.customer_id,
        NEW.risk_score,
        NEW.risk_band,
        'v1.0'
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_prediction
AFTER UPDATE OF risk_score
ON engineered_customers
FOR EACH ROW
EXECUTE FUNCTION log_prediction();