@echo off
echo Starting Cognitive Quorum v2 (MOCK LLM / Offline Mode)...
echo.
echo [INFO] MODE: MOCK LLM (Local Database)
echo [INFO] No real API calls will be made. No costs.
echo [INFO] Data is saved LOCALLY to 'data/db_mock.json'.
echo [INFO] Responses are generated from local templates.
echo.
echo [TIP]  Look for YELLOW text "[MOCK RESPONSE]" in the backend logs
echo        to confirm you are running in Mock mode.
echo.
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
