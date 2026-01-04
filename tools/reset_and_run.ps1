# Stop any running python processes to ensure files aren't locked
Write-Host "Stopping any running Python processes..."
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Remove the existing virtual environment
if (Test-Path ".venv") {
    Write-Host "Removing existing virtual environment (.venv)..."
    Remove-Item -Path ".venv" -Recurse -Force
}

# Run the setup script which will recreate .venv and install dependencies
Write-Host "Starting setup and run script..."
.\run_locally.ps1
