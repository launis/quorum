"""Test suite for execution router endpoints."""

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_current_user_from_header, get_execution_service
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.enums import VisualIntent
from backend_v2.models.v2_core import ReportDataDTO
from backend_v2.models.view.sdui import ReportView

# Basic mock for user
mock_user = TokenData(id="test-user-id", role=UserRole.ROOT, organization_id="root_org")


@pytest.fixture
def override_dependencies() -> Generator[None]:
    app.dependency_overrides[get_current_user_from_header] = lambda: mock_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_execution_service() -> Any:
    service = AsyncMock()
    app.dependency_overrides[get_execution_service] = lambda: service
    return service


def test_get_execution_report_returns_raw_dto(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Integration test for /report headless endpoint using v2_core.ReportDataDTO."""
    client = TestClient(app)

    mock_dto = ReportDataDTO(
        execution_id="test_execution_123",
        workflow_id="wf_1",
        profile_id="prf_001",
        global_score=72.5,
    )
    mock_execution_service.get_report_dto.return_value = mock_dto

    response = client.get("/api/v2/execution/executions/test_execution_123/report")

    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "wf_1"
    assert data["profile_id"] == "prf_001"
    assert data["global_score"] == 72.5
    # Ensure it's not wrapped in SDUI
    assert "sections" not in data


def test_get_execution_sdui_returns_view(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Integration test for /sdui SDUI view endpoint."""
    client = TestClient(app)

    mock_sdui_view = ReportView(
        view_id="test_execution_123",
        title="SDUI Raportti",
        status_theme=VisualIntent.SUCCESS,
        sections=[],
        metrics=None,
        system_notification=None,
        references=[],
    )
    mock_execution_service.get_sdui_view.return_value = mock_sdui_view

    response = client.get("/api/v2/execution/executions/test_execution_123/sdui")

    assert response.status_code == 200
    data = response.json()
    assert data["view_id"] == "test_execution_123"
    assert data["title"] == "SDUI Raportti"
    assert "sections" in data
