-- calculate_risk_score


CREATE OR REPLACE FUNCTION calculate_risk_score(_customer_id INT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_score NUMERIC;
BEGIN

    SELECT risk_score
    INTO v_score
    FROM engineered_features
    WHERE customer_id = _customer_id;

    RETURN COALESCE(v_score, 0);

END;
$$;



-- explain_customer


CREATE OR REPLACE FUNCTION explain_customer(_customer_id INT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result JSON;
BEGIN

    SELECT json_build_object(
        'customer_id', customer_id,
        'risk_score', risk_score,
        'risk_band', risk_band
    )
    INTO result
    FROM engineered_features
    WHERE customer_id = _customer_id;

    RETURN COALESCE(
        result,
        json_build_object('error','customer_not_found')
    );

END;
$$;