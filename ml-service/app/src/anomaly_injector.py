"""
Deterministic Anomaly Injector for Automatic Weather Station readings.
Implements spike, stuck, dropout, drift, and noise_burst anomaly types.
Strictly logs altered indices and assigns ground truth labels.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class AnomalyInjector:
    """
    Injects realistic AWS sensor failure patterns:
    - spike: sudden single or multi-step extreme pulse
    - stuck: sensor value freezes constant across time
    - dropout: sensor drops to zero / unphysical negative or NaN
    - drift: progressive linear calibration offset accumulating over time
    - noise_burst: sharp increase in high-frequency sensor variance
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def inject(
        self, df: pd.DataFrame, config: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Inject anomalies into a canonical AWS DataFrame.
        Config schema:
          {
            "rate": float (e.g. 0.03 for 3%),
            "types": ["spike", "stuck", "dropout", "drift", "noise_burst"],
            "features": ["temperature_c", "pressure_hpa", "humidity_pct"]
          }
        Returns:
          (corrupted_df, ground_truth_df)
        """
        corrupted = df.copy()
        n = len(corrupted)
        rate = float(config.get("rate", 0.03))
        types = config.get("types", ["spike", "stuck", "dropout", "drift", "noise_burst"])
        features = config.get("features", ["temperature_c", "pressure_hpa", "humidity_pct"])

        # Determine target number of anomalous points
        total_anomaly_points = max(1, int(n * rate))
        points_assigned = 0

        # Maintain list of modified indices
        modified_records: List[Dict[str, Any]] = []

        # Available indices for event injection (leave room for sequence duration)
        available_indices = np.arange(10, n - 30)
        self.rng.shuffle(available_indices)
        idx_pointer = 0

        while points_assigned < total_anomaly_points and idx_pointer < len(available_indices):
            start_idx = int(available_indices[idx_pointer])
            idx_pointer += 1

            # Check if this index was already modified
            if corrupted.loc[start_idx, "is_anomaly"]:
                continue

            atype = self.rng.choice(types)
            feature = self.rng.choice(features)

            if atype == "spike":
                # 1 to 3 time steps
                duration = self.rng.integers(1, 4)
                duration = min(duration, total_anomaly_points - points_assigned)
                indices = list(range(start_idx, min(start_idx + duration, n)))

                # Positive or negative spike
                magnitude = 15.0 if feature == "temperature_c" else (40.0 if feature == "pressure_hpa" else 35.0)
                sign = self.rng.choice([-1.0, 1.0])
                for idx in indices:
                    val = corrupted.loc[idx, feature] + sign * magnitude
                    if feature == "humidity_pct":
                        val = np.clip(val, 0.0, 100.0)
                    corrupted.loc[idx, feature] = round(float(val), 2)
                    corrupted.loc[idx, "is_anomaly"] = True
                    corrupted.loc[idx, "anomaly_type"] = "spike"
                    points_assigned += 1
                    modified_records.append({"index": idx, "type": "spike", "feature": feature})

            elif atype == "stuck":
                # 6 to 18 time steps (1 to 3 hours frozen)
                duration = self.rng.integers(6, 18)
                duration = min(duration, total_anomaly_points - points_assigned)
                indices = list(range(start_idx, min(start_idx + duration, n)))
                stuck_val = corrupted.loc[start_idx, feature]

                for idx in indices:
                    corrupted.loc[idx, feature] = stuck_val
                    corrupted.loc[idx, "is_anomaly"] = True
                    corrupted.loc[idx, "anomaly_type"] = "stuck"
                    points_assigned += 1
                    modified_records.append({"index": idx, "type": "stuck", "feature": feature})

            elif atype == "dropout":
                # 1 to 5 time steps of missing/zero sensor signal
                duration = self.rng.integers(1, 6)
                duration = min(duration, total_anomaly_points - points_assigned)
                indices = list(range(start_idx, min(start_idx + duration, n)))

                for idx in indices:
                    # In weather stations, dropouts often manifest as -999.0 or 0.0 or unphysical negative
                    dropout_val = -99.9 if feature == "temperature_c" else 0.0
                    corrupted.loc[idx, feature] = dropout_val
                    corrupted.loc[idx, "is_anomaly"] = True
                    corrupted.loc[idx, "anomaly_type"] = "dropout"
                    points_assigned += 1
                    modified_records.append({"index": idx, "type": "dropout", "feature": feature})

            elif atype == "drift":
                # 12 to 36 steps of progressive calibration drift
                duration = self.rng.integers(12, 36)
                duration = min(duration, total_anomaly_points - points_assigned)
                indices = list(range(start_idx, min(start_idx + duration, n)))
                max_drift = 8.0 if feature == "temperature_c" else (18.0 if feature == "pressure_hpa" else 25.0)
                slope = max_drift / max(duration, 1)

                for step_i, idx in enumerate(indices):
                    corrupted.loc[idx, feature] = round(
                        float(corrupted.loc[idx, feature] + (step_i + 1) * slope), 2
                    )
                    corrupted.loc[idx, "is_anomaly"] = True
                    corrupted.loc[idx, "anomaly_type"] = "drift"
                    points_assigned += 1
                    modified_records.append({"index": idx, "type": "drift", "feature": feature})

            elif atype == "noise_burst":
                # 6 to 15 steps of extreme sensor noise
                duration = self.rng.integers(6, 16)
                duration = min(duration, total_anomaly_points - points_assigned)
                indices = list(range(start_idx, min(start_idx + duration, n)))
                noise_scale = 5.0 if feature == "temperature_c" else (12.0 if feature == "pressure_hpa" else 15.0)

                for idx in indices:
                    burst = self.rng.normal(0, noise_scale)
                    val = corrupted.loc[idx, feature] + burst
                    if feature == "humidity_pct":
                        val = np.clip(val, 0.0, 100.0)
                    corrupted.loc[idx, feature] = round(float(val), 2)
                    corrupted.loc[idx, "is_anomaly"] = True
                    corrupted.loc[idx, "anomaly_type"] = "noise"
                    points_assigned += 1
                    modified_records.append({"index": idx, "type": "noise", "feature": feature})

        logger.info(
            "Injected %d anomaly points across %d operations. Effective rate: %.4f",
            points_assigned,
            len(modified_records),
            points_assigned / n,
        )

        ground_truth = corrupted[["station_id", "timestamp", "is_anomaly", "anomaly_type"]].copy()
        return corrupted, ground_truth
