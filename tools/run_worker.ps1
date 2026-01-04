Write-Host "Starting Arq Worker..."
uv run arq backend.worker.WorkerSettings --watch backend
