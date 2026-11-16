import pytest
import pandas as pd
import numpy as np
from app.src.data_loader import generate_synthetic_station_data
from app.src.anomaly_injector import AnomalyInjector


def test_anomaly_injector_deterministic():
    df = generate_synthetic_station_data(station_id="TEST001", days=5, seed=42)
    injector1 = AnomalyInjector(seed=123)
    corrupted1, gt1 = injector1.inject(df, {"rate": 0.05})

    injector2 = AnomalyInjector(seed=123)
    corrupted2, gt2 = injector2.inject(df, {"rate": 0.05})

    pd.testing.assert_frame_equal(corrupted1, corrupted2)
    pd.testing.assert_frame_equal(gt1, gt2)


def test_anomaly_injector_types_and_ground_truth():
    df = generate_synthetic_station_data(station_id="TEST001", days=10, seed=42)
    injector = AnomalyInjector(seed=999)
    corrupted, gt = injector.inject(df, {"rate": 0.04, "types": ["spike", "stuck", "dropout", "drift", "noise_burst"]})

    assert corrupted["is_anomaly"].sum() > 0
    pd.testing.assert_series_equal(corrupted["is_anomaly"], gt["is_anomaly"])
    pd.testing.assert_series_equal(corrupted["anomaly_type"], gt["anomaly_type"])

    # Verify known anomaly types exist in injected output
    unique_types = set(corrupted["anomaly_type"].dropna().unique())
    assert len(unique_types) > 0
    valid_types = {"spike", "stuck", "dropout", "drift", "noise"}
    assert unique_types.issubset(valid_types)


def test_anomaly_injector_spike_values():
    df = generate_synthetic_station_data(station_id="TEST001", days=5, seed=1)
    injector = AnomalyInjector(seed=10)
    corrupted, _ = injector.inject(df, {"rate": 0.02, "types": ["spike"], "features": ["temperature_c"]})
    spikes = corrupted[corrupted["anomaly_type"] == "spike"]
    assert len(spikes) > 0
    # Spikes should differ noticeably from original base values
    orig_temp = df.loc[spikes.index, "temperature_c"]
    corrupted_temp = spikes["temperature_c"]
    assert (np.abs(corrupted_temp - orig_temp) > 10.0).all()
