"""
API Schemas for ML Microservice.
Strictly models canonical AWS readings, neighbor comparisons, prediction outputs, and training requests.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReadingInput(BaseModel):
    station_id: str = Field(..., description="Unique Automatic Weather Station identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    temperature_c: float = Field(..., description="Ambient temperature in degrees Celsius")
    pressure_hpa: float = Field(..., description="Atmospheric barometric pressure in hectopascals")
    humidity_pct: float = Field(..., description="Relative humidity percentage (0-100)")
    neighbor_readings: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Recent co-temporal readings from nearby weather stations"
    )


class PredictResponse(BaseModel):
    is_anomaly: bool = Field(..., description="Whether the reading is classified as an anomaly")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    root_cause: str = Field(..., description="sensor_fault, comms_error, genuine_extreme, or unknown")
    triggering_features: List[str] = Field(default_factory=list, description="Features triggering detection")
    explanation: Dict[str, Any] = Field(..., description="SHAP feature attributions and natural language summary")
    spatial_support: Optional[Dict[str, Any]] = Field(
        default=None, description="Spatial agreement and neighbor corroboration metrics"
    )
    suggested_correction: Optional[float] = Field(
        default=None, description="Self-healing estimated true temperature reading"
    )
    latency_ms: float = Field(..., description="Total inference and explanation pipeline execution time in ms")


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    models_loaded: Dict[str, bool]


class EvaluateRequest(BaseModel):
    dataset_path: Optional[str] = Field(default="data/synthetic/aws_synthetic_3pct.csv")


class TrainRequest(BaseModel):
    dataset_path: Optional[str] = Field(default="data/synthetic/aws_synthetic_1pct.csv")
    epochs: Optional[int] = Field(default=3)
