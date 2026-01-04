@echo off
echo Starting Arq Worker...
uv run arq backend.worker.WorkerSettings --watch backend
pause
