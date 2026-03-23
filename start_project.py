"""
START PROJECT PIPELINE
--------------------------------------------------
Behavior-Based Micro Risk Scoring Platform

Single entry-point orchestration script.

Runs:
1. Synthetic data generation
2. Feature engineering
3. PostgreSQL loading
4. Visualization
5. Prediction snapshot export
6. Model validation
7. FastAPI server
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


step(
    "Synthetic data generating...",
    "python scripts/generate_synthetic_data.py"
)

step(
    "Feature engineering running...",
    "python scripts/feature_engineering.py"
)

step(
    "Loading dataset into PostgreSQL...",
    "python scripts/load_postgres.py"
)

step(
    "Visualization creating...",
    "python scripts/visualize_final_risk.py"
)


step(
    "Generating prediction snapshot (predictions.csv)...",
    "python scripts/generate_predictions.py"
)

step(
    "Running model validation (MAE & fairness check)...",
    "python scripts/validation.py"
)


print("\n Pipeline completed")
print(" Starting FastAPI server...")

subprocess.run("uvicorn src.api:app --reload", shell=True)