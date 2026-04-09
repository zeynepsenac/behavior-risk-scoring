import hashlib
import json
import os
from datetime import datetime


# =====================================================
# PROJECT PATHS
# =====================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "risk_model.pkl")
METADATA_PATH = os.path.join(PROJECT_ROOT, "models", "metadata.json")


# =====================================================
# VERSION CONFIG
# =====================================================

# Feature engineering version
DEFAULT_FEATURE_VERSION = "v1"

# Dataset version (NEW)
# Dataset değiştiğinde burası güncellenir
DEFAULT_DATASET_VERSION = "v1.0"


# =====================================================
# MODEL HASH CALCULATION
# =====================================================

def calculate_model_hash(file_path: str) -> str:
    """
    Calculates SHA256 hash of trained model file.
    Used for model version tracking.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


# =====================================================
# METADATA CREATION
# =====================================================

def create_metadata(
    features,
    feature_version: str = DEFAULT_FEATURE_VERSION,
    dataset_version: str = DEFAULT_DATASET_VERSION
):
    """
    Creates metadata.json for model lineage tracking.

    Stored information:
    - model hash
    - training timestamp
    - feature version
    - dataset version
    - feature list
    - model type
    """

    # --- model hash ---
    model_hash = calculate_model_hash(MODEL_PATH)

    # --- metadata object ---
    metadata = {
        "model_hash": model_hash,
        "trained_at": datetime.utcnow().isoformat(),
        "feature_version": feature_version,
        "dataset_version": dataset_version,   # ✅ NEW FIELD
        "features": features,
        "model_type": "XGBRegressor"
    }

    # --- save metadata ---
    os.makedirs(os.path.dirname(METADATA_PATH), exist_ok=True)

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=4)

    print("✅ metadata.json created")
    print(f"   Model hash: {model_hash[:10]}...")
    print(f"   Dataset version: {dataset_version}")
    print(f"   Feature version: {feature_version}")