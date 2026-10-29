"""End-to-End Orchestration (PDF Execution & Dynamic MCP Verification Test).

This test validates the FastAPI backend's ability to ingest PDF files via Base64,
perform live MCP gateway tool discovery and invocation, execute a full LLM workflow
to completion, and render the resulting report PDF.
"""

import base64
import json
import logging
import os
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import fitz
import pytest
import requests

from backend_v2.exceptions import AppException
from backend_v2.models.domain.system_config import SystemConfigMCPGateways
from backend_v2.models.dtos.mcp import (
    MCPContentBlockDTO,
    MCPDiscoveredToolWireDTO,
    MCPInitializeResultDTO,
    MCPJsonRpcRequestDTO,
    MCPJsonRpcResponseDTO,
    MCPToolCallResultDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
    MCPToolsListResultDTO,
)
from backend_v2.models.enums import ExecutionStatus, JSONSchemaPropertyType, ReportStatus
from backend_v2.services.mcp.alias_registry import AliasRegistry
from backend_v2.services.mcp.url_validator import MCPUrlValidator

logger = logging.getLogger(__name__)

# Paths
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
BACKEND_LOG_FILE = os.path.join(WORKSPACE_ROOT, "backend_debug.log")
TESTILYHYT_DIR = os.path.join(WORKSPACE_ROOT, "docs", "testilyhyt")

TARGET_WORKFLOW_ID = os.environ.get("TEST_WORKFLOW_ID", "wf_d653170e174847559e08af42b938d826")
WAIT_TIMEOUT = int(os.environ.get("TEST_WAIT_TIMEOUT", "3600"))
DEFAULT_GATEWAY_ID = "sys_0195f3a00000700080008172bda70c86"


class _LocalMCPRequestHandler(BaseHTTPRequestHandler):
    """In-process JSON-RPC 2.0 HTTP handler serving dynamic MCP tools during live E2E verification."""

    def log_message(self, format: str, *args: object) -> None:
        """Silence standard HTTP server access logs during test execution.

        Args:
            format: Log message format string.
            *args: Format arguments.
        """
        return

    def do_POST(self) -> None:
        """Handle incoming JSON-RPC 2.0 POST requests for initialize, tools/list, and tools/call."""
        content_len = int(self.headers["Content-Length"]) if "Content-Length" in self.headers else 0
        raw_body = self.rfile.read(content_len).decode("utf-8")
        rpc_req = MCPJsonRpcRequestDTO.model_validate_json(raw_body)

        if rpc_req.method == "initialize":
            init_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPInitializeResultDTO(protocol_version="2025-03-26"),
            )
            payload_bytes = init_resp.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload_bytes)))
            self.end_headers()
            self.wfile.write(payload_bytes)
            return

        if rpc_req.method == "notifications/initialized":
            self.send_response(202)
            self.end_headers()
            return

        if rpc_req.method == "tools/list":
            list_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPToolsListResultDTO(
                    tools=[
                        MCPDiscoveredToolWireDTO(
                            name="mcp_tavily_search",
                            description="Perform an explicit search on the live internet using Tavily.",
                            input_schema=MCPToolInputSchemaDTO(
                                properties={
                                    "query": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.STRING,
                                        description="The search query to submit to the Tavily search engine.",
                                    )
                                },
                                required=["query"],
                            ),
                        ),
                        MCPDiscoveredToolWireDTO(
                            name="mcp_wikipedia_search",
                            description="Search Wikipedia articles and return top matching titles and snippets.",
                            input_schema=MCPToolInputSchemaDTO(
                                properties={
                                    "query": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.STRING,
                                        description="The search term to query on Wikipedia.",
                                    )
                                },
                                required=["query"],
                            ),
                        ),
                        MCPDiscoveredToolWireDTO(
                            name="mcp_wikipedia_read",
                            description="Retrieve the full encyclopedic summary of a specific Wikipedia article by title.",
                            input_schema=MCPToolInputSchemaDTO(
                                properties={
                                    "title": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.STRING,
                                        description="The exact title of the Wikipedia article to read.",
                                    )
                                },
                                required=["title"],
                            ),
                        ),
                    ]
                ),
            )
            payload_bytes = list_resp.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload_bytes)))
            self.end_headers()
            self.wfile.write(payload_bytes)
            return

        call_resp = MCPJsonRpcResponseDTO(
            id=rpc_req.id,
            result=MCPToolCallResultDTO(
                content=[
                    MCPContentBlockDTO(
                        type="text",
                        text="Verified external empirical reference from MCP gateway search.",
                    )
                ],
                is_error=False,
            ),
        )
        payload_bytes = call_resp.model_dump_json(by_alias=True, exclude_none=True).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload_bytes)))
        self.end_headers()
        self.wfile.write(payload_bytes)


def clear_logs() -> None:  # pragma: no cover
    """Clear backend debug log."""
    with open(BACKEND_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")


def is_redis_running() -> bool:  # pragma: no cover
    """Check if Redis is alive on port 6379.

    Returns:
        True if Redis responds to ping on port 6379.
    """
    try:
        import redis

        client = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=1)
        return bool(client.ping())
    except redis.ConnectionError, redis.TimeoutError, OSError:
        return False


def is_backend_running(timeout: float = 1.0) -> bool:  # pragma: no cover
    """Check if the backend API is alive on port 8000.

    Args:
        timeout: Request timeout in seconds.

    Returns:
        True if the backend docs endpoint returns HTTP 200.
    """
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def wait_for_backend(timeout_seconds: int = 30) -> bool:  # pragma: no cover
    """Wait for backend API to become ready with retries.

    Args:
        timeout_seconds: Maximum wait time in seconds.

    Returns:
        True once the backend responds or False on timeout.
    """
    start = time.time()
    while time.time() - start < timeout_seconds:
        if is_backend_running():
            return True
        time.sleep(1)
    return False


def get_base64_file(file_path: str) -> str:  # pragma: no cover
    """Read a file and return its base64 encoded string.

    Args:
        file_path: Path to the binary file on disk.

    Returns:
        UTF-8 base64 string representation of the file content.
    """
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def test_local_mcp_request_handler_roundtrip_positive() -> None:
    """Positive: Verify that _LocalMCPRequestHandler serves initialize, tools/list, and tools/call JSON-RPC 2.0 envelopes."""
    mcp_server = ThreadingHTTPServer(("127.0.0.1", 0), _LocalMCPRequestHandler)
    mcp_port = mcp_server.server_address[1]
    mcp_thread = threading.Thread(target=mcp_server.serve_forever, daemon=True)
    mcp_thread.start()
    url = f"http://127.0.0.1:{mcp_port}/mcp"
    try:
        init_res = requests.post(
            url,
            data=MCPJsonRpcRequestDTO(id=1, method="initialize").model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert init_res.status_code == 200
        init_dto = MCPJsonRpcResponseDTO.model_validate_json(init_res.text)
        assert isinstance(init_dto.result, MCPInitializeResultDTO)

        notif_res = requests.post(
            url,
            data=MCPJsonRpcRequestDTO(method="notifications/initialized").model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert notif_res.status_code == 202

        list_res = requests.post(
            url,
            data=MCPJsonRpcRequestDTO(id=2, method="tools/list").model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert list_res.status_code == 200
        list_dto = MCPJsonRpcResponseDTO.model_validate_json(list_res.text)
        assert isinstance(list_dto.result, MCPToolsListResultDTO)
        assert len(list_dto.result.tools) == 3

        call_res = requests.post(
            url,
            data=MCPJsonRpcRequestDTO(id=3, method="tools/call").model_dump_json(exclude_none=True),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        assert call_res.status_code == 200
        call_dto = MCPJsonRpcResponseDTO.model_validate_json(call_res.text)
        assert isinstance(call_dto.result, MCPToolCallResultDTO)
        assert call_dto.result.is_error is False
    finally:
        mcp_server.shutdown()
        mcp_server.server_close()


def test_real_llm_mcp_url_ssrf_rejected_negative() -> None:
    """Negative: Verify that MCPUrlValidator blocks private and metadata endpoints when private networks are disabled."""
    with pytest.raises(AppException) as exc_info:
        MCPUrlValidator.validate_mcp_endpoint_url(
            "http://169.254.169.254/latest/meta-data",
            allow_private_networks=False,
        )
    assert exc_info.value.status_code in (400, 403)


def test_real_llm_mcp_invalid_alias_rejected_negative() -> None:
    """Negative: Verify that AliasRegistry rejects un-namespaced tool identifiers."""
    with pytest.raises(AppException) as exc_info:
        AliasRegistry.parse_namespaced_tool_alias("mcp_tavily_search_without_namespace")
    assert exc_info.value.status_code == 400


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_E2E") != "true",
    reason="Live E2E tests skipped by default. Set $env:RUN_LIVE_E2E='true' to run as final verification gate.",
)
@pytest.mark.asyncio
@pytest.mark.order("last")
async def test_real_llm_pdf_execution() -> None:  # pragma: no cover
    """Live E2E test verifying PDF processing and dynamic MCP execution via the FastAPI Backend."""
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

    mcp_server = ThreadingHTTPServer(("127.0.0.1", 0), _LocalMCPRequestHandler)
    mcp_port = mcp_server.server_address[1]
    mcp_thread = threading.Thread(target=mcp_server.serve_forever, daemon=True)
    mcp_thread.start()

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
            del env["PYTEST_CURRENT_TEST"]
        env["USE_FIREBASE_AUTH"] = "false"
        env["MCP_ALLOW_PRIVATE_NETWORKS"] = "true"
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
            mcp_server.shutdown()
            mcp_server.server_close()
            pytest.fail("Failed to start FastAPI backend for testing.")
    else:
        logger.info("Backend is already running. Re-using active instance.")

    headers = {
        "Authorization": "Bearer mock-token:usr_0195f3a00000700188a0d5f6151349a5",
        "Content-Type": "application/json",
        "Accept-Language": "fi",
    }
    original_gateway: SystemConfigMCPGateways | None = None

    try:
        gw_get_res = requests.get(
            f"http://127.0.0.1:8000/api/v2/studio/mcp-gateways/{DEFAULT_GATEWAY_ID}",
            headers=headers,
            timeout=15,
        )
        if gw_get_res.status_code == 200:
            original_gateway = SystemConfigMCPGateways.model_validate_json(gw_get_res.text)
            updated_gateway = original_gateway.model_copy(update={"endpoint_url": f"http://127.0.0.1:{mcp_port}/mcp"})
            gw_put_res = requests.put(
                f"http://127.0.0.1:8000/api/v2/studio/mcp-gateways/{DEFAULT_GATEWAY_ID}",
                data=updated_gateway.model_dump_json(),
                headers=headers,
                timeout=15,
            )
            assert gw_put_res.status_code == 200, f"Failed to point MCP gateway to local server: {gw_put_res.text}"

        dynamic_inputs = {}
        for key, path in pdf_files.items():
            dynamic_inputs[key] = {
                "filename": os.path.basename(path),
                "content_base64": get_base64_file(path),
                "content_type": "application/pdf",
            }

        workflow_id = "wf_0195f3a0000070098d68c573802341db"
        payload = {"workflow_id": workflow_id, "target_locale": "fi", "raw_inputs": {"dynamic_inputs": dynamic_inputs}}

        logger.info("Sending execution POST request to backend...")
        response = requests.post(
            "http://127.0.0.1:8000/api/v2/execution/executions/", json=payload, headers=headers, timeout=30
        )

        assert response.status_code == 202, f"Failed to start execution: {response.text}"

        execution_data = response.json()
        execution_id = execution_data["id"]
        logger.info(f"Execution started with ID: {execution_id}. Polling for completion...")

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
            json={"profile_id": "prf_0195f3a0000070058d6e7f8091a2b3c4"},
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
            if current_status == ReportStatus.READY.value:
                logger.info("Report generation completed successfully (READY).")
                pdf_ready = True
                break
            elif current_status == ReportStatus.FAILED.value:
                pytest.fail(f"Report generation failed for report_id={report_id}: {status_res.text}")
            elif current_status in (ReportStatus.PENDING.value, ReportStatus.GENERATING.value):
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

        assert "Kokonaisvaltainen Auditointi" in full_text or "Raportti" in full_text, (
            "Standard executive synthesis header missing from PDF!"
        )

        logger.info("PDF Execution E2E test passed successfully.")

    finally:
        if original_gateway is not None and is_backend_running():
            try:
                requests.put(
                    f"http://127.0.0.1:8000/api/v2/studio/mcp-gateways/{DEFAULT_GATEWAY_ID}",
                    data=original_gateway.model_dump_json(),
                    headers=headers,
                    timeout=10,
                )
            except requests.exceptions.RequestException:
                pass
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
        mcp_server.shutdown()
        mcp_server.server_close()
