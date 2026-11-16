"""
Per-Station Isolation Forest Anomaly Detector.
Uses unsupervised multivariate isolation trees to detect subtle multi-feature anomalies.
Outputs normalized anomaly scores in [0, 1] via score_samples().
"""

from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.src.feature_engineering import extract_features


class IsolationForestDetector:
    """
    Multivariate Isolation Forest model with station-level training capability.
    Computes anomaly scores normalized to [0, 1] using invert-scaled decision functions.
    """

    def __init__(
        self,
        contamination: float = 0.03,
        n_estimators: int = 100,
        random_state: int = 42,
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.feature_columns: List[str] = []
        self.fitted = False

    def fit(self, df: pd.DataFrame) -> IsolationForestDetector:
        """Fit IsolationForest on extracted features."""
        feat_df = extract_features(df)
        self.feature_columns = list(feat_df.columns)
        X = self.scaler.fit_transform(feat_df.values)
        self.model.fit(X)
        self.fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predicts anomalies and normalized scores for DataFrame.
        Returns:
          (is_anomaly_array, normalized_confidence_scores)
        """
        if not self.fitted:
            self.fit(df)

        feat_df = extract_features(df)
        X = self.scaler.transform(feat_df[self.feature_columns].values)

        # raw_preds: -1 for anomaly, 1 for inlier
        raw_preds = self.model.predict(X)
        is_anomaly = raw_preds == -1

        # score_samples: opposite of the anomaly score (lower means more abnormal)
        # Typically in range [-0.8, -0.3] for anomalies, > -0.3 for inliers
        raw_scores = self.model.score_samples(X)
        # Normalize into [0, 1] where 1.0 is extreme anomaly
        # min_val approx -0.8, max_val approx -0.3
        norm_scores = (np.clip(raw_scores, -0.85, -0.30) - (-0.30)) / (-0.55)
        norm_scores = np.clip(norm_scores, 0.0, 1.0)

        return is_anomaly, np.round(norm_scores, 4)

    def score_single_point(self, feature_row: np.ndarray) -> Tuple[bool, float]:
        """Score single feature vector."""
        if feature_row.ndim == 1:
            feature_row = feature_row.reshape(1, -1)
        X = self.scaler.transform(feature_row)
        pred = self.model.predict(X)[0]
        raw_score = self.model.score_samples(X)[0]
        norm_score = float(np.clip((np.clip(raw_score, -0.85, -0.30) - (-0.30)) / (-0.55), 0.0, 1.0))
        return (pred == -1), round(norm_score, 4)
