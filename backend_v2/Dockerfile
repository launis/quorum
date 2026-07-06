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
    && rm -rf /var/lib/apt/lists/*

# Install uv directly into the image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies using uv (much faster and respects cross-platform uv.lock)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code to root /app
COPY backend_v2 /app/backend_v2

# Set Python path so 'backend' package is resolvable
ENV PYTHONPATH=/app

# Start the application using uv run
# We are in /app, so 'backend' is a package.
CMD ["uv", "run", "uvicorn", "backend_v2.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
