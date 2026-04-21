# ── Stage 1: Builder ──────────────────────────────────────
FROM python:3.12-alpine AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Final image ──────────────────────────────────
FROM python:3.12-alpine

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

RUN adduser -D -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python3 -c "import redis, os; r = redis.Redis(host=os.getenv('REDIS_HOST','redis')); r.ping()" || exit 1

CMD ["python3", "worker.py"]
