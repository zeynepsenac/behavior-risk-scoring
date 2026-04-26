"""
START PROJECT PIPELINE
--------------------------------------------------
Behavior-Based Micro Risk Scoring Platform

Single entry-point orchestration script.

Runs:
1. Synthetic data generation
2. Feature engineering
3. KVKK anonymization (privacy layer)
4. PostgreSQL loading
5. Visualization
6. Prediction snapshot export
7. Model validation
8. FastAPI server
--------------------------------------------------
"""

import subprocess
import sys
import time


def step(message, command):
    print("\n================================================")
    print(f" {message}")
    print("================================================")

    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        print(f"\n STEP FAILED: {message}")
        sys.exit(1)

    print(f" COMPLETED: {message}")
    time.sleep(1)


print("\n==============================")
print("   AI RISK ANALYSIS SYSTEM")
print("==============================")

print("\n===== RISK ANALYSIS PROJECT STARTING =====")


# 1. Synthetic Data
step(
    "Synthetic data generating...",
    "python scripts/generate_synthetic_data.py"
)

# 2. Feature Engineering
step(
    "Feature engineering running...",
    "python scripts/feature_engineering.py"
)

# 🔥 3. KVKK PRIVACY LAYER (FIXED)
step(
    "Applying KVKK anonymization (k-anonymity + l-diversity)...",
    "python scripts/anonymize_data.py"
)

# 4. PostgreSQL Load
step(
    "Loading dataset into PostgreSQL...",
    "python scripts/load_postgres.py"
)

# 5. Visualization
step(
    "Visualization creating...",
    "python scripts/visualize_final_risk.py"
)

# 6. Predictions
step(
    "Generating prediction snapshot (predictions.csv)...",
    "python scripts/generate_predictions.py"
)

# 7. Validation
step(
    "Running model validation (MAE & fairness check)...",
    "python scripts/validation.py"
)

print("\n Pipeline completed")
print(" Starting FastAPI server...")

# 8. API
subprocess.run("uvicorn src.api:app --reload", shell=True)