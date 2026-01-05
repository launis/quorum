@echo off

REM ========================================================
REM  RUN LIVE LLM TESTS (REAL COST, MOCK DB) - SAFE MODE
REM ========================================================

pushd %~dp0\..

echo.
echo ========================================================
echo  WARNING: LIVE LLM TESTING
echo ========================================================
echo.
echo  This will make REAL calls to Gemini/Vertex AI.
echo  It will incur COSTS.
echo.
echo  Database: MOCK (Safe)
echo.

REM Set Environment for Safe Runner but override LLM Mode
set USE_MOCK_LLM=false
set USE_MOCK_DB=true
set TESTING=true

REM We still use the safe runner, but it needs to respect the ENV vars we set here.
REM run_tests_safely.py copies os.environ, so this works.
REM Use specific marker for live tests to avoid running EVERYTHING against paying API.
uv run scripts/run_tests_safely.py -m live

popd

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Live tests passed!
) else (
    echo.
    echo [FAILURE] Live tests failed.
)
pause
