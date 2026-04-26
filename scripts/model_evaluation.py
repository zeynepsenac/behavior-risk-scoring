import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.calibration import calibration_curve
from sklearn.model_selection import train_test_split
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# =========================
# PATH SETUP
# =========================
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "predictions.csv"
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(DATA_PATH)

print("MODEL EVALUATION STARTED")

# =========================
# SAFE COLUMN HANDLING (FIX)
# =========================
def get_score_column(df):
    candidates = ["risk_score", "risk", "predicted_risk_score", "score"]
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError("No valid risk column found in dataset!")

score_col = get_score_column(df)

# fallback for prediction score
if "predicted_risk_score" not in df.columns:
    if "risk_score" in df.columns:
        df["predicted_risk_score"] = df["risk_score"]
    else:
        df["predicted_risk_score"] = df[score_col]

# =========================
# LABEL CREATION (FIXED)
# =========================
df["true_label"] = np.where(df[score_col] > 0.5, 1, 0)

threshold = df["predicted_risk_score"].median()
df["pred_label"] = np.where(df["predicted_risk_score"] > threshold, 1, 0)

# =========================
# SPLIT
# =========================
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

y_true = test_df["true_label"]
y_pred = test_df["pred_label"]
y_score = test_df["predicted_risk_score"]

# =========================
# METRICS
# =========================
acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, zero_division=0)
rec = recall_score(y_true, y_pred, zero_division=0)
f1 = f1_score(y_true, y_pred, zero_division=0)

mae = mean_absolute_error(test_df[score_col], y_score)
rmse = np.sqrt(mean_squared_error(test_df[score_col], y_score))
r2 = r2_score(test_df[score_col], y_score)

print("Metrics calculated")

# =========================
# 1. CONFUSION MATRIX
# =========================
cm = confusion_matrix(y_true, y_pred)

disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot()

plt.title("Confusion Matrix")
plt.savefig(REPORT_DIR / "validation_confusion_matrix.png")
plt.close()

# =========================
# 2. CALIBRATION CURVE
# =========================
prob_true, prob_pred = calibration_curve(y_true, y_score, n_bins=10)

plt.plot(prob_pred, prob_true, marker="o")
plt.plot([0, 1], [0, 1], linestyle="--")
plt.title("Calibration Curve")
plt.xlabel("Predicted Probability")
plt.ylabel("True Probability")

plt.savefig(REPORT_DIR / "calibration_chart.png")
plt.close()

# =========================
# 3. BIAS ANALYSIS
# =========================
bias = y_score - test_df[score_col]

plt.hist(bias, bins=20)
plt.title("Prediction Bias Distribution")

plt.savefig(REPORT_DIR / "validation_bias_chart.png")
plt.close()

# =========================
# 4. PERFORMANCE CHART
# =========================
metrics_names = ["Accuracy", "Precision", "Recall", "F1"]
metrics_values = [acc, prec, rec, f1]

plt.bar(metrics_names, metrics_values)
plt.ylim(0, 1)
plt.title("Model Performance")

plt.savefig(REPORT_DIR / "validation_performance_chart.png")
plt.close()

# =========================
# 5. SAVE CSV REPORT
# =========================
report_df = pd.DataFrame([
    ["Accuracy", acc],
    ["Precision", prec],
    ["Recall", rec],
    ["F1 Score", f1],
    ["MAE", mae],
    ["RMSE", rmse],
    ["R2 Score", r2],
    ["Threshold", threshold]
], columns=["Metric", "Value"])

report_df.to_csv(REPORT_DIR / "model_metrics.csv", index=False)

# =========================
# 6. PDF REPORT
# =========================
pdf_path = REPORT_DIR / "model_evaluation_report.pdf"

doc = SimpleDocTemplate(str(pdf_path))
styles = getSampleStyleSheet()

content = []
content.append(Paragraph("MODEL EVALUATION REPORT", styles["Title"]))
content.append(Spacer(1, 20))

for _, row in report_df.iterrows():
    content.append(Paragraph(f"{row['Metric']}: {round(row['Value'], 4)}", styles["Normal"]))

doc.build(content)

print("\nMODEL EVALUATION COMPLETED")
print("Reports saved to:", REPORT_DIR)