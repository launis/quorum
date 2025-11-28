@echo off
echo Starting Cognitive Quorum v2 (Local Mode)...

REM Start Backend
start "Cognitive Quorum Backend" cmd /k "uvicorn src.api.server:app --reload --port 8000"

REM Wait a bit for backend to start
timeout /t 5

REM Start Frontend
start "Cognitive Quorum Frontend" cmd /k "streamlit run ui.py"

echo.
echo Services started!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:8501
echo.
pause
