@echo off
set USE_MOCK_DB=false
set STORAGE_BACKEND=LOCAL
set GOOGLE_APPLICATION_CREDENTIALS=service-account.json
uv run python debug_settings.py > debug_out.txt 2>&1
type debug_out.txt
