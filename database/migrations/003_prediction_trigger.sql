CREATE OR REPLACE FUNCTION log_prediction() 
RETURNS TRIGGER
LANGUAGE plpgsql
AS $func$
DECLARE
    active_model TEXT;
    active_dataset TEXT := 'dataset_v1';
BEGIN

  --  Sonsuz tetikleyici döngüsüne karşı koruma
    IF TG_TABLE_NAME <> 'engineered_features' THEN
        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        END IF;
        RETURN NEW;
    END IF;

    -- aktif modeli al
    SELECT model_version
    INTO active_model
    FROM model_registry
    WHERE is_active = TRUE
    LIMIT 1;

    -- fallback
    IF active_model IS NULL THEN
        active_model := 'unknown_model';
    END IF;


  
    -- DELETE AUDIT
    
    IF TG_OP = 'DELETE' THEN
        INSERT INTO prediction_history (
            customer_id,
            risk_score,
            model_version,
            feature_version,
            dataset_version,
            deleted_at
        )
        VALUES (
            OLD.customer_id,
            OLD.risk_score,
            active_model,
            OLD.feature_version,
            active_dataset,
            NOW()
        );

        RETURN OLD;
    END IF;


 
    -- UPDATE CHANGE CHECK
 
    IF TG_OP = 'UPDATE' THEN
        IF NEW.risk_score IS NOT DISTINCT FROM OLD.risk_score
           AND NEW.feature_version IS NOT DISTINCT FROM OLD.feature_version
        THEN
            RETURN NEW;
        END IF;
    END IF;


  
    -- INSERT & UPDATE AUDIT LOG
  
    INSERT INTO prediction_history (
        customer_id,
        risk_score,
        model_version,
        feature_version,
        dataset_version
    )
    VALUES (
        NEW.customer_id,
        NEW.risk_score,
        active_model,
        NEW.feature_version,
        active_dataset
    );

    RETURN NEW;
END;
$func$;