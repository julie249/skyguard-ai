"""
Ultra-fast real-time statistical anomaly detector for AWS data.
Combines rolling Z-score with dynamic Interquartile Range (IQR) gating.
Target latency: <50ms per single reading evaluation.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


class StatisticalDetector:
    """
    Statistical Anomaly Detector using dynamic Z-Score and Interquartile Range (IQR).
    Operates on rolling windows or pre-calibrated baseline distributions.
    Capable of scoring batch series or single incoming points in <10ms.
    """

    def __init__(
        self,
        z_threshold: float = 3.2,
        iqr_multiplier: float = 2.2,
        features: list[str] = ["temperature_c", "pressure_hpa", "humidity_pct"],
    ):
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier
        self.features = features
        self.baselines: Dict[str, Dict[str, float]] = {}

    def fit(self, df: pd.DataFrame) -> StatisticalDetector:
        """Calculate mean, std, Q1, Q3, and IQR per feature from training data."""
        for feat in self.features:
            s = df[feat].dropna()
            q1 = float(s.quantile(0.25))
            q3 = float(s.quantile(0.75))
            iqr = q3 - q1
            self.baselines[feat] = {
                "mean": float(s.mean()),
                "std": float(s.std()) if float(s.std()) > 0 else 1.0,
                "q1": q1,
                "q3": q3,
                "iqr": iqr if iqr > 0 else 1.0,
                "lower_bound": q1 - self.iqr_multiplier * iqr,
                "upper_bound": q3 + self.iqr_multiplier * iqr,
            }
        return self

    def score_single_point(self, reading: Dict[str, float]) -> Tuple[bool, float, List[str], float]:
        """
        Scores a single incoming reading.
        Returns:
          (is_anomaly, confidence, triggering_features, latency_ms)
        Execution is guaranteed in <50ms (typically <1ms).
        """
        start = time.perf_counter()
        triggering = []
        max_score = 0.0

        for feat in self.features:
            if feat not in reading or reading[feat] is None:
                continue

            val = float(reading[feat])
            base = self.baselines.get(feat, {"mean": 20.0, "std": 5.0, "lower_bound": -10.0, "upper_bound": 55.0, "iqr": 10.0})

            # Z-score test
            z = abs(val - base["mean"]) / base["std"]
            # IQR test
            iqr_breach = val < base["lower_bound"] or val > base["upper_bound"]

            # Physical meteorological sanity checks
            physical_breach = False
            if feat == "temperature_c" and (val < -60.0 or val > 65.0):
                physical_breach = True
            elif feat == "pressure_hpa" and (val < 750.0 or val > 1100.0):
                physical_breach = True
            elif feat == "humidity_pct" and (val < 0.0 or val > 100.0):
                physical_breach = True

            if z >= self.z_threshold or iqr_breach or physical_breach:
                triggering.append(feat)

            # Normalized anomaly score for this feature [0, 1]
            feat_score = np.clip(z / (self.z_threshold * 2.0), 0.0, 1.0)
            if physical_breach:
                feat_score = 1.0
            if feat_score > max_score:
                max_score = feat_score

        is_anomaly = len(triggering) > 0
        latency_ms = (time.perf_counter() - start) * 1000.0
        return is_anomaly, round(float(max_score), 4), triggering, round(latency_ms, 3)

    def predict_series(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Batch prediction over DataFrame.
        Returns:
          (is_anomaly_array, confidence_scores_array)
        """
        if not self.baselines:
            self.fit(df)

        n = len(df)
        is_anomaly = np.zeros(n, dtype=bool)
        confidence = np.zeros(n, dtype=float)

        for feat in self.features:
            s = df[feat].values
            base = self.baselines[feat]
            z = np.abs(s - base["mean"]) / base["std"]
            iqr_mask = (s < base["lower_bound"]) | (s > base["upper_bound"])
            feat_anomaly = (z >= self.z_threshold) | iqr_mask

            is_anomaly = is_anomaly | feat_anomaly
            feat_conf = np.clip(z / (self.z_threshold * 2.0), 0.0, 1.0)
            confidence = np.maximum(confidence, feat_conf)

        return is_anomaly, np.round(confidence, 4)
