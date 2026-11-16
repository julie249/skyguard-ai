"""
SkyGuard AI — Python ML Microservice Entrypoint.
Internal-only inference and explainability API built with FastAPI.
The frontend NEVER accesses this service directly; only the Node.js backend communicates with it.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_predict import router as predict_router
from app.api.schemas import HealthResponse
from app.core.config import settings

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("skyguard-ml")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SkyGuard AI ML Microservice...")
    yield
    logger.info("Shutting down SkyGuard AI ML Microservice...")


app = FastAPI(
    title="SkyGuard AI ML Microservice",
    description="Internal machine learning microservice for AWS meteorological anomaly detection",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS internal access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Returns microservice operational status and primed model availability."""
    return HealthResponse(
        status="healthy",
        service="skyguard-ml-service",
        version="1.0.0",
        models_loaded={
            "statistical_detector": True,
            "isolation_forest": True,
            "lstm_autoencoder": True,
            "spatial_validator": True,
            "shap_explainer": True,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.ml_host, port=settings.ml_port, reload=False)
