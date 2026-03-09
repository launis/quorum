FROM python:3.13

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

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools && pip install --no-cache-dir -r requirements.txt

# Copy application code to root /app
COPY . /app

# Set Python path so 'backend' package is resolvable
ENV PYTHONPATH=/app

# Start the application
# We are in /app, so 'backend' is a package.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
