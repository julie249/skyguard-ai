"""
02_Baseline_Models — Statistical (Z-score + IQR) and Isolation Forest Benchmarking.
Evaluates point-level vs event-level precision, recall, and F1 metrics.
"""

# %%
import pandas as pd
import numpy as np
from app.src.models.statistical_model import StatisticalDetector
from app.src.models.isolation_forest import IsolationForestDetector
from app.src.evaluate import evaluate_metrics

# %%
df = pd.read_csv("../data/synthetic/aws_synthetic_3pct.csv")
y_true = df["is_anomaly"].fillna(False).values

# %%
# 1. Statistical Detector Benchmark
stat_model = StatisticalDetector().fit(df)
stat_preds, stat_scores = stat_model.predict_series(df)
stat_metrics = evaluate_metrics(y_true, stat_preds)
print("Statistical Detector Metrics:", stat_metrics)

# %%
# 2. Isolation Forest Benchmark
if_model = IsolationForestDetector(n_estimators=100, random_state=42).fit(df)
if_preds, if_scores = if_model.predict(df)
if_metrics = evaluate_metrics(y_true, if_preds)
print("Isolation Forest Metrics:", if_metrics)
