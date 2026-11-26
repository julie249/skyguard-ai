# ── SkyGuard AI · ML Microservice (Python 3.11 + PyTorch CPU) ────────────────
FROM python:3.11-slim

WORKDIR /app

# System deps for numpy/scipy builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps (torch>=2.2.0 is already in requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV ML_HOST=0.0.0.0
ENV ML_PORT=8000
# Set ENABLE_LSTM=false to skip LSTM layer and use Random Forest fallback only
ENV ENABLE_LSTM=true

HEALTHCHECK --interval=20s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
