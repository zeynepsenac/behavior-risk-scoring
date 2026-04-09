-- FINAL prediction trigger (project closing migration)

DROP FUNCTION IF EXISTS log_prediction CASCADE;

CREATE OR REPLACE FUNCTION log_prediction()
RETURNS TRIGGER AS $$
DECLARE
    active_model TEXT := 'v1';
    active_dataset TEXT := 'dataset_v1';
    calculated_risk NUMERIC;
    calculated_band TEXT;
BEGIN

    -- normalize features (0–100 → 0–1)
    calculated_risk :=
        (
            (NEW.payment_discipline_score / 100.0) * 0.4 +
            (NEW.income_stability_index / 100.0) * 0.3 +
            (NEW.financial_resilience_score / 100.0) * 0.3
        );

    -- risk band calculation
    IF calculated_risk >= 0.7 THEN
        calculated_band := 'High';
    ELSIF calculated_risk >= 0.4 THEN
        calculated_band := 'Medium';
    ELSE
        calculated_band := 'Low';
    END IF;

    INSERT INTO prediction_history(
        customer_id,
        risk_score,
        risk_band,
        model_version,
        prediction_time,
        created_by,
        dataset_version,
        pipeline_run_id,
        created_at
    )
    VALUES (
        NEW.customer_id,
        calculated_risk,
        calculated_band,
        active_model,
        NOW(),
        'ml_pipeline',
        active_dataset,
        gen_random_uuid(),
        NOW()
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trigger_prediction ON engineered_features;

CREATE TRIGGER trigger_prediction
AFTER INSERT OR UPDATE
ON engineered_features
FOR EACH ROW
EXECUTE FUNCTION log_prediction();