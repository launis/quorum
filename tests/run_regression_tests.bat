@echo off

REM ========================================================
REM  RUN FULL REGRESSION SUITE (SAFE MODE)
REM ========================================================
REM Delegates to the central python safety wrapper to ensure 
REM correct environment (TESTING=true) and signal handling.

pushd %~dp0\..

echo.
echo ========================================================
echo  RUNNING FULL REGRESSION SUITE (SAFE WRAPPER)
echo ========================================================
echo.

uv run scripts/run_tests_safely.py

popd

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] All tests passed!
) else (
    echo.
    echo [FAILURE] Tests failed. Check output above.
)
pause
