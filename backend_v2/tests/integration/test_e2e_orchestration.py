import os
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest
import requests

# Paths relative to the project root
PROJECT_ROOT = Path("c:/src/quorum")
BACKEND_LOG = PROJECT_ROOT / "backend_debug.log"
CLIENT_LOG = PROJECT_ROOT / "client_debug.log"
DART_SCRIPT_DIR = PROJECT_ROOT / "client_app_v2"
DART_SCRIPT_PATH = DART_SCRIPT_DIR / "bin" / "e2e_simulation.dart"


def clear_logs() -> Any:
    """Clear both backend and client logs."""
    for log_file in [BACKEND_LOG, CLIENT_LOG]:
        if log_file.exists():
            try:
                # Open in write mode and close immediately to truncate the file
                # This avoids Windows PermissionErrors if the backend is already running and holds a lock.
                open(log_file, "w", encoding="utf-8").close()
                print(f"Cleared content of {log_file}")
            except Exception as e:
                print(f"Failed to clear {log_file}: {e}")


def check_backend_health() -> bool:
    """Check if the backend is already running."""
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


@pytest.mark.order("last")
@pytest.mark.skipif(
    os.environ.get("RUN_E2E_TESTS") != "1",
    reason="Skipped by default to speed up quality gate and prevent log spam. Run with RUN_E2E_TESTS=1",
)
def test_e2e_orchestration() -> None:
    """End-to-End Orchestration Test for V2 Architecture.

    Validates the Fail-Fast doctrine and Single Source of Truth by running a simulated
    Flutter client request against a live FastAPI backend and asserting that both logs
    are correctly populated during the execution flow.
    """
    # 1. Clear previous logs
    clear_logs()

    backend_process = None
    worker_process = None
    started_by_test = False

    try:
        # 2. Liveness Check
        if not check_backend_health():
            print("Backend not running. Starting Backend and Worker...")
            started_by_test = True

            # Start backend
            env = os.environ.copy()
            env["USE_FIREBASE_AUTH"] = "false"
            env["PYTHONUTF8"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"
            env["NO_COLOR"] = "1"
            env["TERM"] = "dumb"
            env["PYTHONPATH"] = str(PROJECT_ROOT)

            backend_log_fp = open(BACKEND_LOG, "a", encoding="utf-8")

            backend_cmd = (
                "chcp 65001 > nul && uv run python -c "
                '"import sys; '
                "sys.stdout.reconfigure(encoding='utf-8') "
                "if sys.stdout and hasattr(sys.stdout, 'reconfigure') else None; "
                "sys.stderr.reconfigure(encoding='utf-8') "
                "if sys.stderr and hasattr(sys.stderr, 'reconfigure') else None; "
                "import uvicorn; sys.argv=['uvicorn', 'backend_v2.main:app', '--host', '0.0.0.0', '--port', '8000']; "
                'uvicorn.main()"'
            )
            backend_process = subprocess.Popen(
                backend_cmd,
                cwd=str(PROJECT_ROOT),
                env=env,
                stdout=backend_log_fp,
                stderr=subprocess.STDOUT,
                shell=True,  # noqa: E501
            )

            # Start worker
            worker_cmd = (
                "chcp 65001 > nul && uv run python -c "
                '"import sys; '
                "sys.stdout.reconfigure(encoding='utf-8') "
                "if sys.stdout and hasattr(sys.stdout, 'reconfigure') else None; "
                "sys.stderr.reconfigure(encoding='utf-8') "
                "if sys.stderr and hasattr(sys.stderr, 'reconfigure') else None; "
                "import runpy; sys.argv=['run_worker.py']; "
                "runpy.run_module('backend_v2.run_worker', run_name='__main__', alter_sys=True)\""
            )
            worker_process = subprocess.Popen(
                worker_cmd, cwd=str(PROJECT_ROOT), env=env, stdout=backend_log_fp, stderr=subprocess.STDOUT, shell=True
            )

            # Wait for backend to be healthy
            max_retries = 30
            for _i in range(max_retries):
                if check_backend_health():
                    print("Backend and Worker started successfully.")
                    break
                time.sleep(1)
            else:
                pytest.fail("Failed to start backend within 30 seconds.")
        else:
            print("Backend is already running. Reusing existing instance.")

        # 3. Execution (Run Dart script)
        print("Running Dart E2E Simulation...")
        dart_cmd = ["dart", "run", "bin/e2e_simulation.dart"]
        result = subprocess.run(
            dart_cmd, cwd=str(DART_SCRIPT_DIR), capture_output=True, text=True, shell=os.name == "nt"
        )

        # Print script output for debugging if it fails
        print("Dart Script STDOUT:", result.stdout)
        print("Dart Script STDERR:", result.stderr)

        # We expect the dart script to either succeed or cleanly fail with known logs.
        # Epic 16 uses real LLM, but here we just need to ensure the logs are populated.
        # But wait, execution will fail if Redis isn't running, etc. If it returns non-zero,
        # we still check the logs because it might test failures too, but it should succeed.
        assert result.returncode == 0, (
            f"Dart simulation script failed.\\nSTDOUT:\\n{result.stdout}\\nSTDERR:\\n{result.stderr}"
        )

        # 4. Validation (Check Logs)
        assert BACKEND_LOG.exists(), "Backend debug log was not created."
        assert CLIENT_LOG.exists(), "Client debug log was not created."

        with open(BACKEND_LOG, encoding="utf-8") as f:
            backend_content = f.read()
            assert len(backend_content) > 0, "Backend log is empty."
            # Verify it processed an execution (DAGExecutor or routing)
            assert (
                "api" in backend_content.lower()
                or "workflow" in backend_content.lower()
                or "execution" in backend_content.lower()
            ), "Backend log does not contain expected execution traces."

        with open(CLIENT_LOG, encoding="utf-8") as f:
            client_content = f.read()
            assert len(client_content) > 0, "Client log is empty."
            assert "E2E Simulation Started" in client_content, "Client log missing start marker."
            assert "E2E Simulation Completed" in client_content, "Client log missing completion marker."

    finally:
        # 5. Cleanup if we started them
        if started_by_test:
            print("Terminating test-started Backend and Worker...")
            if backend_process:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(backend_process.pid)], capture_output=True)
            if worker_process:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(worker_process.pid)], capture_output=True)
                worker_process.wait()
            try:
                backend_log_fp.close()
            except Exception as e:
                print(f"Failed to close backend_log_fp: {e}")
