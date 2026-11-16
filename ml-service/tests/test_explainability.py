import pytest
import time
from app.src.spatial_consistency import SpatialConsistencyValidator, haversine_distance_km
from app.src.root_cause_classifier import RootCauseClassifier
from app.src.explainability import ExplainabilityEngine


def test_haversine_distance():
    # Delhi Ridge to Palam Airport is roughly 11-13 km
    dist = haversine_distance_km(28.6139, 77.2090, 28.5665, 77.1031)
    assert 10.0 <= dist <= 15.0


def test_spatial_consistency_corroboration():
    validator = SpatialConsistencyValidator()
    target_reading = {"temperature_c": 48.0, "pressure_hpa": 1005.0}

    # Case A: Neighbors corroborate (genuine extreme heatwave)
    corroborating_neighbors = [
        {"station_id": "AWS002", "temperature_c": 47.5},
        {"station_id": "AWS003", "temperature_c": 48.2},
    ]
    res_a = validator.compute_spatial_agreement("AWS001", target_reading, corroborating_neighbors)
    assert res_a["is_corroborated"] is True
    assert res_a["agreement_score"] == 1.0

    # Case B: Isolated sensor failure (neighbors report 30°C)
    disagreeing_neighbors = [
        {"station_id": "AWS002", "temperature_c": 30.0},
        {"station_id": "AWS003", "temperature_c": 30.5},
    ]
    res_b = validator.compute_spatial_agreement("AWS001", target_reading, disagreeing_neighbors)
    assert res_b["is_corroborated"] is False
    assert res_b["agreement_score"] == 0.0


def test_root_cause_classification_rules():
    reading = {"temperature_c": 45.0, "pressure_hpa": 1010.0, "humidity_pct": 50.0}

    # Rule 1: Dropout -> comms_error
    rc1 = RootCauseClassifier.classify("dropout", {"temperature_c": -99.9}, ["temperature_c"])
    assert rc1 == "comms_error"

    # Rule 2: Stuck sensor -> sensor_fault
    rc2 = RootCauseClassifier.classify("stuck", reading, ["temperature_c"])
    assert rc2 == "sensor_fault"

    # Rule 3: Drift -> sensor_fault
    rc3 = RootCauseClassifier.classify("drift", reading, ["temperature_c"])
    assert rc3 == "sensor_fault"

    # Rule 4: Isolated spike (repudiated by neighbors) -> sensor_fault
    spatial_isolated = {"is_corroborated": False, "agreement_score": 0.0}
    rc4 = RootCauseClassifier.classify("spike", reading, ["temperature_c"], spatial_isolated)
    assert rc4 == "sensor_fault"

    # Rule 5: Extreme co-occurring weather (corroborated by neighbors) -> genuine_extreme
    spatial_corroborated = {"is_corroborated": True, "agreement_score": 1.0}
    rc5 = RootCauseClassifier.classify("spike", reading, ["temperature_c"], spatial_corroborated)
    assert rc5 == "genuine_extreme"


def test_shap_explanation_latency_under_200ms():
    engine = ExplainabilityEngine()
    reading = {"temperature_c": 49.5, "pressure_hpa": 1008.0, "humidity_pct": 25.0}

    start = time.perf_counter()
    explanation = engine.explain(reading, ["temperature_c"])
    latency_ms = (time.perf_counter() - start) * 1000.0

    assert latency_ms < 200.0  # Must be strictly under 200ms
    assert "temperature_c" in explanation["feature_contributions"]
    assert len(explanation["summary"]) > 10
    assert explanation["feature_contributions"]["temperature_c"] > 0.0
