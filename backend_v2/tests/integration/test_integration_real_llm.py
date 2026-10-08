"""Epic 16.5: End-to-End Orchestration (PDF Execution Test).

This test validates the FastAPI backend's ability to ingest PDF files via Base64,
perform eager extraction, and execute a full LLM workflow to completion.
"""

import base64
import json
import logging
import os
import subprocess
import threading
import time
from pathlib import Path

import fitz
import pytest
import requests

from backend_v2.models.enums import ExecutionStatus

logger = logging.getLogger(__name__)

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
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


def is_redis_running() -> bool:
    """Check if Redis is alive on port 6379."""
    try:
        import redis

        client = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=1)
        return bool(client.ping())
    except redis.ConnectionError, redis.TimeoutError, OSError:
        return False


def is_backend_running(timeout: float = 1.0) -> bool:
    """Check if the backend API is alive on port 8000."""
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def wait_for_backend(timeout_seconds: int = 30) -> bool:
    """Wait for backend API to become ready with retries."""
    start = time.time()
    while time.time() - start < timeout_seconds:
        if is_backend_running():
            return True
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
    pdf_dir = os.path.join(WORKSPACE_ROOT, "docs", "jwdatat")
    pdf_files = {
        "chat_log": os.path.join(pdf_dir, "keskusteluhistoria.pdf"),
        "product_text": os.path.join(pdf_dir, "lopputuote.pdf"),
        "reflection_text": os.path.join(pdf_dir, "reflektiodokumentti.pdf"),
    }

    for _, path in pdf_files.items():
        if not os.path.exists(path):
            pytest.skip(f"Required PDF not found: {path}. Skipping test.")

    clear_logs()

    redis_server = None
    if not is_redis_running():
        logger.info("Local Redis not detected on port 6379. Starting TcpFakeServer daemon on port 6379.")
        from fakeredis import TcpFakeServer

        redis_server = TcpFakeServer(("127.0.0.1", 6379))
        redis_thread = threading.Thread(target=redis_server.serve_forever, daemon=True)
        redis_thread.start()
        time.sleep(0.5)
        assert is_redis_running(), "Failed to start TcpFakeServer on port 6379."

    backend_process = None
    worker_process = None
    backend_log_fp = None
    if not is_backend_running():
        logger.info("Backend is not running. Starting local FastAPI instance on port 8000.")
        env = os.environ.copy()
        if "PYTEST_CURRENT_TEST" in env:
            del env["PYTEST_CURRENT_TEST"]  # CRITICAL: Prevent FakeRedis isolation in subprocesses
        env["USE_FIREBASE_AUTH"] = "false"
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["NO_COLOR"] = "1"
        env["TERM"] = "dumb"

        backend_log_fp = open(BACKEND_LOG_FILE, "a", encoding="utf-8")
        backend_cmd = [
            "uv",
            "run",
            "python",
            "-m",
            "uvicorn",
            "backend_v2.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ]
        backend_process = subprocess.Popen(
            backend_cmd, cwd=WORKSPACE_ROOT, env=env, stdout=backend_log_fp, stderr=subprocess.STDOUT
        )

        worker_cmd = [
            "uv",
            "run",
            "python",
            "-m",
            "backend_v2.run_worker",
        ]
        worker_process = subprocess.Popen(
            worker_cmd, cwd=WORKSPACE_ROOT, env=env, stdout=backend_log_fp, stderr=subprocess.STDOUT
        )

        if not wait_for_backend(timeout_seconds=30):
            if backend_process:
                subprocess.run(f"taskkill /F /T /PID {backend_process.pid}", shell=True, capture_output=True)
            if worker_process:
                subprocess.run(f"taskkill /F /T /PID {worker_process.pid}", shell=True, capture_output=True)
            if backend_log_fp:
                backend_log_fp.close()
            if redis_server:
                redis_server.shutdown()
                redis_server.server_close()
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

        headers = {
            "Authorization": "Bearer mock-token:usr_18a0d5f6151349a5",
            "Content-Type": "application/json",
            "Accept-Language": "fi",
        }

        logger.info("Sending execution POST request to backend...")
        response = requests.post(
            "http://127.0.0.1:8000/api/v2/execution/executions/", json=payload, headers=headers, timeout=30
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
            current_status = status_data["status"] if "status" in status_data else None

            if current_status == ExecutionStatus.PASSED.value:
                logger.info(f"Execution {execution_id} completed successfully.")
                completed = True
                break
            elif current_status == ExecutionStatus.FAILED.value:
                logger.error(f"Execution failed: {json.dumps(status_data)}")
                pytest.fail(f"Execution {execution_id} failed.")

            time.sleep(5)

        assert completed, f"Execution {execution_id} timed out after {WAIT_TIMEOUT} seconds."

        logger.info("Requesting report generation via canonical reports endpoint...")
        create_report_res = requests.post(
            f"http://127.0.0.1:8000/api/v2/executions/{execution_id}/reports",
            json={"output_profile_id": None},
            headers=headers,
            timeout=30,
        )
        assert create_report_res.status_code == 202, (
            f"Failed to create report: {create_report_res.status_code} - {create_report_res.text}"
        )
        report_data = create_report_res.json()
        report_id = report_data["id"]
        logger.info("Report creation accepted, report_id=%s. Polling for READY status...", report_id)

        render_start = time.time()
        pdf_ready = False
        while time.time() - render_start < 120:
            status_res = requests.get(
                f"http://127.0.0.1:8000/api/v2/reports/{report_id}",
                headers=headers,
                timeout=30,
            )
            assert status_res.status_code == 200, (
                f"Failed to fetch report status: {status_res.status_code} - {status_res.text}"
            )
            current_status = status_res.json()["status"]
            if current_status == "READY":
                logger.info("Report generation completed successfully (READY).")
                pdf_ready = True
                break
            elif current_status == "FAILED":
                pytest.fail(f"Report generation failed for report_id={report_id}: {status_res.text}")
            elif current_status in ("PENDING", "GENERATING"):
                logger.info("Report generation in progress (%s)...", current_status)
            else:
                logger.warning("Unexpected report status: %s", current_status)
            time.sleep(3)

        assert pdf_ready, f"Report generation timed out for {report_id}"

        logger.info("Verifying generated PDF via canonical reports PDF endpoint...")
        pdf_res = requests.get(
            f"http://127.0.0.1:8000/api/v2/reports/{report_id}/pdf",
            headers=headers,
            timeout=30,
        )
        assert pdf_res.status_code == 200, f"Failed to download PDF: {pdf_res.status_code} - {pdf_res.text}"
        assert pdf_res.headers["content-type"] == "application/pdf"

        doc = fitz.open(stream=pdf_res.content, filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()

        # Verify header and executive content rendered into PDF
        assert "Kokonaisvaltainen Auditointi" in full_text or "Raportti" in full_text, (
            "Standard executive synthesis header missing from PDF!"
        )

        logger.info("PDF Execution E2E test passed successfully.")

    finally:
        logger.info("Tearing down E2E orchestrator processes...")
        if backend_process:
            subprocess.run(f"taskkill /F /T /PID {backend_process.pid}", shell=True, capture_output=True)
        if worker_process:
            subprocess.run(f"taskkill /F /T /PID {worker_process.pid}", shell=True, capture_output=True)
        if backend_log_fp:
            backend_log_fp.close()
        if redis_server:
            redis_server.shutdown()
            redis_server.server_close()
