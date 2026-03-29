SET search_path TO public;

INSERT INTO public.model_registry(
    model_version,
    model_name,
    is_active
)
VALUES ('v2.0','xgboost', TRUE)
ON CONFLICT (model_version)
DO UPDATE SET
    model_name = EXCLUDED.model_name,
    is_active = TRUE;