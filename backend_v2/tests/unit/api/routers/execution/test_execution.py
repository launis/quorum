"""Unit tests for the Execution API Routers package facade (__init__.py).

Verifies that the execution package facade exports and mounts the canonical
execution and report routers and propagates fail-fast AppException errors.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_arq_pool,
    get_current_user_from_header,
    get_execution_service,
    get_report_service,
)
from backend_v2.api.routers.execution import reports_router, router
from backend_v2.exceptions import (
    AppException,
    ConflictError,
    ErrorCodes,
    ResourceNotFoundError,
)
from backend_v2.models.auth import TokenData, UserRole

MOCK_USER_ID = "usr_0195f3a0000070018234567890abcdef"
MOCK_ORG_ID = "org_0195f3a0000070018234567890abcdef"
MOCK_EXE_ID = "exe_0195f3a0000070018234567890abcdef"
MOCK_PRF_ID = "prf_0195f3a0000070018234567890abcdef"

MOCK_USER = TokenData(id=MOCK_USER_ID, role=UserRole.ROOT, organization_id=MOCK_ORG_ID)


def _create_test_app(
    execution_service: AsyncMock | None = None,
    report_service: AsyncMock | None = None,
) -> FastAPI:
    """Create an isolated FastAPI instance mounting the execution facade routers.

    Args:
        execution_service: Optional mocked ExecutionService dependency override.
        report_service: Optional mocked ReportService dependency override.

    Returns:
        Configured FastAPI application with execution and reports routers mounted.
    """
    test_app = FastAPI()
    test_app.include_router(router)
    test_app.include_router(reports_router)
    test_app.dependency_overrides[get_current_user_from_header] = lambda: MOCK_USER
    test_app.dependency_overrides[get_arq_pool] = lambda: AsyncMock()
    if execution_service is not None:
        test_app.dependency_overrides[get_execution_service] = lambda: execution_service
    if report_service is not None:
        test_app.dependency_overrides[get_report_service] = lambda: report_service
    return test_app


def test_execution_package_routers_mount_expected_endpoints() -> None:
    """Verify router prefixes and mounted route paths on a FastAPI instance."""
    assert router.prefix == "/execution"
    assert reports_router.prefix == ""

    test_app = _create_test_app()
    route_paths = set(test_app.openapi()["paths"].keys())

    assert "/execution/executions/" in route_paths
    assert "/execution/executions/{execution_id}" in route_paths
    assert "/executions/{execution_id}/reports" in route_paths
    assert "/reports/{report_id}" in route_paths


def test_execution_facade_get_missing_execution_raises_app_exception() -> None:
    """Negative test: Requesting a non-existent execution via facade router raises ResourceNotFoundError."""
    mock_exec_service = AsyncMock()
    mock_exec_service.get_execution.side_effect = ResourceNotFoundError(
        resource_type="Execution",
        resource_id=MOCK_EXE_ID,
    )
    test_app = _create_test_app(execution_service=mock_exec_service)
    client = TestClient(test_app, raise_server_exceptions=True)

    with pytest.raises(AppException) as exc_info:
        client.get(f"/execution/executions/{MOCK_EXE_ID}")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


def test_execution_facade_create_report_conflict_raises_app_exception() -> None:
    """Negative test: Creating a report for an unready execution via facade router raises ConflictError."""
    mock_rep_service = AsyncMock()
    mock_rep_service.list_reports_for_execution.return_value = []
    mock_rep_service.create_report_artifact.side_effect = ConflictError(
        message="Execution has not passed and cannot generate a report."
    )
    test_app = _create_test_app(report_service=mock_rep_service)
    client = TestClient(test_app, raise_server_exceptions=True)

    with pytest.raises(AppException) as exc_info:
        client.post(
            f"/executions/{MOCK_EXE_ID}/reports",
            json={"profile_id": MOCK_PRF_ID, "locale": "fi"},
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT_ERROR.value
