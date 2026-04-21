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

RUN rm -f .env

RUN adduser -D -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
