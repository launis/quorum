"""Unit tests for workflow execution UI schema router and studio workflow RBAC."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_execution_service,
    get_studio_output_profile_service,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
    get_studio_workflow_service,
)
from backend_v2.api.routers.execution.workflows import get_workflow_ui_schema, router
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.services.execution import ExecutionService
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.services.studio.workflow_service import StudioWorkflowService
from backend_v2.tests.factories import WorkflowFactory
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryExecutionRepository,
    InMemoryWorkflowRepository,
)


def mock_get_current_user_member() -> TokenData:
    """Provide a standard MEMBER role user token for RBAC and router tests."""
    return TokenData(
        email="member@test.com",
        id="usr_1234567890abcdef",
        role=UserRole.MEMBER,
        organization_id="org_1234567890abcdef",
    )


def mock_get_current_user_root() -> TokenData:
    """Provide a ROOT superuser token for administrative test scenarios."""
    return TokenData(
        email="root@test.com",
        id="usr_abcdef1234567890",
        role=UserRole.ROOT,
        organization_id="org_1234567890abcdef",
    )


@pytest.fixture
def execution_service(fake_workflow_repo: InMemoryWorkflowRepository) -> ExecutionService:
    """Provide a real ExecutionService wired to hermetic in-memory repositories."""
    return ExecutionService(
        exec_repo=InMemoryExecutionRepository(),
        workflow_repo=fake_workflow_repo,
    )


@pytest.fixture
def client_member(
    studio_workflow_service: StudioWorkflowService,
    studio_prompt_block_service: StudioPromptBlockService,
    execution_service: ExecutionService,
) -> Generator[TestClient]:
    """Provide a TestClient authenticated as MEMBER with real in-memory services."""
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_member
    app.dependency_overrides[get_studio_simulation_service] = lambda: studio_workflow_service
    app.dependency_overrides[get_studio_workflow_service] = lambda: studio_workflow_service
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: studio_prompt_block_service
    app.dependency_overrides[get_studio_output_profile_service] = lambda: studio_workflow_service
    app.dependency_overrides[get_execution_service] = lambda: execution_service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_execution_workflows_router_metadata() -> None:
    """Verify router prefix and tags configuration."""
    assert router.prefix == "/workflows"
    assert "Workflows" in router.tags


def test_workflow_rbac_save_member_forbidden(client_member: TestClient) -> None:
    """Negative RBAC test: MEMBER role cannot save or mutate studio workflows."""
    workflow = WorkflowFactory.build(organization_id="org_1234567890abcdef")
    payload = workflow.model_dump(mode="json")
    response = client_member.put(f"/api/v2/studio/workflows/{workflow.id}", json=payload)

    assert response.status_code == 403
    assert "Permission" in response.json()["detail"] or "ADMIN" in response.json()["detail"]


def test_workflow_rbac_delete_member_forbidden(
    client_member: TestClient,
    fake_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    """Negative RBAC test: MEMBER role cannot delete studio workflows."""
    workflow = WorkflowFactory.build(organization_id="org_1234567890abcdef")
    fake_workflow_repo._save_isolated(workflow.id, workflow)

    response = client_member.delete(f"/api/v2/studio/workflows/{workflow.id}")
    assert response.status_code == 403


def test_get_workflow_ui_schema_success(
    client_member: TestClient,
    fake_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    """Positive test: GET /{workflow_id}/ui_schema returns expected_inputs from persisted workflow."""
    expected_input = ExpectedInput(
        input_key="source_document",
        label=I18nText(translations={"en": "Source Document", "fi": "Lähdedokumentti"}),
        description=I18nText(translations={"en": "Primary source text", "fi": "Ensisijainen lähdeteksti"}),
        input_modes=["text"],
        required=True,
    )
    workflow = WorkflowFactory.build(
        organization_id="org_1234567890abcdef",
        expected_inputs=[expected_input],
    )
    fake_workflow_repo._save_isolated(workflow.id, workflow)

    response = client_member.get(f"/api/v2/execution/workflows/{workflow.id}/ui_schema")
    assert response.status_code == 200
    body = response.json()
    assert len(body["expected_inputs"]) == 1
    assert body["expected_inputs"][0]["input_key"] == "source_document"


@pytest.mark.asyncio
async def test_get_workflow_ui_schema_not_found_raises_app_exception(
    client_member: TestClient,
    execution_service: ExecutionService,
) -> None:
    """Negative test: Missing workflow ID raises ResourceNotFoundError (AppException) with RESOURCE_NOT_FOUND."""
    missing_id = "wor_0000000000000000"
    with pytest.raises(AppException) as exc_info:
        await get_workflow_ui_schema(
            workflow_id=missing_id,
            current_user=mock_get_current_user_member(),
            execution_service=execution_service,
        )

    assert isinstance(exc_info.value, ResourceNotFoundError)
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    response = client_member.get(f"/api/v2/execution/workflows/{missing_id}/ui_schema")
    assert response.status_code == 404
    assert response.json()["extensions"]["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_get_workflow_ui_schema_whitespace_boundary_raises_app_exception(
    execution_service: ExecutionService,
) -> None:
    """Negative boundary test: Whitespace/malformed workflow ID raises AppException (404 RESOURCE_NOT_FOUND)."""
    with pytest.raises(AppException) as exc_info:
        await get_workflow_ui_schema(
            workflow_id="   ",
            current_user=mock_get_current_user_member(),
            execution_service=execution_service,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_get_workflow_ui_schema_repository_fault_raises_app_exception(
    fake_workflow_repo: InMemoryWorkflowRepository,
    execution_service: ExecutionService,
) -> None:
    """Negative fault test: Repository failure propagates AppException cleanly with fault cleanup."""
    workflow = WorkflowFactory.build(organization_id="org_1234567890abcdef")
    fake_workflow_repo._save_isolated(workflow.id, workflow)
    fake_workflow_repo.inject_fault(
        "get_workflow_by_id",
        AppException(
            message="Simulated database error",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ),
    )
    try:
        with pytest.raises(AppException) as exc_info:
            await get_workflow_ui_schema(
                workflow_id=workflow.id,
                current_user=mock_get_current_user_member(),
                execution_service=execution_service,
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
    finally:
        fake_workflow_repo.clear_faults()
