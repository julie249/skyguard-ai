"""
Rule-Based Root Cause Classifier.
Maps detected anomaly profiles and spatial agreement scores to specific root causes:
  - sensor_fault: isolated spikes, uncalibrated drift, stuck/frozen sensor values
  - comms_error: dropouts (-999 / 0 / NaN), missing data packets, intermittent signals
  - genuine_extreme: anomalies confirmed and corroborated by spatial neighbors
  - unknown: ambiguous or unclassifiable patterns
All rules are explicitly documented.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class RootCauseClassifier:
    """
    Classifies root cause based on anomaly characteristics and spatial consensus.

    Decision Matrix Rules:
    ----------------------
    1. COMMS_ERROR:
       - Value is missing / NaN / dropout indicator (-99.9 or negative/zero pressure)
       - Consecutive sequence of lost packets
    2. SENSOR_FAULT:
       - Stuck/frozen value: zero variance over window
       - Isolated spike: sharp change NOT corroborated by spatial neighbors (agreement_score < 0.4)
       - Progressive calibration drift over multiple hours
       - High-frequency sensor noise burst
    3. GENUINE_EXTREME:
       - Severe departure from seasonal norm BUT corroborated by >= 50% of neighbor stations
       - Severe storm or frontal passage where surrounding network observes synchronous drop
    4. UNKNOWN:
       - When confidence is low or telemetry is insufficient
    """

    @staticmethod
    def classify(
        anomaly_type: Optional[str],
        reading: Dict[str, Any],
        triggering_features: List[str],
        spatial_support: Optional[Dict[str, Any]] = None,
        confidence: float = 0.5,
    ) -> str:
        """Determines the operational root cause string."""
        # 1. Check for dropout / comms error signals
        if anomaly_type == "dropout":
            return "comms_error"

        for feat in ["temperature_c", "pressure_hpa", "humidity_pct"]:
            val = reading.get(feat)
            if val is None:
                return "comms_error"
            if feat == "temperature_c" and val <= -90.0:
                return "comms_error"
            if feat == "pressure_hpa" and val <= 100.0:
                return "comms_error"

        # 2. Check for stuck sensor
        if anomaly_type == "stuck":
            return "sensor_fault"

        # 3. Check for calibration drift
        if anomaly_type == "drift":
            return "sensor_fault"

        # 4. Check for noise burst
        if anomaly_type == "noise":
            return "sensor_fault"

        # 5. Check spatial corroboration for spikes or general anomalies
        agreement_score = 0.0
        if spatial_support:
            agreement_score = float(spatial_support.get("agreement_score", 0.0))
            is_corroborated = bool(spatial_support.get("is_corroborated", False))

            # If neighbors corroborate the extreme measurement (e.g. heatwave, cyclonic drop)
            if is_corroborated or agreement_score >= 0.5:
                return "genuine_extreme"
            else:
                # Isolated spike repudiated by neighbors
                return "sensor_fault"

        if anomaly_type == "spike":
            # If no neighbor info, default isolated spike to sensor fault
            return "sensor_fault"

        if confidence > 0.6:
            return "sensor_fault"

        return "unknown"
