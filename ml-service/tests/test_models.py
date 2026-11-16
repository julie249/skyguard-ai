import time
import pytest
import numpy as np
import pandas as pd

from app.src.data_loader import generate_synthetic_station_data
from app.src.anomaly_injector import AnomalyInjector
from app.src.feature_engineering import extract_features
from app.src.models.statistical_model import StatisticalDetector
from app.src.models.isolation_forest import IsolationForestDetector
from app.src.models.lstm_autoencoder import LSTMAutoencoderDetector
from app.src.models.ensemble import HybridEnsembleDetector


def test_feature_engineering_dimensions():
    df = generate_synthetic_station_data(station_id="TEST001", days=3, seed=10)
    features = extract_features(df)
    assert len(features) == len(df)
    assert "dew_point_c" in features.columns
    assert "dew_point_depression" in features.columns
    assert "temperature_c_roll_mean_1h" in features.columns
    assert "hour_sin" in features.columns
    assert not features.isnull().any().any()


def test_statistical_model_latency_under_50ms():
    df = generate_synthetic_station_data(station_id="TEST001", days=5, seed=10)
    model = StatisticalDetector().fit(df)
    reading = {"temperature_c": 52.0, "pressure_hpa": 980.0, "humidity_pct": 20.0}

    is_anomaly, conf, trig, latency = model.score_single_point(reading)
    assert latency < 50.0  # Must be strictly under 50ms
    assert is_anomaly is True
    assert "temperature_c" in trig


def test_isolation_forest_normalized_scores():
    df = generate_synthetic_station_data(station_id="TEST001", days=5, seed=10)
    injector = AnomalyInjector(seed=10)
    corrupted, _ = injector.inject(df, {"rate": 0.05})

    model = IsolationForestDetector(n_estimators=30).fit(df)
    is_anomaly, scores = model.predict(corrupted)

    assert len(scores) == len(corrupted)
    assert (scores >= 0.0).all() and (scores <= 1.0).all()


def test_lstm_autoencoder_state_save_load(tmp_path):
    df = generate_synthetic_station_data(station_id="TEST001", days=4, seed=10)
    model = LSTMAutoencoderDetector(epochs=2, batch_size=32).fit(df)

    save_path = tmp_path / "lstm_test.pt"
    model.save_state(save_path)
    assert save_path.exists()

    new_model = LSTMAutoencoderDetector(epochs=2)
    new_model.load_state(save_path)
    assert new_model.fitted is True


def test_hybrid_ensemble_predictions():
    df = generate_synthetic_station_data(station_id="TEST001", days=5, seed=10)
    injector = AnomalyInjector(seed=20)
    corrupted, _ = injector.inject(df, {"rate": 0.04})

    ensemble = HybridEnsembleDetector().fit(df)
    is_anomaly, conf = ensemble.predict(corrupted)

    assert len(is_anomaly) == len(corrupted)
    assert is_anomaly.sum() > 0
    assert (conf >= 0.0).all() and (conf <= 1.0).all()
