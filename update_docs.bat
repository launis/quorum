@echo off
echo Starting Documentation Update (with AI)...
echo Ensure backend is running at http://localhost:8000

python scripts/update_docs.py --ai

if %errorlevel% neq 0 (
    echo Error occurred during update.
    pause
    exit /b %errorlevel%
)

echo Update completed successfully.
echo Starting MkDocs server at http://localhost:8003...
mkdocs serve -a localhost:8003
pause
