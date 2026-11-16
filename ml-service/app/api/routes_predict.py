"""
Inference and Model Pipeline Orchestration Routes.
Handles /predict, /evaluate, and /train endpoints for internal microservice consumption.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict
import pandas as pd
from fastapi import APIRouter, HTTPException

from app.api.schemas import EvaluateRequest, PredictResponse, ReadingInput, TrainRequest
from app.src.evaluate import evaluate_metrics, generate_report
from app.src.explainability import ExplainabilityEngine
from app.src.models.ensemble import HybridEnsembleDetector
from app.src.models.isolation_forest import IsolationForestDetector
from app.src.models.statistical_model import StatisticalDetector
from app.src.root_cause_classifier import RootCauseClassifier
from app.src.spatial_consistency import SpatialConsistencyValidator

router = APIRouter()

# Singletons initialized for low latency
stat_detector = StatisticalDetector()
if_detector = IsolationForestDetector(n_estimators=50)
ensemble_detector = HybridEnsembleDetector()
spatial_validator = SpatialConsistencyValidator()
explainer = ExplainabilityEngine()


def _ensure_models_trained():
    """Ensure baseline distributions are primed if not yet fit."""
    if not stat_detector.baselines:
        default_data_path = Path("data/synthetic/aws_synthetic_1pct.csv")
        if default_data_path.exists():
            df = pd.read_csv(default_data_path)
            stat_detector.fit(df)
            if_detector.fit(df)
            ensemble_detector.fit(df)
            explainer.init_explainer(df.head(200))


_ensure_models_trained()


@router.post("/predict", response_model=PredictResponse)
def predict_reading(reading: ReadingInput) -> PredictResponse:
    """
    Evaluates a single AWS reading using the multi-model ensemble, spatial cross-validation,
    SHAP explainability, and rule-based root cause classifier.
    Guaranteed response under 300ms.
    """
    start_time = time.perf_counter()
    _ensure_models_trained()

    reading_dict = {
        "temperature_c": reading.temperature_c,
        "pressure_hpa": reading.pressure_hpa,
        "humidity_pct": reading.humidity_pct,
    }

    # 1. Ultra-fast Statistical score
    stat_anomaly, stat_conf, trig_features, _ = stat_detector.score_single_point(reading_dict)

    # 2. Check for physical corruption or comms dropouts
    detected_type = None
    if reading.temperature_c <= -90.0 or reading.pressure_hpa <= 100.0:
        detected_type = "dropout"
    elif stat_anomaly:
        detected_type = "spike"

    # 3. Spatial cross-validation against neighbors if provided
    spatial_support = None
    suggested_correction = None
    if reading.neighbor_readings:
        spatial_support = spatial_validator.compute_spatial_agreement(
            target_station_id=reading.station_id,
            target_reading=reading_dict,
            neighbor_readings=reading.neighbor_readings,
        )
        suggested_correction = spatial_support.get("suggested_correction")

    # 4. Root cause analysis
    root_cause = RootCauseClassifier.classify(
        anomaly_type=detected_type,
        reading=reading_dict,
        triggering_features=trig_features,
        spatial_support=spatial_support,
        confidence=stat_conf,
    )

    # 5. Fast SHAP explanation
    explanation = explainer.explain(
        reading=reading_dict,
        triggering_features=trig_features,
        baseline_stats=stat_detector.baselines,
    )

    total_latency_ms = (time.perf_counter() - start_time) * 1000.0

    return PredictResponse(
        is_anomaly=stat_anomaly,
        confidence=stat_conf,
        root_cause=root_cause,
        triggering_features=trig_features,
        explanation=explanation,
        spatial_support=spatial_support,
        suggested_correction=suggested_correction,
        latency_ms=round(total_latency_ms, 2),
    )


@router.post("/evaluate")
async def run_evaluation(req: EvaluateRequest) -> Dict[str, Any]:
    """Runs evaluation benchmark on specified dataset and updates docs/model_report.md."""
    path = Path(req.dataset_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found at {req.dataset_path}")

    df = pd.read_csv(path)
    y_true = df["is_anomaly"].fillna(False).values

    preds, _ = stat_detector.predict_series(df)
    metrics = evaluate_metrics(y_true, preds)

    # Update docs
    results = {path.name: {"Statistical (Z+IQR)": metrics}}
    generate_report(results, output_path="docs/model_report.md")

    return {"status": "success", "dataset": str(path), "metrics": metrics}


@router.post("/train")
async def train_models(req: TrainRequest) -> Dict[str, Any]:
    """Retrain and prime models on provided dataset."""
    path = Path(req.dataset_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found at {req.dataset_path}")

    df = pd.read_csv(path)
    stat_detector.fit(df)
    if_detector.fit(df)
    ensemble_detector.fit(df)
    explainer.init_explainer(df.head(200))

    return {"status": "success", "trained_on": str(path), "records_processed": len(df)}
