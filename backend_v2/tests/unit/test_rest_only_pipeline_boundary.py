"""Architectural boundary tests enforcing the REST-Only Pipeline Boundary Invariant.

Mandated by Tripartite Pipeline Isolation and Worker Decoupling (Step 10):
1. AST import analysis: verify that execution_worker.py, core computational execution subservices,
   and topological_evaluator.py contain zero imports or calls referencing ReportService or report compilation tasks.
2. AST zero sys_render steps: verify dag_executor.py contains zero sys_render injections.
3. Test zero side-effects: verify that running execute_workflow_job with mocked Redis enqueues 0 report/render jobs.
4. Test REST-only entrypoint: verify that POST /api/v2/executions/{id}/reports is the exclusive trigger
   that creates ReportArtifact and enqueues worker generation.
5. Test precondition gate: verify that calling POST /api/v2/executions/{id}/reports when execution is RUNNING or FAILED
   raises HTTP 409 Conflict with ErrorCodes.EXECUTION_NOT_READY.
6. Test Dual-Axis Localization AST compliance: verify backend_v2 contains zero occurrences of open() opening
   files with '.arb' extension or paths targeting client_app_v2/lib/l10n/.
7. Test Strict Enum Adapter: verify ReportStatus.l10n_key maps 1:1 to Flutter ARB camelCase translation keys
   and those keys exist in client_app_v2/lib/l10n/app_en.arb and app_fi.arb.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_arq_pool,
    get_current_user_from_header,
    get_execution_service,
    get_report_service,
)
from backend_v2.exceptions import ErrorCodes, ExecutionNotReadyError
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode, ReportStatus
from backend_v2.workers.execution_worker import execute_workflow_job

# ---------------------------------------------------------------------------
# Test 1: AST Import Analysis (Execution Engine Zero Reporting Coupling)
# ---------------------------------------------------------------------------


def test_ast_execution_worker_zero_reporting_coupling() -> None:
    """Verify backend_v2/workers/execution_worker.py contains zero references to reporting."""
    worker_path = Path("backend_v2/workers/execution_worker.py")
    assert worker_path.exists(), "execution_worker.py must exist"

    tree = ast.parse(worker_path.read_text(encoding="utf-8"))
    forbidden_tokens = {
        "ReportService",
        "generate_report_artifact_job",
        "render_profile_job",
        "report_worker",
        "ReportArtifact",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for token in forbidden_tokens:
                    assert token not in alias.name, f"Forbidden import '{alias.name}' in execution_worker.py"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for token in forbidden_tokens:
                assert token not in module, f"Forbidden from-import module '{module}' in execution_worker.py"
            for alias in node.names:
                for token in forbidden_tokens:
                    assert token not in alias.name, f"Forbidden imported symbol '{alias.name}' in execution_worker.py"
        elif isinstance(node, ast.Name):
            for token in forbidden_tokens:
                assert node.id != token, f"Forbidden reference to '{token}' in execution_worker.py"


def test_ast_execution_subservices_zero_reporting_coupling() -> None:
    """Verify core execution services contain zero references to ReportService."""
    target_files = [
        Path("backend_v2/services/execution/ingress_service.py"),
        Path("backend_v2/services/execution/lifecycle_service.py"),
        Path("backend_v2/services/execution/resumption_service.py"),
        Path("backend_v2/services/execution/override_service.py"),
        Path("backend_v2/services/execution/stream_service.py"),
        Path("backend_v2/services/execution/context_service.py"),
        Path("backend_v2/services/orchestrator/topological_evaluator.py"),
    ]

    forbidden_tokens = {
        "ReportService",
        "generate_report_artifact_job",
        "render_profile_job",
    }

    for path in target_files:
        assert path.exists(), f"File {path} must exist"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for token in forbidden_tokens:
                        assert token not in alias.name, f"Forbidden import '{alias.name}' in {path}"
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for token in forbidden_tokens:
                    assert token not in module, f"Forbidden from-import module '{module}' in {path}"
                for alias in node.names:
                    for token in forbidden_tokens:
                        assert token not in alias.name, f"Forbidden symbol '{alias.name}' in {path}"


def test_ast_dag_executor_zero_sys_render_injection() -> None:
    """Verify dag_executor.py contains zero sys_render steps or references."""
    dag_path = Path("backend_v2/services/orchestrator/dag_executor.py")
    assert dag_path.exists()
    content = dag_path.read_text(encoding="utf-8")
    assert "sys_render" not in content, "Found forbidden 'sys_render' in dag_executor.py"


# ---------------------------------------------------------------------------
# Test 2: Zero Side-Effects (ExecutionWorker enqueues 0 report jobs)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execution_worker_zero_report_side_effects() -> None:
    """Verify execute_workflow_job does NOT create report records or enqueue report jobs."""
    mock_workflow = Workflow(
        id="wor_0123456789abcdef",
        slug="test-workflow",
        name="Test Workflow",
        description="Test Description",
        status="active",
        version=1,
        default_strictness_level=50,
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    mock_record = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        progress=None,
        status_message=None,
        steps=[],
    )

    mock_repo = MagicMock()
    mock_repo.get_workflow = AsyncMock(return_value=mock_workflow)
    mock_repo.get_execution = AsyncMock(return_value=mock_record)
    mock_repo.update_execution = AsyncMock()

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_record)

    mock_redis = AsyncMock()

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "preflight_service": MagicMock(run=AsyncMock()),
        "redis": mock_redis,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs={},
        execution_id="exe_0123456789abcdef",
    )

    assert result["status"] == "COMPLETED"
    # Invariant: Redis enqueue_job was never called
    if hasattr(mock_redis, "enqueue_job"):
        assert not mock_redis.enqueue_job.called
    # Invariant: update_execution was called with status=PASSED
    update_call = mock_repo.update_execution.call_args
    assert update_call is not None
    assert update_call[0][1].status == ExecutionStatus.PASSED


# ---------------------------------------------------------------------------
# Test 3 & 4: REST-Only Entrypoint & Precondition Gate
# ---------------------------------------------------------------------------

MOCK_USER_ID = "usr_0123456789abcdef"
MOCK_ORG_ID = "org_0123456789abcdef"
MOCK_EXE_ID = "exe_0123456789abcdef"
MOCK_WOR_ID = "wor_0123456789abcdef"
MOCK_PRF_ID = "prf_0123456789abcdef"
MOCK_REP_ID = "rep_0123456789abcdef"

mock_user = TokenData(id=MOCK_USER_ID, role=UserRole.ROOT, organization_id=MOCK_ORG_ID)


@pytest.fixture
def override_test_deps() -> Generator[None]:
    """Dependency override fixture."""
    app.dependency_overrides[get_current_user_from_header] = lambda: mock_user
    app.dependency_overrides[get_arq_pool] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()


def test_rest_only_entrypoint_creates_report(override_test_deps: Any) -> None:
    """Test POST /api/v2/executions/{id}/reports is the exclusive trigger creating ReportArtifact."""
    mock_report_service = AsyncMock()
    mock_execution_service = AsyncMock()
    app.dependency_overrides[get_report_service] = lambda: mock_report_service
    app.dependency_overrides[get_execution_service] = lambda: mock_execution_service

    now = datetime.now(timezone.utc)
    mock_report_service.list_reports_for_execution.return_value = []
    mock_report_service.create_report_artifact.return_value = ReportArtifact(
        id=MOCK_REP_ID,
        execution_id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        profile_id=MOCK_PRF_ID,
        locale="fi",
        title="Executive Summary",
        status=ReportStatus.PENDING,
        created_at=now,
    )

    client = TestClient(app)
    resp = client.post(
        f"/api/v2/executions/{MOCK_EXE_ID}/reports",
        json={"profile_id": MOCK_PRF_ID, "locale": "fi"},
    )
    assert resp.status_code == 202
    data = resp.json()
    assert data["id"] == MOCK_REP_ID
    assert data["status"] == "generating"
    assert mock_report_service.create_report_artifact.called


def test_precondition_gate_execution_not_ready_raises_409(override_test_deps: Any) -> None:
    """Test POST /api/v2/executions/{id}/reports fails fast with 409 if execution is not PASSED."""
    mock_report_service = AsyncMock()
    app.dependency_overrides[get_report_service] = lambda: mock_report_service

    # When execution is RUNNING or FAILED, ReportService raises ExecutionNotReadyError
    mock_report_service.create_report_artifact.side_effect = ExecutionNotReadyError(
        execution_id=MOCK_EXE_ID,
        current_status="running",
    )

    client = TestClient(app)
    resp = client.post(
        f"/api/v2/executions/{MOCK_EXE_ID}/reports",
        json={"profile_id": MOCK_PRF_ID, "locale": "fi"},
    )
    assert resp.status_code == 409
    data = resp.json()
    assert data["extensions"]["error_code"] == ErrorCodes.EXECUTION_NOT_READY.value


# ---------------------------------------------------------------------------
# Test 5: Dual-Axis Localization AST Compliance (Zero open() on .arb files)
# ---------------------------------------------------------------------------


def test_dual_axis_localization_ast_compliance() -> None:
    """Verify backend_v2 contains zero occurrences of open() targeting .arb files."""
    backend_root = Path("backend_v2")
    py_files = list(backend_root.rglob("*.py"))
    assert len(py_files) > 50, f"Expected > 50 python files, found {len(py_files)}"

    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8")
        if "open(" not in content:
            continue

        try:
            tree = ast.parse(content, filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name == "open" and node.args:
                    first_arg = node.args[0]
                    # Check string literals
                    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                        val = first_arg.value
                        assert not val.endswith(".arb"), f"Forbidden open() on .arb file in {py_file}: {val}"
                        assert "client_app_v2/lib/l10n" not in val, (
                            f"Forbidden open() targeting l10n in {py_file}: {val}"
                        )
                    # Check f-strings
                    elif isinstance(first_arg, ast.JoinedStr):
                        fstring_parts = [
                            p.value
                            for p in first_arg.values
                            if isinstance(p, ast.Constant) and isinstance(p.value, str)
                        ]
                        joined = "".join(fstring_parts)
                        assert ".arb" not in joined, f"Forbidden open() on .arb f-string in {py_file}: {joined}"
                        assert "client_app_v2/lib/l10n" not in joined, (
                            f"Forbidden open() targeting l10n in {py_file}: {joined}"
                        )


# ---------------------------------------------------------------------------
# Test 6: Strict Enum Adapter Parity (ReportStatus.l10n_key)
# ---------------------------------------------------------------------------


def test_strict_enum_adapter_report_status() -> None:
    """Verify ReportStatus.l10n_key maps 1:1 to Flutter ARB keys and keys exist in ARB files."""
    expected_mappings = {
        ReportStatus.PENDING: "reportStatusPending",
        ReportStatus.GENERATING: "reportStatusGenerating",
        ReportStatus.READY: "reportStatusReady",
        ReportStatus.FAILED: "reportStatusFailed",
    }

    for status, expected_key in expected_mappings.items():
        assert status.l10n_key == expected_key, f"Mismatch for {status}: {status.l10n_key} != {expected_key}"

    # Verify keys exist in client ARB files
    arb_en_path = Path("client_app_v2/lib/l10n/app_en.arb")
    arb_fi_path = Path("client_app_v2/lib/l10n/app_fi.arb")
    assert arb_en_path.exists(), "app_en.arb must exist"
    assert arb_fi_path.exists(), "app_fi.arb must exist"

    data_en = json.loads(arb_en_path.read_text(encoding="utf-8"))
    data_fi = json.loads(arb_fi_path.read_text(encoding="utf-8"))

    for expected_key in expected_mappings.values():
        assert expected_key in data_en, f"Key '{expected_key}' missing from app_en.arb"
        assert expected_key in data_fi, f"Key '{expected_key}' missing from app_fi.arb"
