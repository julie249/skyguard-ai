# SkyGuard AI

> **SIH26073**: AI/ML-Based Intelligent Anomaly Detection for Automatic Weather Stations (Ministry of Earth Sciences)

SkyGuard AI is an end-to-end meteorological anomaly detection and self-healing platform. It detects sensor failures (spikes, stuck values, dropouts, calibration drift, noise bursts) across Automatic Weather Station (AWS) networks using temperature (°C), atmospheric pressure (hPa), and relative humidity (%).

## Architecture Overview
SkyGuard AI utilizes an intentional microservice architecture:
- **Node.js + Fastify (TypeScript)**: Main backend owning the database, REST API, WebSocket streams, orchestration, and alerting.
- **Python (FastAPI)**: Internal-only ML microservice executing statistical detection, Isolation Forest, LSTM Autoencoders, spatial cross-validation, and SHAP explainability.
- **React + Vite (TypeScript)**: Interactive real-time operations dashboard with geospatial station mapping, time-series visualization, and explainability cards.
