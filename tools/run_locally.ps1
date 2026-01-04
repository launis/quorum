# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

# Check version
uv version | Out-Null
if ($LastExitCode -ne 0) {
    Write-Host "Installing uv..."
    pip install uv
}

# Sync and install dependencies
Write-Host "Syncing environment..."
uv sync

# Install dependencies
Write-Host "Syncing dependencies with uv..."
uv sync

# Start Backend in background
Write-Host "Starting Backend..."
$backendProcess = Start-Process -FilePath "cmd" -ArgumentList "/k title Cognitive Quorum Backend && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000" -PassThru

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend
# Start Frontend in a new window
Write-Host "Starting Frontend..."
# Set environment variable for frontend to find backend
$env:API_URL = "http://localhost:8000"
$frontendProcess = Start-Process -FilePath "cmd" -ArgumentList "/k title Cognitive Quorum Frontend && python -m streamlit run ui.py --server.port 8501" -PassThru

# Wait for the frontend window to be closed
Write-Host "Both services are running in separate windows."
Write-Host "Close the Frontend window to stop the Backend and exit."
Wait-Process -Id $frontendProcess.Id

# Cleanup on exit
Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
