import numpy as np
import pandas as pd
import warnings
from lime.lime_tabular import LimeTabularExplainer

warnings.filterwarnings("ignore", category=RuntimeWarning)

# =====================================================
# GLOBAL CACHE
# =====================================================
_explainer = None
_feature_names = []


# =====================================================
# INITIALIZE (APP STARTUP)
# =====================================================
def initialize_explainer(df: pd.DataFrame, features: list):
    """
    Initialize LIME explainer safely.
    NEVER crashes API.
    """

    global _explainer, _feature_names

    print("\n🔎 Initializing LIME explainer...")

    try:
        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------
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

        # -------------------------------------------------
        # TRAINING DATA PREP
        # -------------------------------------------------
        X = df[features].copy()

        print("📊 Raw feature sample:")
        print(X.head())

        # force numeric
        X = X.apply(pd.to_numeric, errors="coerce")

        # clean NaN / inf
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median(numeric_only=True))
        X = X.fillna(0)

        # -------------------------------------------------
        # VARIANCE CHECK (REAL DEBUG)
        # -------------------------------------------------
        stds = X.std()

        print("\n📈 Feature std values:")
        print(stds)

        valid_columns = stds[stds > 1e-6].index.tolist()

        if len(valid_columns) == 0:
            print("⚠️ LIME disabled: all features zero variance")
            _explainer = None
            _feature_names = []
            return

        # keep only valid columns
        X = X[valid_columns]
        _feature_names = valid_columns

        training_data = X.values.astype(np.float32)

        print("✅ Active LIME features:", _feature_names)
        print("✅ Training shape:", training_data.shape)

        # -------------------------------------------------
        # EXPLAINER INIT
        # -------------------------------------------------
        _explainer = LimeTabularExplainer(
            training_data=training_data,
            feature_names=_feature_names,
            mode="regression",
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

    # dataframe → series
    if isinstance(row_features, pd.DataFrame):
        row_features = row_features.iloc[0]

    # dict → series
    if isinstance(row_features, dict):
        row_features = pd.Series(row_features)

    try:
        # enforce order
        row_features = row_features[_feature_names]
    except Exception:
        return None

    # numeric cleaning
    row_features = pd.to_numeric(row_features, errors="coerce")
    row_features = row_features.replace([np.inf, -np.inf], np.nan)
    row_features = row_features.fillna(0)

    arr = row_features.values.astype(np.float32)

    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)

    # prevent zero variance instance
    if np.std(arr) == 0:
        arr = arr + np.random.normal(0, 1e-6, arr.shape)

    return arr


# =====================================================
# EXPLAIN INSTANCE
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

        exp = _explainer.explain_instance(
            data_row=instance,
            predict_fn=model.predict,
            num_features=len(_feature_names)
        )

        results = []

        for feature, impact in exp.as_list():
            results.append({
                "feature": feature,
                "impact": round(float(impact), 4)
            })

        return results

    except Exception as e:
        print("⚠️ LIME explain failed:", str(e))

        return [{
            "feature": "explanation_failed",
            "impact": 0.0
        }]