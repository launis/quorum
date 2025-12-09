@echo off
echo Starting Cognitive Quorum v2 (Real LLM / Connects to APIs)...
echo.
echo [INFO] MODE: REAL LLM (Local Database)
echo [INFO] This mode WILL make real API calls to Google/OpenAI.
echo [INFO] Data is saved LOCALLY to 'data/db_mock.json'.
echo [INFO] Costs may apply for LLM usage.
echo.
echo [TIP]  If you see "[MOCK RESPONSE]" in the logs, you are in the wrong mode.
echo        In this mode, logs should show real execution time and varying scores.
echo.
set USE_MOCK_LLM=false
chcp 65001
set PYTHONIOENCODING=utf-8

REM Start Backend
start "Cognitive Quorum Backend" cmd /k "chcp 65001 && set USE_MOCK_LLM=false && uvicorn backend.main:app --reload --port 8000"

REM Wait a bit for backend to start
timeout /t 15

REM Start Frontend
start "Cognitive Quorum Frontend" cmd /k "chcp 65001 && set USE_MOCK_LLM=false && streamlit run ui.py"

echo.
echo Services started!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:8501
echo.
pause
