# SkyGuard AI — 3-Minute Demo Script

> **SIH26073** — AI/ML-Based Anomaly Detection for Automatic Weather Stations (Ministry of Earth Sciences)

---

## Setup Checklist (Before the Presentation)

```bash
# Terminal 1 — ML service
cd ml-service
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Backend
cd backend
npm run dev

# Terminal 3 — Frontend (or use built dist)
cd frontend
npm run dev -- --port 5173
```

Open **http://localhost:5173** in Chrome. Confirm: live connection indicator shows green (WebSocket connected).

---

## Minute 1 — Problem & Dashboard Overview (0:00–1:00)

**Say**: *"India has over 1,000 Automatic Weather Stations feeding real-time data to IMD. When a sensor fails and reports 55°C, meteorologists face a critical question: is this a hardware fault, or the onset of a heatwave requiring a public alert?"*

**Show**:
1. The **station map** — 5 stations pinned across North India (Delhi, Noida, Gurgaon, Faridabad, Ghaziabad).
2. Click **AWS001 (Delhi IGI)** — the right panel shows the live telemetry chart: temperature, pressure, humidity for the last 40 readings.
3. Point to the **Alert Feed** column on the right — existing seeded alerts visible.

---

## Minute 2 — SENSOR_FAULT Demo (1:00–2:00)

**Say**: *"Watch what happens when a sensor transmits a rogue 55°C spike."*

**Click**: The **"⚡ Demo Inject Spike (55°C)"** button (bottom of the left panel or station detail panel).

**Show within 3–5 seconds**:
1. Station `AWS001` turns **red** on the map.
2. The **Alert Feed** shows a new `SENSOR_FAULT` alert: *"Temperature spike (55.0°C) on AWS001. Neighbor stations (Noida, Gurgaon) show normal readings (28–31°C). Spatial disagreement indicates sensor fault. Corrected estimate: 27.9°C."*
3. Click the alert row — the **Explainability Card** expands showing SHAP feature bars: `temperature_z_score` is the dominant feature with high positive contribution.
4. Point to the **Corrected Estimate** field: `27.9°C (self-healed)`.

**Say**: *"Three neighbor stations found no agreement with the spike. Our Haversine-based spatial corroboration instantly classifies this as a sensor fault — not a heatwave — and provides a corrected estimate using the spatial average."*

---

## Minute 3 — GENUINE_EXTREME & Architecture (2:00–3:00)

**Say**: *"Now contrast this with a real extreme event."*

**Show**:
1. Scroll the Alert Feed to the seeded **`GENUINE_EXTREME`** alert for `AWS004` — this shows a microburst event where multiple neighbor stations agree on the extreme values.
2. Point to the architecture diagram (or summarize): *"Our system is a microservice duo: Node.js Fastify handles all WebSocket streams and database writes — it never drops a reading. The Python FastAPI ML engine handles LSTM, Isolation Forest, and SHAP offline from the ingestion pipeline."*
3. If time allows: show **http://localhost:8000/docs** — live Swagger UI for the ML microservice.

**Closing**: *"All data shown today is synthetic — generated with diurnal and seasonal equations matching IMD AWS sensor specs. With real IMD CSV telemetry, you replace the synthetic CSVs in `data/synthetic/` and re-run `python run_benchmark.py`. The pipeline is the same."*

---

## Failure Fallback Plan

| Failure | Fallback |
|---|---|
| Frontend won't start | Open `frontend/dist/index.html` in browser directly |
| Backend crashes | Show Swagger UI at `http://localhost:8000/docs` and POST `/predict` manually |
| ML service OOM | Set `ENABLE_LSTM=false` and restart — Statistical + IF still work |
| WebSocket disconnects | Readings still save to DB; refresh page and reconnect |
| Alert doesn't appear in UI | Check browser console; show the POST `/simulate/inject` response JSON directly |

---

## Key Numbers to Cite (Verified)

| Metric | Value | Source |
|---|---|---|
| Hybrid Ensemble Event F1 (1% fault rate) | **0.6524** | `run_benchmark.py` output |
| LSTM Training Time (CPU, 4 epochs) | **~20–24s** | Measured in benchmark |
| Statistical Gate Latency | **< 1ms** | Measured in `test_statistical_model_latency_under_50ms` |
| SHAP Explanation Latency | **< 200ms** | Measured in `test_shap_explanation_latency_under_200ms` |
| Edge Detector Latency (PC, Python 3.13) | **< 1ms** (measured on PC, **not** ESP32) | `edge/edge_detector.py` |
| Estimated ESP32 MicroPython latency | **~0.4–1.2 ms** | Estimated, not hardware-measured |
| All training data | **SYNTHETIC** | Generated via `generate_datasets.py` |
