
import os
import sys
import traceback
from pathlib import Path

import uvicorn

# Setup Path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

log_file = project_root / "server_startup.log"

def main():
    print(f"DEBUG: Starting Backend Server Simulation... Logging to {log_file}")

    # 1. Set Env Vars (Simulate run_local.bat)
    os.environ["USE_MOCK_DB"] = "false"
    os.environ["USE_MOCK_LLM"] = "false"
    os.environ["STORAGE_BACKEND"] = "LOCAL"
    os.environ["USE_VERTEX_LLM"] = "true"
    os.environ["USE_FIREBASE_AUTH"] = "true"

    # Intentionally do NOT set GOOGLE_APPLICATION_CREDENTIALS to test the fix?
    # No, run_local.bat sets it. Let's set it to be faithful to the user's environment,
    # OR rely on auto-discovery if run_local.bat fails to set it properly.
    # The user said "service-account.json on juuressa", so run_local.bat's "%CD%\service-account.json"
    # should work if %CD% is correct.
    # Let's verify the auto-discovery by NOT setting it here, forcing the fix to work.
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(project_root / "service-account.json")

    try:
        # Import app JUST BEFORE running to catch import-time errors inside the try/except
        from backend.main import app

        # Configure logging
        # We can't easily use the yaml config here without uvicorn command line,
        # but we can run uvicorn.run

        with open(log_file, "w") as f:
            f.write("Starting Uvicorn...\n")

        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
        # Port 8001 to avoid conflict if the other one IS running (unlikely)

    except Exception as e:
        print(f"FAILURE: Server Crash: {e}")
        with open(log_file, "a") as f:
            f.write(f"\nCRITICAL ERROR: {e}\n")
            traceback.print_exc(file=f)

if __name__ == "__main__":
    main()
