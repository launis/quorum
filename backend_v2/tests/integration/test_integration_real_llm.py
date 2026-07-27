"""Epic 16.5: End-to-End Orchestration (PDF Execution Test).

This test validates the FastAPI backend's ability to ingest PDF files via Base64,
perform eager extraction, and execute a full LLM workflow to completion.
"""

import base64
import json
import logging
import os
import subprocess
import time
from pathlib import Path

import fitz  # type: ignore
import pytest
import requests

from backend_v2.models.enums import ExecutionStatus

logger = logging.getLogger(__name__)

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_LOG_FILE = os.path.join(WORKSPACE_ROOT, "backend_debug.log")
TESTILYHYT_DIR = os.path.join(WORKSPACE_ROOT, "docs", "testilyhyt")

TARGET_WORKFLOW_ID = os.environ.get("TEST_WORKFLOW_ID", "wf_d653170e174847559e08af42b938d826")
WAIT_TIMEOUT = int(os.environ.get("TEST_WAIT_TIMEOUT", "3600"))


def clear_logs() -> None:
    """Clear backend debug log."""
    if os.path.exists(BACKEND_LOG_FILE):
        with open(BACKEND_LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")
    else:
        with open(BACKEND_LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")


def is_backend_running() -> bool:
    """Check if the backend API is alive on port 8000 with resilient retry loop."""
    for _ in range(30):
        try:
            response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def get_base64_file(file_path: str) -> str:
    """Read a file and return its base64 encoded string."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_E2E") != "true",
    reason="Live E2E tests skipped by default. Set $env:RUN_LIVE_E2E='true' to run as final Epic verification gate.",
)
@pytest.mark.asyncio
@pytest.mark.order("last")
async def test_real_llm_pdf_execution() -> None:
    """Live E2E test verifying PDF processing via the FastAPI Backend."""
    # Verify PDF files exist
    pdf_files = {
        "chat_log": os.path.join(TESTILYHYT_DIR, "keskusteluhistoriia.pdf"),
        "product_text": os.path.join(TESTILYHYT_DIR, "loppputuote.pdf"),
        "reflection_text": os.path.join(TESTILYHYT_DIR, "reflektio.pdf"),
    }

    for _, path in pdf_files.items():
        if not os.path.exists(path):
            pytest.skip(f"Required PDF not found: {path}. Skipping test.")

    clear_logs()

    backend_process = None
    worker_process = None
    if not is_backend_running():
        logger.info("Backend is not running. Starting local FastAPI instance on port 8000.")
        env = os.environ.copy()
        env.pop("PYTEST_CURRENT_TEST", None)  # CRITICAL: Prevent FakeRedis isolation in subprocesses
        env["USE_FIREBASE_AUTH"] = "false"
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["NO_COLOR"] = "1"
        env["TERM"] = "dumb"

        backend_log_fp = open(BACKEND_LOG_FILE, "a", encoding="utf-8")
        backend_cmd = (
            "chcp 65001 > nul && uv run python -c "
            '"import sys; '
            "sys.stdout.reconfigure(encoding='utf-8') if sys.stdout and hasattr(sys.stdout, 'reconfigure') else None; "
            "sys.stderr.reconfigure(encoding='utf-8') if sys.stderr and hasattr(sys.stderr, 'reconfigure') else None; "
            "import uvicorn; sys.argv=['uvicorn', 'backend_v2.main:app', '--host', '0.0.0.0', '--port', '8000']; "
            'uvicorn.main()"'
        )
        backend_process = subprocess.Popen(
            backend_cmd, cwd=WORKSPACE_ROOT, env=env, stdout=backend_log_fp, stderr=subprocess.STDOUT, shell=True
        )

        worker_cmd = (
            "chcp 65001 > nul && uv run python -c "
            '"import sys; '
            "sys.stdout.reconfigure(encoding='utf-8') if sys.stdout and hasattr(sys.stdout, 'reconfigure') else None; "
            "sys.stderr.reconfigure(encoding='utf-8') if sys.stderr and hasattr(sys.stderr, 'reconfigure') else None; "
            "import runpy; sys.argv=['run_worker.py']; "
            "runpy.run_module('backend_v2.run_worker', run_name='__main__', alter_sys=True)\""
        )
        worker_process = subprocess.Popen(
            worker_cmd, cwd=WORKSPACE_ROOT, env=env, stdout=backend_log_fp, stderr=subprocess.STDOUT, shell=True
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
        # Build WorkflowInputsIngress payload
        dynamic_inputs = {}
        for key, path in pdf_files.items():
            dynamic_inputs[key] = {
                "filename": os.path.basename(path),
                "content_base64": get_base64_file(path),
                "content_type": "application/pdf",
            }

        # Use the specific workflow ID from the seeded local DB
        workflow_id = "wf_9d68c573802341db"

        payload = {"workflow_id": workflow_id, "target_locale": "fi", "raw_inputs": {"dynamic_inputs": dynamic_inputs}}

        headers = {"Authorization": "Bearer mock-token:usr_18a0d5f6151349a5", "Content-Type": "application/json"}

        logger.info("Sending execution POST request to backend...")
        response = requests.post(
            "http://127.0.0.1:8000/api/v2/execution/executions/", json=payload, headers=headers, timeout=10
        )

        assert response.status_code == 202, f"Failed to start execution: {response.text}"

        execution_data = response.json()
        execution_id = execution_data["id"]
        logger.info(f"Execution started with ID: {execution_id}. Polling for completion...")

        # Poll for completion
        start_time = time.time()
        completed = False

        while time.time() - start_time < WAIT_TIMEOUT:
            status_res = requests.get(
                f"http://127.0.0.1:8000/api/v2/execution/executions/{execution_id}", headers=headers, timeout=30
            )

            assert status_res.status_code == 200, f"Failed to get execution status: {status_res.text}"

            status_data = status_res.json()
            current_status = status_data.get("status")

            if current_status == ExecutionStatus.PASSED.value:
                logger.info(f"Execution {execution_id} completed successfully.")
                completed = True
                break
            elif current_status == ExecutionStatus.FAILED.value:
                logger.error(f"Execution failed: {json.dumps(status_data)}")
                pytest.fail(f"Execution {execution_id} failed.")

            time.sleep(5)

        assert completed, f"Execution {execution_id} timed out after {WAIT_TIMEOUT} seconds."

        logger.info("Verifying generated PDF for SDUI parity...")
        pdf_path = os.path.join(WORKSPACE_ROOT, "data", "files", "executions", execution_id, "report.pdf")
        assert os.path.exists(pdf_path), f"PDF report not found at {pdf_path}"

        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        assert "Yhteenveto" not in full_text, "Legacy hardcoded string 'Yhteenveto' found in PDF!"
        assert "ARVIOINNIN YKSITYISKOHTAINEN PISTEYTYS" in full_text, "Dynamic resolved title 'ARVIOINNIN YKSITYISKOHTAINEN PISTEYTYS' missing from PDF!"

        logger.info("PDF Execution E2E test passed successfully.")

    finally:
        logger.info("Tearing down E2E orchestrator processes...")
        if backend_process:
            backend_process.terminate()
            backend_process.wait(timeout=5)
        if worker_process:
            worker_process.terminate()
            worker_process.wait(timeout=5)
