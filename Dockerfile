# Multi-stage Dockerfile for Molavi Web Intelligence Engine (MWIE)
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir hatchling

FROM python:3.12-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . /app

RUN pip install --no-cache-dir .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    MWIE_HOST=0.0.0.0 \
    MWIE_PORT=8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "mwie.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
