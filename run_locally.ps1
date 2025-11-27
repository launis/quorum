# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# Start Backend in background
Write-Host "Starting Backend..."
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn backend.main:app --host 0.0.0.0 --port 8000" -PassThru -NoNewWindow

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend..."
# Set environment variable for frontend to find backend
$env:API_URL = "http://localhost:8000"
python -m streamlit run frontend/app.py --server.port 8501

# Cleanup on exit (this part is tricky in simple scripts, user might need to kill backend manually if script stops abruptly, but we'll try)
Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
