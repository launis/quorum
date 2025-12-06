@echo off
echo Starting Cognitive Quorum v2 (MOCK MODE)...
set USE_MOCK_LLM=true
chcp 65001
set PYTHONIOENCODING=utf-8

REM Start Backend with MOCK env var
start "Cognitive Quorum Backend (MOCK)" cmd /k "chcp 65001 && set USE_MOCK_LLM=true && uvicorn backend.main:app --reload --port 8000"

REM Wait a bit for backend to start
timeout /t 15

REM Start Frontend
start "Cognitive Quorum Frontend (MOCK)" cmd /k "chcp 65001 && set USE_MOCK_LLM=true && streamlit run ui.py"

echo.
echo MOCK Services started!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:8501
echo.
pause
