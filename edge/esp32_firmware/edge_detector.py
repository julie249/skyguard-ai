"""
SkyGuard AI — Standalone Edge Firmware (MicroPython / Raspberry Pi / ESP32)
Zero-dependency lightweight meteorological anomaly detector.
Implements Z-Score, IQR, and meteorological physical boundary checks on-chip.
Runs offline with minimal power draw for solar-powered remote AWS field stations.
"""

import time
import math

class EdgeStatisticalDetector:
    def __init__(self):
        # Baseline climatological distributions for North India plains
        self.baselines = {
            "temperature_c": {"mean": 24.5, "std": 6.2, "q1": 19.5, "q3": 29.8, "iqr": 10.3},
            "pressure_hpa": {"mean": 1012.0, "std": 5.8, "q1": 1008.0, "q3": 1016.0, "iqr": 8.0},
            "humidity_pct": {"mean": 62.0, "std": 18.0, "q1": 48.0, "q3": 76.0, "iqr": 28.0},
        }
        self.z_threshold = 3.2
        self.iqr_multiplier = 2.0

    def evaluate_reading(self, temp_c, pressure_hpa, humidity_pct):
        start = time.ticks_us() if hasattr(time, "ticks_us") else time.perf_counter()
        triggers = []
        is_anomaly = False

        readings = {
            "temperature_c": temp_c,
            "pressure_hpa": pressure_hpa,
            "humidity_pct": humidity_pct,
        }

        # Physical limits
        if temp_c < -60.0 or temp_c > 65.0:
            triggers.append("temperature_c")
            is_anomaly = True
        if pressure_hpa < 700.0 or pressure_hpa > 1100.0:
            triggers.append("pressure_hpa")
            is_anomaly = True
        if humidity_pct < 0.0 or humidity_pct > 100.0:
            triggers.append("humidity_pct")
            is_anomaly = True

        # Statistical gating
        for feat, val in readings.items():
            base = self.baselines[feat]
            z = abs(val - base["mean"]) / base["std"]
            lower_bound = base["q1"] - self.iqr_multiplier * base["iqr"]
            upper_bound = base["q3"] + self.iqr_multiplier * base["iqr"]

            if z >= self.z_threshold or val < lower_bound or val > upper_bound:
                if feat not in triggers:
                    triggers.append(feat)
                is_anomaly = True

        elapsed_us = (time.ticks_diff(time.ticks_us(), start)) if hasattr(time, "ticks_us") else (time.perf_counter() - start) * 1000000
        latency_ms = elapsed_us / 1000.0

        return {
            "is_anomaly": is_anomaly,
            "triggers": triggers,
            "latency_ms": latency_ms,
        }

if __name__ == "__main__":
    detector = EdgeStatisticalDetector()
    print("SkyGuard AI Edge Detector Initialized (ESP32/MicroPython Standalone)")
    test_reading = (55.4, 1010.0, 20.0)
    result = detector.evaluate_reading(*test_reading)
    print("Test reading (55.4C, 1010hPa, 20%):", result)
