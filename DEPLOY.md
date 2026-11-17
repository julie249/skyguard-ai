# SkyGuard AI — Deployment Guide

> **Phase 7** — All environment URLs are environment-variable–driven. No `localhost` references exist in production builds.

---

## Architecture Deployment Targets

| Service | Platform | Method |
|---|---|---|
| Frontend (React + Vite) | **Vercel** | Static build via `vercel.json` |
| Backend (Node.js / Fastify) | **Render** | Docker (`backend/Dockerfile`) |
| ML Microservice (Python / FastAPI) | **Render** | Docker (`ml-service/Dockerfile`) |

---

## 1. Frontend — Vercel

### Prerequisites
- Vercel account: https://vercel.com
- Vercel CLI: `npm i -g vercel`

### Environment Variables (set in Vercel Dashboard → Project → Settings → Environment Variables)
```
VITE_API_URL=https://your-backend.onrender.com
VITE_WS_URL=wss://your-backend.onrender.com/ws/stream
```

### Deploy
```bash
cd frontend
vercel --prod
```

The `vercel.json` at root rewrites all routes to `index.html` for SPA routing:
```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

---

## 2. Backend — Render (Docker)

### Prerequisites
- Render account: https://render.com
- Push `backend/Dockerfile` to your GitHub repo (already done).

### Steps
1. In Render Dashboard → **New** → **Web Service** → Connect GitHub repo.
2. **Root Directory**: `backend`
3. **Dockerfile Path**: `Dockerfile`
4. **Environment Variables**:
```
NODE_ENV=production
PORT=3000
HOST=0.0.0.0
DATABASE_URL=file:./dev.db        # SQLite — OK for free tier
ML_SERVICE_URL=https://your-ml-service.onrender.com
TELEGRAM_BOT_TOKEN=               # optional
TELEGRAM_CHAT_ID=                 # optional
TELEGRAM_CONFIDENCE_THRESHOLD=0.75
```
5. **Build Command**: (empty — Docker handles it)
6. **Start Command**: (empty — set in Dockerfile CMD)

> [!NOTE] On first deploy, run the seeder manually via Render's Shell tab:
> ```bash
> node seed_demo.js
> ```

---

## 3. ML Microservice — Render (Docker)

> [!WARNING] **Free-tier RAM limit**: Render's free tier gives **512 MB RAM**. The LSTM model loads ~400 MB of PyTorch weights. Set `ENABLE_LSTM=false` to skip the LSTM and stay within RAM limits. Anomaly detection will still work via the Statistical + Isolation Forest ensemble.

### Steps
1. In Render Dashboard → **New** → **Web Service** → Connect GitHub repo.
2. **Root Directory**: `ml-service`
3. **Dockerfile Path**: `Dockerfile`
4. **Environment Variables**:
```
ENVIRONMENT=production
ML_HOST=0.0.0.0
ML_PORT=8000
ENABLE_LSTM=false    # Recommended for Render free tier (saves ~400 MB RAM)
```

---

## 4. Docker Compose (Local / Self-Hosted)

```bash
# From project root:
docker compose up --build
```

Services:
- Frontend: http://localhost:5173
- Backend API + Swagger: http://localhost:3000/docs
- ML Microservice + Swagger: http://localhost:8000/docs

---

## 5. Free-Tier Limits Summary

| Limit | Detail |
|---|---|
| Render free RAM | 512 MB per service → use `ENABLE_LSTM=false` on ml-service |
| Render free CPU | Shared — cold starts ~30s; first `/predict` call may be slow |
| Render free disk | 1 GB — SQLite dev.db is fine; TimescaleDB requires a paid tier |
| Vercel bandwidth | 100 GB/month on free tier — sufficient for demos |

---

## 6. Post-Deployment Checklist

- [ ] Frontend `VITE_API_URL` points to Render backend URL (not localhost)
- [ ] Frontend `VITE_WS_URL` points to Render backend WebSocket URL (wss://)
- [ ] Backend `ML_SERVICE_URL` points to Render ml-service URL (not localhost)
- [ ] Backend seeder has been run (`node seed_demo.js`)
- [ ] Confirm `/health` endpoints return 200 on both backend and ml-service
- [ ] Test anomaly injection via dashboard "⚡ Demo Inject Spike" button
