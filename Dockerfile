# =============================================================================
# GeneralDataPlatform — multi‑stage production Dockerfile
# 1. Build the Vite frontend (Node)
# 2. Copy it into the Python backend image
# =============================================================================

# ---- Stage 1: Frontend build -----------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /build/frontend

# Leverage Docker layer cache for npm deps
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Build the SPA
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Python backend + frontend assets -----------------------------
FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend source
COPY backend/ .

# Frontend build artifacts from stage 1
COPY --from=frontend-builder /build/frontend/dist /app/static

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
