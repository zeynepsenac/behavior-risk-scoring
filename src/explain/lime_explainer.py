import pandas as pd
from lime.lime_tabular import LimeTabularExplainer

# =====================================================
# GLOBAL EXPLAINER CACHE
# =====================================================
_explainer = None
_feature_names = None


# =====================================================
# INITIALIZE (CALL ON STARTUP)
# =====================================================
def initialize_explainer(df: pd.DataFrame, features: list):

    global _explainer, _feature_names

    _feature_names = features

    _explainer = LimeTabularExplainer(
        training_data=df[features].values,
        feature_names=features,
        mode="regression",
        discretize_continuous=True
    )

    print("LIME explainer initialized (cached)")


# =====================================================
# EXPLAIN INSTANCE
# =====================================================
def explain_instance(row_features, model):

    if _explainer is None:
        raise RuntimeError("Explainer not initialized")

    exp = _explainer.explain_instance(
        row_features.values,
        model.predict,
        num_features=len(_feature_names)
    )

    results = []

    for feature, impact in exp.as_list():
        results.append({
            "feature": feature,
            "impact": round(float(impact), 4)
        })

    return results