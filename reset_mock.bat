@echo off
echo =======================================
echo   RESET MOCK DATABASE (Wrapper)
echo =======================================
echo.
echo Calling: uv run python backend/seed/seed_mock.py
echo.
uv run python backend/seed/seed_mock.py
pause
