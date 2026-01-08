FROM python:3.13

WORKDIR /app



# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools && pip install --no-cache-dir -r requirements.txt

# Copy application code to root /app
COPY . /app

# Set Python path so 'backend' package is resolvable
ENV PYTHONPATH=/app

# Start the application
# We are in /app, so 'backend' is a package.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
