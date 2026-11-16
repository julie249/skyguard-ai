"""
CLI evaluation runner for all 4 detection models across the 3 synthetic benchmark datasets.
Calculates point-level & event-level metrics and writes docs/model_report.md.
"""

from pathlib import Path
import json
import time
import numpy as np
import pandas as pd

from app.src.evaluate import evaluate_metrics, generate_report
from app.src.models.statistical_model import StatisticalDetector
from app.src.models.isolation_forest import IsolationForestDetector
from app.src.models.lstm_autoencoder import LSTMAutoencoderDetector
from app.src.models.ensemble import HybridEnsembleDetector


def run_benchmark():
    datasets = {
        "Synthetic 1%": "data/synthetic/aws_synthetic_1pct.csv",
        "Synthetic 3%": "data/synthetic/aws_synthetic_3pct.csv",
        "Synthetic 8%": "data/synthetic/aws_synthetic_8pct.csv",
    }

    results = {}

    for ds_label, ds_path in datasets.items():
        print(f"\n==========================================")
        print(f"Evaluating Dataset: {ds_label} ({ds_path})")
        print(f"==========================================")
        df = pd.read_csv(ds_path)
        y_true = df["is_anomaly"].fillna(False).values

        # 1. Statistical Detector
        print("Running Statistical Detector...")
        stat_model = StatisticalDetector().fit(df)
        stat_preds, stat_scores = stat_model.predict_series(df)
        stat_metrics = evaluate_metrics(y_true, stat_preds)

        # 2. Isolation Forest
        print("Running Isolation Forest...")
        if_model = IsolationForestDetector(n_estimators=100, random_state=42).fit(df)
        if_preds, if_scores = if_model.predict(df)
        if_metrics = evaluate_metrics(y_true, if_preds)

        # 3. LSTM Autoencoder
        print("Running LSTM Autoencoder...")
        lstm_model = LSTMAutoencoderDetector(epochs=4, batch_size=64).fit(df)
        lstm_preds, lstm_scores = lstm_model.predict(df)
        lstm_metrics = evaluate_metrics(y_true, lstm_preds)
        print(f"LSTM Autoencoder CPU Training Time: {lstm_model.training_time_sec:.2f}s")

        # 4. Hybrid Ensemble Detector
        print("Running Hybrid Ensemble Detector...")
        ensemble_model = HybridEnsembleDetector()
        ens_preds, ens_scores = ensemble_model.predict(
            df,
            stat_scores=stat_scores,
            if_scores=if_scores,
            lstm_scores=lstm_scores,
        )
        ens_metrics = evaluate_metrics(y_true, ens_preds)

        results[ds_label] = {
            "Statistical (Z+IQR)": stat_metrics,
            "Isolation Forest": if_metrics,
            "LSTM Autoencoder": lstm_metrics,
            "Hybrid Ensemble": ens_metrics,
        }

    report_text = generate_report(results, output_path="docs/model_report.md")
    print("\nBenchmark complete! docs/model_report.md updated:")
    print(report_text)


if __name__ == "__main__":
    run_benchmark()
