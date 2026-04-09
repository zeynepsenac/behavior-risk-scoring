import numpy as np
import pandas as pd
import warnings
import re
from lime.lime_tabular import LimeTabularExplainer

warnings.filterwarnings("ignore", category=RuntimeWarning)

# =====================================================
# GLOBAL CACHE
# =====================================================
_explainer = None
_feature_names = []


# =====================================================
# FEATURE CLEANER
# =====================================================
def clean_lime_feature(feature_text: str) -> str:
    try:
        return re.split(r"\s*(<=|>=|<|>)\s*", feature_text)[0]
    except Exception:
        return feature_text


# =====================================================
# INITIALIZE (APP STARTUP)
# =====================================================
def initialize_explainer(df: pd.DataFrame, features: list):

    global _explainer, _feature_names

    print("\n🔎 Initializing LIME explainer...")

    try:
        if df is None or df.empty:
            print("⚠️ LIME disabled: empty dataframe")
            _explainer = None
            _feature_names = []
            return

        missing = [f for f in features if f not in df.columns]
        if missing:
            print("⚠️ Missing features:", missing)
            _explainer = None
            _feature_names = []
            return

        X = df[features].copy()

        X = X.apply(pd.to_numeric, errors="coerce")
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median(numeric_only=True))
        X = X.fillna(0)

        stds = X.std()
        valid_columns = stds[stds > 1e-6].index.tolist()

        if len(valid_columns) == 0:
            print("⚠️ LIME disabled: all features zero variance")
            _explainer = None
            _feature_names = []
            return

        X = X[valid_columns]
        _feature_names = valid_columns

        training_data = X.values.astype(np.float32)

        print("✅ Active LIME features:", _feature_names)
        print("✅ Training shape:", training_data.shape)

        _explainer = LimeTabularExplainer(
            training_data=training_data,
            feature_names=_feature_names,
            mode="classification",
            discretize_continuous=False,
            random_state=42
        )

        print("✅ LIME explainer initialized successfully\n")

    except Exception as e:
        print("⚠️ LIME initialization failed:", str(e))
        _explainer = None
        _feature_names = []


# =====================================================
# INSTANCE PREPARATION
# =====================================================
def _prepare_instance(row_features):

    global _feature_names

    if not _feature_names:
        return None

    if isinstance(row_features, pd.DataFrame):
        row_features = row_features.iloc[0]

    if isinstance(row_features, dict):
        row_features = pd.Series(row_features)

    try:
        row_features = row_features[_feature_names]
    except Exception:
        return None

    row_features = pd.to_numeric(row_features, errors="coerce")
    row_features = row_features.replace([np.inf, -np.inf], np.nan)
    row_features = row_features.fillna(0)

    arr = row_features.values.astype(np.float32)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)

    if np.std(arr) == 0:
        arr = arr + np.random.normal(0, 1e-6, arr.shape)

    return arr


# =====================================================
# EXPLAIN INSTANCE (MAIN CALL)
# =====================================================
# =====================================================
# EXPLAIN INSTANCE (MAIN CALL)
# =====================================================
def explain_instance(row_features, model):

    global _explainer, _feature_names

    if _explainer is None or not _feature_names:
        return [{
            "feature": "explanation_unavailable",
            "impact": 0.0
        }]

    try:
        instance = _prepare_instance(row_features)

        if instance is None:
            return [{
                "feature": "explanation_unavailable",
                "impact": 0.0
            }]

        # 🔥🔥🔥 KRİTİK FIX BURASI
        def predict_fn(x):
            try:
                # 👉 regression model output
                raw = model.predict(x)

                # 👉 normalize (SENİN SİSTEMİNLE UYUMLU)
                normalized = raw / 25.0

                # 👉 LIME classification bekliyor → 2D probability format
                return np.vstack([1 - normalized, normalized]).T

            except Exception as e:
                print("predict_fn error:", e)
                return np.zeros((len(x), 2))

        exp = _explainer.explain_instance(
            data_row=instance,
            predict_fn=predict_fn,
            num_features=min(5, len(_feature_names))
        )

        results = []

        # 👉 risk class = 1
        for feature, impact in exp.as_list(label=1):
            clean_feature = clean_lime_feature(feature)

            results.append({
                "feature": clean_feature,
                "impact": round(float(impact), 4)
            })

        return results

    except Exception as e:
        print("⚠️ LIME explain failed:", str(e))

        return [{
            "feature": "explanation_failed",
            "impact": 0.0
        }]


# =====================================================
# API COMPATIBILITY WRAPPER
# =====================================================
def build_explanation(row_features, model, *args, **kwargs):
    return explain_instance(row_features, model)