@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

REM ========================================================
REM  RUN LIVE LLM TESTS (REAL COST, MOCK DB)
REM ========================================================

REM Navigate to Project Root
pushd %~dp0\..

echo.
echo ========================================================
echo  WARNING: LIVE LLM TESTING
echo ========================================================
echo  This will make REAL calls to Gemini/Vertex AI.
echo  It will incur COSTS.
echo.
echo  Database: MOCK (Safe)
echo ========================================================
echo.

set USE_MOCK_LLM=false
set USE_MOCK_DB=true

echo.
echo ========================================================
echo  TESTS COMPLETED
echo ========================================================
echo.
echo NOTE: Please close the "Backend (LIVE LLM)" window manually when done.
pause
