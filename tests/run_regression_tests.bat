@echo off

REM ========================================================
REM  RUN FULL REGRESSION SUITE (MOCK MODE)
REM ========================================================

REM Navigate to Project Root
pushd %~dp0\..

echo.
echo ========================================================
echo  RUNNING FULL REGRESSION SUITE (MOCK MODE)
echo ========================================================
echo.
echo  Configuration:
echo  - LLM: MOCK (Offline/Free)
echo  - DB:  MOCK (Safe)
echo.

set USE_MOCK_LLM=true
set USE_MOCK_DB=true
set PYTHONUTF8=1

REM Run everything
uv run pytest tests/ > tests/output/regression_results.txt 2>&1

echo.
echo  DONE.
echo  Check 'tests/output/regression_results.txt' for details.
echo.

popd

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] All tests passed!
) else (
    echo.
    echo [FAILURE] Some tests failed. Check output above.
)
pause
