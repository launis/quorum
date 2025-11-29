@echo off
echo Starting Cognitive Quorum v2 (Local Mode)...
chcp 65001
set PYTHONIOENCODING=utf-8

REM Start Backend
start "Cognitive Quorum Backend" cmd /k "chcp 65001 && uvicorn src.api.server:app --reload --port 8000"

REM Wait a bit for backend to start
timeout /t 5

REM Start Frontend
start "Cognitive Quorum Frontend" cmd /k "chcp 65001 && streamlit run ui.py"

echo.
echo Services started!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:8501
echo.
pause
