-- ==========================================
-- Update prediction trigger to use active model
-- ==========================================

CREATE OR REPLACE FUNCTION log_prediction()
RETURNS TRIGGER AS $$
DECLARE active_model TEXT;
BEGIN
    -- aktif modeli registry'den al
    SELECT model_version
    INTO active_model
    FROM model_registry
    WHERE is_active = TRUE
    LIMIT 1;

    -- eğer aktif model yoksa hata üret
    IF active_model IS NULL THEN
        RAISE EXCEPTION 'No active model found in model_registry';
    END IF;

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
        active_model
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;