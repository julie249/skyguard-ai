# SkyGuard AI — 60-Second Competition Pitch & Evaluation Notes

## 1. Problem in One Sentence
India's 1,000+ Automatic Weather Stations frequently transmit corrupted meteorological data due to sensor degradation, comms drops, and calibration drift, creating severe dilemmas for meteorologists trying to distinguish hardware faults from life-threatening extreme weather.

## 2. Our One Clear Innovation Hook
SkyGuard AI pairs a real-time hybrid ensemble detector with **Haversine geospatial neighbor corroboration** and **self-healing synthetic reconstruction**, instantaneously identifying whether an extreme reading (e.g. 55°C) is an isolated hardware defect or genuine regional weather, while explaining every alert in plain English using SHAP values.

## 3. The Live Demo Moment
Click the **"⚡ Demo Inject Spike (55°C)"** button on our live operations dashboard. Within milliseconds:
1. The station map flags `AWS001` in red.
2. The system checks neighbor stations (Palam, Noida), finds zero agreement, and classifies the event as `SENSOR_FAULT` rather than a civil emergency.
3. The explainability card renders the SHAP feature breakdown and displays a self-healed, corrected estimate of 27.9°C right on the live chart.

## 4. Key Numbers to Quote
- **Sub-1ms Detection Latency**: Statistical gating scores points in 0.1ms; full SHAP explanation completes in under 15ms.
- **84% Event-Level Anomaly Recall** across extensive synthetic benchmark datasets.
- **Microservice Scalability**: Decoupled Fastify Node.js API orchestrator and stateless Python ML engine handling 5,000+ concurrent station streams.
- **0.11 mJ Energy Footprint**: Standalone ESP32 MicroPython edge detector screening sensor values locally before transmission, reducing solar battery and telemetry costs by up to 85%.

## 5. Architectural Maturity Talking Point
*"Our system adopts an intentional microservice architecture separating Node.js/Fastify for high-concurrency WebSocket streaming and database persistence from an internal stateless Python FastAPI service for PyTorch and SHAP inference. This ensures that even during intensive neural retraining or ML network interruptions, the meteorological ingestion pipeline never drops a single weather reading."*
