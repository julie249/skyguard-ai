import pytest
from app.api.routes_predict import predict_reading
from app.api.schemas import ReadingInput


def test_predict_reading_normal():
    r = ReadingInput(
        station_id="AWS001",
        timestamp="2026-05-10T12:00:00Z",
        temperature_c=25.0,
        pressure_hpa=1012.0,
        humidity_pct=60.0,
    )
    res = predict_reading(r)
    assert res.latency_ms < 300.0  # Must be strictly under 300ms
    assert 0.0 <= res.confidence <= 1.0
    assert "feature_contributions" in res.explanation
    assert "summary" in res.explanation


def test_predict_reading_spike_sensor_fault():
    r = ReadingInput(
        station_id="AWS001",
        timestamp="2026-05-10T14:00:00Z",
        temperature_c=54.0,  # Extreme spike
        pressure_hpa=1010.0,
        humidity_pct=20.0,
        neighbor_readings=[
            {"station_id": "AWS002", "temperature_c": 28.0},
            {"station_id": "AWS003", "temperature_c": 27.5},
        ],
    )
    res = predict_reading(r)
    assert res.is_anomaly is True
    assert res.root_cause == "sensor_fault"
    assert res.spatial_support["is_corroborated"] is False
    assert res.suggested_correction is not None
    assert 27.0 <= res.suggested_correction <= 28.5


def test_predict_reading_genuine_extreme():
    r = ReadingInput(
        station_id="AWS001",
        timestamp="2026-06-15T15:00:00Z",
        temperature_c=49.0,
        pressure_hpa=998.0,
        humidity_pct=18.0,
        neighbor_readings=[
            {"station_id": "AWS002", "temperature_c": 48.5},
            {"station_id": "AWS003", "temperature_c": 49.2},
        ],
    )
    res = predict_reading(r)
    assert res.is_anomaly is True
    assert res.root_cause == "genuine_extreme"
    assert res.spatial_support["is_corroborated"] is True


def test_predict_reading_comms_dropout():
    r = ReadingInput(
        station_id="AWS001",
        timestamp="2026-05-10T16:00:00Z",
        temperature_c=-99.9,
        pressure_hpa=1012.0,
        humidity_pct=50.0,
    )
    res = predict_reading(r)
    assert res.is_anomaly is True
    assert res.root_cause == "comms_error"
