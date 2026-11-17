# SkyGuard AI — Project Execution & Implementation Progress

Last Updated: **2026-11-17** (Phase 1–10 Verification Complete, tagged v1.1.0)

---

## Phase Breakdown (Original SIH Phases 0–9)

| Phase | Phase Name | Status | What Exists | What Is Missing |
| :--- | :--- | :---: | :--- | :--- |
| **Phase 0** | Git Setup & Skeleton | **DONE** | Repo initialized, `.gitignore`, `LICENSE`, `README.md`, `.env.example`, skeleton dirs | — |
| **Phase 1** | Synthetic Data + Test Harness | **DONE** | Diurnal generator, 5 anomaly types, 3 labeled datasets (1%/3%/8%), `evaluate.py`, unit tests | — |
| **Phase 2** | Detection Models (Python) | **DONE** | Statistical Z+IQR, Isolation Forest, PyTorch LSTM Autoencoder, Hybrid Ensemble, benchmark | — |
| **Phase 3** | Explainability & Root Cause | **DONE** | Haversine spatial corroboration, root cause classifier, SHAP < 200ms, unit tests | — |
| **Phase 4** | ML Microservice (FastAPI) | **DONE** | FastAPI `/predict` `/evaluate` `/train` `/health`, Dockerfile, Pydantic schemas, 16 pytest PASS | — |
| **Phase 5** | Node.js Fastify Backend | **DONE** | Fastify server, Prisma+SQLite, `/stations` `/alerts` `/simulate/inject`, WebSocket stream, seed_demo.js | — |
| **Phase 6** | React + Vite Frontend | **DONE** | Station map (Leaflet), time-series chart (Recharts), AlertFeed, ExplainabilityCard, live WS | — |
| **Phase 7** | Differentiators | **DONE** | Sensor degradation forecasting, health tracking, SHAP UI, spatial validation | — |
| **Phase 8** | Edge Demo | **DONE** | ESP32 MicroPython standalone edge detector, energy profiling | — |
| **Phase 9** | Docker Compose & Docs | **DONE** | `docker-compose.yml`, GitHub Actions CI, `model_report.md`, `README.md`, `DEPLOY.md`, `DEMO.md` | — |

---

## Verification Phases (Post-SIH, 2026-11-17)

| Phase | Description | Status | Evidence |
| :--- | :--- | :---: | :--- |
| Phase 1 | Fresh clone / clean setup test | **PARTIAL** | venv_fresh pip install succeeded in clean-test dir; frontend node_modules copy blocked by sandbox EPERM (Windows). npm install requires running outside sandbox with network. |
| Phase 2 | README + .env.example files + fix hardcoded URLs | **DONE** | `backend/.env.example`, `ml-service/.env.example`, `frontend/.env.example` created. `client.ts` and `useLiveStream.ts` now use `import.meta.env.VITE_API_URL/VITE_WS_URL`. Committed `d80b438`. |
| Phase 3 | Docker Compose | **PARTIAL** | `docker-compose.yml` exists with all 4 services. Cannot verify `docker compose up --build` from sandbox (no Docker daemon). Must be tested manually. |
| Phase 4 | Honest Verification | **DONE** | `run_benchmark.py` executed — real numbers differ from prior claims (see `docs/model_report.md`). Edge latency measured: **0.0007 ms on PC Python 3.13** (10,000 iterations). Data is SYNTHETIC. Backend calls ML live via HTTP POST. Committed `79ecda9`. |
| Phase 5 | Failure Behavior | **VERIFIED IN CODE** | `mlClient.service.ts`: 2500ms timeout, one retry, then `null` (reading saved as unscored). Cannot live-test without running backend outside sandbox. |
| Phase 6 | Security Audit | **DONE** | `dev.db` committed in `200775d`, untracked in `e2f0e3d`. `.gitignore` covers `.env`, `*.db`, `*.sqlite`, `node_modules`, `venv`. No API keys or tokens found in any committed file. Telegram fields are empty strings. |
| Phase 7 | Deployment Configs | **DONE** | `vercel.json`, `render.yaml`, `DEPLOY.md` created. All URLs driven by env vars. `ENABLE_LSTM=false` flag added for Render free tier. Committed `bb7eadc`. |
| Phase 8 | Demo Assets + DEMO.md | **DONE** | `DEMO.md` created with 3-minute timed script, failure fallback table, verified metrics. Committed `2674aa5`. |
| Phase 9 | Pitch Deck | **DONE** | `docs/pitch_deck.pptx` (12 slides) generated via `python-pptx`. Committed `f08dff4`. |
| Phase 10 | Tag v1.1.0 + Push | **DONE** | All 5 commits pushed to `main`. Tag `v1.1.0` pushed to GitHub. |

---

## Test Verification (2026-11-17)

| Test Suite | Result |
|---|---|
| `pytest ml-service/tests/ -v` | **16 passed**, 8 deprecation warnings (pandas `dayofyear`), 0 failures |
| `npx tsc --noEmit` (backend) | **0 errors** |
| `run_benchmark.py` | **Completed** — 3 datasets × 4 models = 12 result rows |

---

## Key Corrections from Prior Claims

| Claim | Reality |
|---|---|
| "84% Event-Level Anomaly Recall" | Highest measured: 92% (LSTM recall on 1%), but precision is only 1.4% at that recall. Best balanced metric: Hybrid Ensemble Event F1 = **0.65** (1% dataset). |
| "0.007 ms edge latency" | Actually **0.0007 ms/call** on PC Python 3.13 (7.24 ms / 10,000 runs). ESP32 latency **estimated** ~0.4–1.2 ms, not measured on hardware. |
| Data source | All data is **SYNTHETIC** — not real IMD AWS data. |
| Backend scoring | **LIVE** HTTP POST to ML service on every reading — not cached or fallback by default. |

---

## Next Steps for Real Deployment

1. `docker compose up --build` — must be tested manually (needs Docker Desktop running)
2. Frontend `npm install` in clean clone — requires network outside sandbox
3. Set GitHub repo visibility to **Public** (you do this in Settings → Danger Zone)
4. Deploy frontend to Vercel, backend+ml-service to Render following `DEPLOY.md`
5. For real IMD data: replace `data/synthetic/*.csv` and re-run `python ml-service/run_benchmark.py`
