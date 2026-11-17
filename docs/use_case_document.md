# SkyGuard AI — Official Brief End-to-End Use Case Document

## Target Problem: SIH26073
**AI/ML-Based Intelligent Anomaly Detection for Automatic Weather Stations (Ministry of Earth Sciences)**

Automatic Weather Stations (AWS) operated across India frequently encounter sensor anomalies caused by electronic noise, battery drain, calibration degradation, communication line drops, or debris obstruction. A critical challenge identified by the Ministry of Earth Sciences (MoES) is distinguishing between:
1. **Severe Sensor Hardware Faults** (e.g. broken thermistor or faulty A/D converter transmitting an unphysical reading).
2. **Genuine Extreme Weather Events** (e.g. intense local heatwaves, microbursts, or sudden frontal squalls).

---

## The Official Brief Reference Scenario: 55°C Reading vs. Neighboring Stations

### Scenario Setup
At 14:00 UTC during pre-monsoon summer, station `AWS001` (New Delhi Ridge) suddenly reports an ambient temperature of **55.4°C**, jumping +27.4°C in a single 10-minute interval.

Without intelligent multi-sensor spatial validation, traditional range-checking or thresholding systems face an operational dilemma:
- Either trigger a high-severity civil weather alarm for an unverified heat record, OR
- Blindly discard the reading, risking the loss of true severe weather detection.

---

## SkyGuard AI End-to-End Execution Trace

### 1. Ingestion & Orchestration (Node.js Fastify Backend)
The reading is ingested via REST or WebSocket into the Node.js backend:
```json
{
  "station_id": "AWS001",
  "timestamp": "2026-05-10T14:00:00Z",
  "temperature_c": 55.4,
  "pressure_hpa": 1009.2,
  "humidity_pct": 21.0
}
```
The Fastify orchestration service stores the reading in PostgreSQL/TimescaleDB and immediately queries the nearest active AWS nodes from `station_metadata.csv` (e.g., `AWS002` Palam Airport at 11.2 km, `AWS003` Noida Sector 62 at 15.6 km).

### 2. Microservice Inference Call (Python FastAPI)
The reading plus neighbor observations are dispatched via internal HTTP POST to `ml-service:8000/predict`:
- **Statistical Gating**: Rolling Z-score exceeds `5.8` ($\ge 3.2$ threshold). Breaches upper IQR bound ($Q3 + 2.2 \times IQR$).
- **Isolation Forest & LSTM-AE**: Flag extreme multivariate sequence reconstruction error.
- **Ensemble Consensus**: Ensemble agreement ratio reaches 100%, yielding a calibrated confidence score of **0.91** (91%).

### 3. Spatial Cross-Validation & Corroboration Engine
The Haversine spatial engine compares `AWS001` with its nearest neighbors:
- `AWS002` (Palam Airport, 11.2 km): reporting **28.1°C** ($\Delta = 27.3^\circ\text{C}$).
- `AWS003` (Noida Sector 62, 15.6 km): reporting **27.6°C** ($\Delta = 27.8^\circ\text{C}$).
- **Spatial Agreement Score**: **0.00** (0/2 stations agree within the 4.5°C tolerance).
- **Corroboration Flag**: `is_corroborated: false`.

### 4. Rule-Based Root Cause Classification
`RootCauseClassifier` evaluates the decision matrix:
- Extreme spike detected + spatial agreement score is 0.00 (repudiated by surrounding network).
- Classification: **`sensor_fault`** (hardware failure/drift, NOT extreme weather).

### 5. SHAP Explainability & Self-Healing Synthesis
- **Feature Contributions**:
  - `temperature_c`: **84.6%**
  - `pressure_hpa`: **9.2%**
  - `humidity_pct`: **6.2%**
- **Human-Readable Summary**:
  > *"Temperature C recorded 55.4°C (30.9°C above station norm), accounting for 84.6% of anomaly attribution score. Repudiated by 2/2 neighboring stations."*
- **Self-Healing Corrected Estimation**:
  $$\hat{T}_{\text{corr}} = \text{mean}(28.1^\circ\text{C}, 27.6^\circ\text{C}) = \mathbf{27.85^\circ\text{C}}$$

### 6. Operational Dispatch
The backend broadcasts the alert via WebSocket to the React frontend dashboard:
- The alert appears on screen with root cause badge `SENSOR_FAULT`.
- The UI displays the SHAP attribution bar chart and marks the corrected temperature estimate labeled as *"Estimated: 27.9°C"*.
- The automated Telegram alert notifies duty meteorologists without sounding false civil alarms.
