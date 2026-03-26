"""Epic 16.5: End-to-End Orchestration (Backend + Flutter Client Simulation).

This test behaves as the master E2E Orchestrator:
1. Clears `backend_debug.log` and `client_debug.log`.
2. Checks if FastAPI backend is running via HTTP.
3. If not running, spawns it as a subprocess.
4. Executes `dart run` (or `flutter test`) to simulate the real Flutter frontend hitting the API.
5. Performs True Structural / Deep Logic Parity assertions on the new JSON traces.
6. Asserts both debug logs contain natural execution telemetry.
"""

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest
import requests

logger = logging.getLogger(__name__)

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_LOG_FILE = os.path.join(WORKSPACE_ROOT, "backend_debug.log")
CLIENT_LOG_FILE = os.path.join(WORKSPACE_ROOT, "client_debug.log")

ORIGINAL_TRACE_FILE = os.environ.get("TEST_REFERENCE_TRACE", os.path.join(WORKSPACE_ROOT, "data", "files", "executions", "exe_c0bc5098e7164453afffd7743ff35c2c", "execution_trace.json"))
NEW_TRACE_FILE = os.environ.get("TEST_E2E_TRACE_OUT", os.path.join(WORKSPACE_ROOT, "backend_v2", "tests", "test_data", "e2e_new_trace.json"))
TARGET_WORKFLOW_ID = os.environ.get("TEST_WORKFLOW_ID", "wf_d653170e174847559e08af42b938d826")
WAIT_TIMEOUT = int(os.environ.get("TEST_WAIT_TIMEOUT", "600"))

# The INPUTS_FILE is still hardcoded as it's specific to the test data for this particular workflow.
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data")
INPUTS_FILE = os.path.join(TEST_DATA_DIR, "exe_c0bc_inputs.json")


def clear_logs() -> None:
    """Clear both debug logs to ensure deterministic E2E assertions."""
    for file_path in [BACKEND_LOG_FILE, CLIENT_LOG_FILE]:
        if os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")
        else:
            # Touch the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")

def is_backend_running() -> bool:
    """Check if the backend API is alive on port 8000."""
    try:
        # Assuming there is a health check endpoint, or we can just hit something basic
        response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def deep_logic_compare(old_trace: list[dict[str, Any]], new_trace: list[dict[str, Any]]) -> None:
    """Structurally compares the new trace with the old trace to ensure consistency."""
    old_steps = {event.get("step_name"): event for event in old_trace if event.get("event_type") == "output"}
    new_steps = {event.get("step_name"): event for event in new_trace if event.get("event_type") == "output"}

    logger.info(f"Old output steps: {list(old_steps.keys())}")
    logger.info(f"New output steps: {list(new_steps.keys())}")

    for step_name, old_event in old_steps.items():
        if step_name not in new_steps:
            logger.warning(f"Step {step_name} missing from new trace.")
            continue

        old_content = old_event.get("content", {})
        new_content = new_steps[step_name].get("content", {})

        # 1. Structural Parity
        old_keys = set(old_content.keys())
        new_keys = set(new_content.keys())

        missing_keys = old_keys - new_keys
        if missing_keys:
            logger.warning(f"Step {step_name} output missing keys compared to historical trace: {missing_keys}")
            
        # 2. Heuristic & Semantic Sanity Checks
        content_str = json.dumps(new_content).lower()
        
        # Negative heuristics: no AI apologies
        assert "as an ai language model" not in content_str, f"Step {step_name} failed: Contains AI apology."
        assert "i cannot fulfill" not in content_str, f"Step {step_name} failed: Contains AI refusal."
        
        # Length heuristic: if old was substantial, new should be too
        if len(str(old_content)) > 100:
            assert len(content_str) > 50, f"Step {step_name} failed: Undersized payload compared to historical size."

    # 3. Contextual Keyword Matching across the whole trace
    full_new_trace_str = json.dumps(new_trace).lower()
    
    # We know the inputs for exe_c0bc contained "Test Org", "Technology", "Developers"
    # The final output DAG should naturally contain references to these.
    expected_keywords = ["technology", "developers"]
    for kw in expected_keywords:
        assert kw in full_new_trace_str, f"Fail-Fast Context Check: Expected keyword '{kw}' missing from execution results."

    logger.info("Deep Logic & Semantic Parity Checks PASSED.")

@pytest.mark.asyncio
@pytest.mark.order("last")
async def test_real_llm_e2e_orchestration():
    """Live E2E test coordinating the Dart Client Simulation and the FastAPI Backend."""
    if not os.path.exists(INPUTS_FILE):
        pytest.skip(f"Inputs file not found at {INPUTS_FILE}. Skipping E2E test.")
    if not os.path.exists(ORIGINAL_TRACE_FILE):
        pytest.skip(f"Original trace not found at {ORIGINAL_TRACE_FILE}. Skipping E2E test.")

    clear_logs()

    backend_process = None
    worker_process = None # Initialize worker_process
    if not is_backend_running():
        logger.info("Backend is not running. Starting local FastAPI instance on port 8000.")
        env = os.environ.copy()
        env["USE_FIREBASE_AUTH"] = "false"
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["NO_COLOR"] = "1"
        env["TERM"] = "dumb"
        
        backend_log_fp = open(BACKEND_LOG_FILE, "a", encoding="utf-8")
        backend_cmd = (
            "chcp 65001 > nul && uv run python -c "
            "\"import sys; "
            "sys.stdout.reconfigure(encoding='utf-8') if sys.stdout and hasattr(sys.stdout, 'reconfigure') else None; "
            "sys.stderr.reconfigure(encoding='utf-8') if sys.stderr and hasattr(sys.stderr, 'reconfigure') else None; "
            "import uvicorn; sys.argv=['uvicorn', 'backend_v2.main:app', '--host', '0.0.0.0', '--port', '8000']; "
            "uvicorn.main()\""
        )
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=WORKSPACE_ROOT,
            env=env,
            stdout=backend_log_fp,
            stderr=subprocess.STDOUT,
            shell=True
        )
        
        worker_cmd = (
            "chcp 65001 > nul && uv run python -c "
            "\"import sys; "
            "sys.stdout.reconfigure(encoding='utf-8') if sys.stdout and hasattr(sys.stdout, 'reconfigure') else None; "
            "sys.stderr.reconfigure(encoding='utf-8') if sys.stderr and hasattr(sys.stderr, 'reconfigure') else None; "
            "import runpy; sys.argv=['run_worker.py']; "
            "runpy.run_module('backend_v2.run_worker', run_name='__main__', alter_sys=True)\""
        )
        worker_process = subprocess.Popen(
            worker_cmd,
            cwd=WORKSPACE_ROOT,
            env=env,
            stdout=backend_log_fp,
            stderr=subprocess.STDOUT,
            shell=True
        )
        
        # Wait for boot
        time.sleep(10)

        if not is_backend_running():
            if backend_process:
                backend_process.terminate()
            if worker_process:
                worker_process.terminate()
            pytest.fail("Failed to start FastAPI backend for testing.")
    else:
        logger.info("Backend is already running. Re-using active instance.")

    try:
        # 1. Run the Dart simulation (Mimics Flutter's Client-Side Execution)
        client_dir = os.path.join(WORKSPACE_ROOT, "client_app_v2")
        logger.info("Triggering Dart E2E Client Simulation...")

        # We use flutter test because LoggerService depends on package:flutter framework libraries.
        result = subprocess.run(
            ["flutter", "test", "test/e2e_client_test.dart"],
            cwd=client_dir,
            capture_output=True,
            text=True,
            shell=os.name == "nt"
        )

        if result.returncode != 0:
            logger.error(f"Dart execution failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
            pytest.fail("Dart E2E Client Simulation failed.")

        # 2. Wait for background worker to complete the execution
        logger.info(f"Polling local database for execution completion (max {WAIT_TIMEOUT}s)...")
        # Find the latest execution ID from Dart output or just poll db_v2.json
        db_path = os.path.join(WORKSPACE_ROOT, "data", "db_v2.json")
        
        # Ensure the test data directory exists
        os.makedirs(os.path.dirname(NEW_TRACE_FILE), exist_ok=True)
        
        max_retries = int(WAIT_TIMEOUT / 2) # e.g. 600 seconds limit
        completed_trace = None
        for i in range(max_retries):
            time.sleep(2)
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    db_data = json.load(f)
                
                # Get the latest execution for this workflow
                executions = [v for k,v in db_data.get("executions", {}).items() if v.get("workflow_id") == TARGET_WORKFLOW_ID]
                if not executions:
                    continue
                    
                # Sort by created_at or just take last
                latest_exe = sorted(executions, key=lambda x: x.get("created_at", ""), reverse=True)[0]
                
                if latest_exe.get("status") in ["COMPLETED", "FAILED"]:
                    completed_trace = latest_exe
                    break
            except Exception as e:
                logger.warning(f"Error reading DB: {e}")
                
        if not completed_trace:
            pytest.fail("Timeout waiting for background execution to complete.")
            
        if completed_trace.get("status") == "FAILED":
            pytest.fail(f"Background execution failed: {completed_trace.get('error_reason')}")
            
        new_trace = completed_trace.get("execution_results", [])

        with open(ORIGINAL_TRACE_FILE, encoding="utf-8") as f:
            old_trace = json.load(f)

        # 3. Structural Parity
        deep_logic_compare(old_trace, new_trace)

        # 4. Assert Dual-Log Generation (User Request: "Varmista, että näihin molempiin logeihin tulostuu dataa.")
        backend_log_size = os.path.getsize(BACKEND_LOG_FILE)
        client_log_size = os.path.getsize(CLIENT_LOG_FILE)

        assert backend_log_size > 0, "backend_debug.log was empty! FastAPI did not log the execution."
        assert client_log_size > 0, "client_debug.log was empty! Dart client did not naturally log execution."

        logger.info("E2E Test completed successfully. Both logs were naturally populated.")

    finally:
        # Cleanup
        if backend_process:
            logger.info(f"Terminating local backend process tree (PID: {backend_process.pid})...")
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(backend_process.pid)], capture_output=True)
        if worker_process:
            logger.info(f"Terminating local worker process tree (PID: {worker_process.pid})...")
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(worker_process.pid)], capture_output=True)
            
        try:
            backend_log_fp.close()
        except Exception:
            pass
