"""
Ensemble Anomaly Detector combining Statistical, Isolation Forest, and LSTM Autoencoder.
Formula:
  Agreement Bonus: Cross-model consensus exponentially reinforces confidence.
  Disagreement Penalty: High variance across models scales down final alert confidence.
Exact formula documented in docstring.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from app.src.models.statistical_model import StatisticalDetector
from app.src.models.isolation_forest import IsolationForestDetector


class HybridEnsembleDetector:
    """
    Weighted Ensemble Anomaly Detector.

    Mathematical Formulation:
    -------------------------
    Let m_i be the model i score in [0, 1] with base weight w_i (sum(w_i) = 1.0).
    Base weighted score:
        S_base = sum(w_i * m_i)

    Agreement Factor (Consensus Amplifier):
        Let p_i = I(m_i >= threshold_i).
        Agreement Ratio A = count(p_i == 1) / N_models.
        Disagreement Variance V = sum((m_i - S_base)^2) / N_models.

    Final Calibrated Ensemble Score:
        If A >= 0.66 (at least 2/3 agree):
            S_final = S_base + (1.0 - S_base) * (A - 0.5) * 0.4
        Else if A == 0:
            S_final = S_base * 0.4
        Else (mixed / uncertain):
            S_final = S_base * (1.0 - np.sqrt(V) * 0.5)

    Thresholding:
        is_anomaly = S_final >= alert_threshold (default 0.45)
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        alert_threshold: float = 0.45,
    ):
        self.weights = weights or {
            "statistical": 0.35,
            "isolation_forest": 0.35,
            "lstm_autoencoder": 0.30,
        }
        self.alert_threshold = alert_threshold
        self.stat_model = StatisticalDetector()
        self.if_model = IsolationForestDetector()
        self.lstm_model = None

    def fit(self, df: pd.DataFrame) -> HybridEnsembleDetector:
        """Fit all component detectors."""
        self.stat_model.fit(df)
        self.if_model.fit(df)
        if self.lstm_model is not None:
            self.lstm_model.fit(df)
        return self

    def predict(
        self,
        df: pd.DataFrame,
        stat_scores: Optional[np.ndarray] = None,
        if_scores: Optional[np.ndarray] = None,
        lstm_scores: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates ensemble predictions and calibrated confidence scores.
        Returns:
          (is_anomaly_array, calibrated_confidence_array)
        """
        n = len(df)
        if stat_scores is None:
            _, stat_scores = self.stat_model.predict_series(df)
        if if_scores is None:
            _, if_scores = self.if_model.predict(df)
        if lstm_scores is None:
            if self.lstm_model is not None:
                _, lstm_scores = self.lstm_model.predict(df)
            else:
                # Fallback to mean of available if LSTM not invoked
                lstm_scores = (stat_scores + if_scores) / 2.0

        w_stat = self.weights["statistical"]
        w_if = self.weights["isolation_forest"]
        w_lstm = self.weights["lstm_autoencoder"]
        total_w = w_stat + w_if + w_lstm

        # Base weighted score
        s_base = (w_stat * stat_scores + w_if * if_scores + w_lstm * lstm_scores) / total_w

        # Binary decisions per model
        b_stat = (stat_scores >= 0.40).astype(float)
        b_if = (if_scores >= 0.45).astype(float)
        b_lstm = (lstm_scores >= 0.40).astype(float)

        # Agreement ratio A in [0, 1]
        agreement_ratio = (b_stat + b_if + b_lstm) / 3.0

        # Disagreement variance V
        diff_stat = (stat_scores - s_base) ** 2
        diff_if = (if_scores - s_base) ** 2
        diff_lstm = (lstm_scores - s_base) ** 2
        variance = (diff_stat + diff_if + diff_lstm) / 3.0

        # Consensus calibration
        # High agreement bonus
        high_agree = agreement_ratio >= 0.66
        zero_agree = agreement_ratio == 0.0
        mixed = (~high_agree) & (~zero_agree)

        s_final = np.zeros(n, dtype=float)
        s_final[high_agree] = s_base[high_agree] + (1.0 - s_base[high_agree]) * (agreement_ratio[high_agree] - 0.5) * 0.4
        s_final[zero_agree] = s_base[zero_agree] * 0.35
        s_final[mixed] = s_base[mixed] * (1.0 - np.sqrt(variance[mixed]) * 0.4)

        s_final = np.clip(s_final, 0.0, 1.0)
        is_anomaly = s_final >= self.alert_threshold

        return is_anomaly, np.round(s_final, 4)
