FROM python:3.14

WORKDIR /app

# Install system dependencies for WeasyPrint (PDF generation)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 quorum

# Install uv directly into the image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies using uv (respects cross-platform uv.lock) and assign non-root ownership
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project \
    && chown -R quorum:quorum /app/.venv

# Copy application code to root /app with non-root ownership
COPY --chown=quorum:quorum backend_v2 /app/backend_v2

# Configure pre-built .venv environment and Cloud Run default port
ENV PYTHONPATH=/app \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    UV_NO_SYNC=1 \
    UV_OFFLINE=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    PORT=8000

USER quorum

# Execute pre-built uvicorn directly on Cloud Run ${PORT} without --reload or runtime uv sync
CMD ["sh", "-c", "exec /app/.venv/bin/uvicorn backend_v2.main:app --host 0.0.0.0 --port ${PORT}"]
