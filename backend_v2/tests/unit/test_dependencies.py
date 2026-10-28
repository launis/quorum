"""Unit tests for FastAPI dependency injection providers in backend_v2/api/dependencies.py."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from backend_v2.api.dependencies import (
    get_agent_repo,
    get_arq_pool,
    get_audit_repo,
    get_auth_service,
    get_component_repo,
    get_current_admin_user,
    get_current_user_from_header,
    get_dag_executor,
    get_db_driver,
    get_document_extraction_service,
    get_execution_repo,
    get_execution_service,
    get_export_service,
    get_identity_repo,
    get_knowledge_repo,
    get_llm_handler,
    get_llm_task_executor,
    get_output_profile_repo,
    get_prompt_block_repo,
    get_prompt_compiler,
    get_report_artifact_repo,
    get_report_service,
    get_studio_output_profile_service,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
    get_studio_system_config_service,
    get_studio_workflow_service,
    get_system_repo,
    get_task_blueprint_repo,
    get_usage_service,
    get_workflow_repo,
    require_role,
)
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.database.repositories.components.agent import AgentRepositoryImpl
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.repositories.components.task_blueprint import TaskBlueprintRepositoryImpl
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.database.repositories.knowledge import KnowledgeRepositoryImpl
from backend_v2.database.repositories.report_artifact import ReportArtifactRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import AuthenticationError, PermissionDeniedError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def fake_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an in-memory unified workflow repository fake.

    Returns:
        InMemoryUnifiedWorkflowRepository instance.
    """
    return InMemoryUnifiedWorkflowRepository()


@pytest.fixture
def mock_settings() -> Settings:
    """Provide a hermetic mocked Settings instance without live environment I/O.

    Returns:
        Mocked Settings instance with use_firebase_auth disabled.
    """
    settings = MagicMock(spec=Settings)
    settings.use_firebase_auth = False
    return settings


@pytest.mark.asyncio
async def test_get_db_driver(mock_settings: Settings) -> None:
    """Test get_db_driver delegates to get_driver with injected settings."""
    expected_driver = MagicMock()
    with patch("backend_v2.api.dependencies.get_driver", new=AsyncMock(return_value=expected_driver)) as mock_factory:
        driver = await get_db_driver(settings=mock_settings)
        assert driver is expected_driver
        mock_factory.assert_awaited_once_with(mock_settings)


def test_get_auth_service(fake_repo: InMemoryUnifiedWorkflowRepository, mock_settings: Settings) -> None:
    """Test get_auth_service wires repository and firebase setting."""
    auth_service = get_auth_service(repo=fake_repo, settings=mock_settings)
    assert auth_service is not None
    assert auth_service.use_firebase is False


@pytest.mark.asyncio
async def test_get_current_user_from_header_missing_token(caplog: pytest.LogCaptureFixture) -> None:
    """Test get_current_user_from_header logs RFC 7807 error and raises AuthenticationError when token is None."""
    mock_auth_service = AsyncMock()

    with caplog.at_level(logging.ERROR), pytest.raises(AuthenticationError) as exc:
        await get_current_user_from_header(auth_service=mock_auth_service, token=None, token_query=None)

    assert "Missing authentication token" in str(exc.value)
    assert exc.value.details == {"error_code": "AUTH_TOKEN_MISSING"}
    assert any("Missing authentication token" in rec.message for rec in caplog.records)


@pytest.mark.asyncio
async def test_get_current_user_from_header_empty_string_token_boundary() -> None:
    """Test get_current_user_from_header raises AuthenticationError on empty string credentials (boundary)."""
    mock_auth_service = AsyncMock()
    empty_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    empty_credentials.credentials = ""

    with pytest.raises(AuthenticationError) as exc:
        await get_current_user_from_header(
            auth_service=mock_auth_service,
            token=empty_credentials,
            token_query="",
        )

    assert exc.value.details == {"error_code": "AUTH_TOKEN_MISSING"}
    mock_auth_service.verify_token.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_from_header_valid_token() -> None:
    """Test get_current_user_from_header returns user data for valid bearer token."""
    mock_auth_service = AsyncMock()
    user_id = generate_opaque_id(EntityPrefix.USER)
    expected_user = TokenData(id=user_id, email="test@test.com", role=UserRole.MEMBER)
    mock_auth_service.verify_token.return_value = expected_user

    mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    mock_credentials.credentials = "valid_token"

    user = await get_current_user_from_header(auth_service=mock_auth_service, token=mock_credentials)
    assert user == expected_user
    mock_auth_service.verify_token.assert_called_once_with("valid_token")


@pytest.mark.asyncio
async def test_get_current_user_from_header_token_query() -> None:
    """Test get_current_user_from_header authenticates via query parameter fallback."""
    mock_auth_service = AsyncMock()
    user_id = generate_opaque_id(EntityPrefix.USER)
    expected_user = TokenData(id=user_id, email="query@test.com", role=UserRole.MEMBER)
    mock_auth_service.verify_token.return_value = expected_user

    user = await get_current_user_from_header(auth_service=mock_auth_service, token=None, token_query="query_token_123")
    assert user == expected_user
    mock_auth_service.verify_token.assert_called_once_with("query_token_123")


@pytest.mark.asyncio
async def test_get_studio_simulation_service() -> None:
    """Test get_studio_simulation_service injection."""
    mock_pb_service = AsyncMock()
    service = await get_studio_simulation_service(
        prompt_block_service=mock_pb_service,
    )
    assert service.prompt_block_service is mock_pb_service


def test_get_document_extraction_service() -> None:
    """Test get_document_extraction_service instantiation."""
    service = get_document_extraction_service()
    assert service is not None


@pytest.mark.asyncio
async def test_require_role_root_and_matches(caplog: pytest.LogCaptureFixture) -> None:
    """Test require_role dependency checker for root bypass, matching role, and RFC 7807 rejection."""
    checker = require_role(UserRole.ADMIN)

    # Root user bypasses role requirement
    root_user = TokenData(id=generate_opaque_id(EntityPrefix.USER), email="root@test.com", role=UserRole.ROOT)
    assert await checker(user=root_user) == root_user

    # Admin user matches ADMIN requirement
    admin_user = TokenData(id=generate_opaque_id(EntityPrefix.USER), email="admin@test.com", role=UserRole.ADMIN)
    assert await checker(user=admin_user) == admin_user

    # Member user fails ADMIN requirement and logs RFC 7807 structured error
    member_user = TokenData(id=generate_opaque_id(EntityPrefix.USER), email="member@test.com", role=UserRole.MEMBER)
    with caplog.at_level(logging.ERROR), pytest.raises(PermissionDeniedError) as exc:
        await checker(user=member_user)

    assert exc.value.details["required_role"] == UserRole.ADMIN.value
    assert exc.value.details["current_role"] == UserRole.MEMBER.value
    assert any("Insufficient privileges" in rec.message for rec in caplog.records)


@pytest.mark.asyncio
async def test_get_current_admin_user() -> None:
    """Test get_current_admin_user invokes admin role checker."""
    coro = get_current_admin_user()
    assert coro is not None
    coro.close()


def test_compiler_and_executor_dependencies() -> None:
    """Test prompt compiler and LLM task executor factory dependencies."""
    compiler = get_prompt_compiler()
    assert compiler is not None
    executor = get_llm_task_executor(compiler=compiler)
    assert executor.prompt_compiler is compiler


@pytest.mark.asyncio
async def test_repository_factory_dependencies() -> None:
    """Test repository factory dependencies bind the injected storage driver."""
    mock_driver = MagicMock()
    assert isinstance(await get_execution_repo(driver=mock_driver), ExecutionRepositoryImpl)
    assert isinstance(await get_report_artifact_repo(driver=mock_driver), ReportArtifactRepositoryImpl)
    assert isinstance(await get_identity_repo(driver=mock_driver), IdentityRepositoryImpl)
    assert isinstance(await get_workflow_repo(driver=mock_driver), WorkflowRepositoryImpl)
    assert isinstance(await get_component_repo(driver=mock_driver), ComponentRepositoryImpl)
    assert isinstance(await get_prompt_block_repo(driver=mock_driver), PromptBlockRepositoryImpl)
    assert isinstance(await get_agent_repo(driver=mock_driver), AgentRepositoryImpl)
    assert isinstance(await get_task_blueprint_repo(driver=mock_driver), TaskBlueprintRepositoryImpl)
    assert isinstance(await get_output_profile_repo(driver=mock_driver), OutputProfileRepositoryImpl)
    assert isinstance(await get_knowledge_repo(driver=mock_driver), KnowledgeRepositoryImpl)
    assert isinstance(await get_system_repo(driver=mock_driver), SystemRepositoryImpl)
    assert isinstance(await get_audit_repo(driver=mock_driver), AuditRepositoryImpl)


@pytest.mark.asyncio
async def test_service_factory_dependencies(fake_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Test service factory dependencies wire repositories and sub-services accurately."""
    mock_driver = MagicMock()

    usage_svc = get_usage_service(identity_repo=fake_repo, audit_repo=fake_repo)
    assert usage_svc.identity_repo is fake_repo
    assert usage_svc.audit_repo is fake_repo

    export_svc = await get_export_service(prompt_block_repo=fake_repo)
    assert export_svc.prompt_block_repo is fake_repo

    report_svc = await get_report_service(driver=mock_driver, prompt_block_repo=fake_repo)
    assert report_svc.export_service.prompt_block_repo is fake_repo

    wf_svc = await get_studio_workflow_service(
        workflow_repo=fake_repo,
        output_profile_repo=fake_repo,
        prompt_block_repo=fake_repo,
        system_repo=fake_repo,
    )
    assert wf_svc.workflow_repo is fake_repo

    pb_svc = await get_studio_prompt_block_service(
        prompt_block_repo=fake_repo,
        system_repo=fake_repo,
    )
    assert pb_svc.prompt_block_repo is fake_repo

    op_svc = await get_studio_output_profile_service(
        output_profile_repo=fake_repo,
        workflow_service=wf_svc,
    )
    assert op_svc.output_profile_repo is fake_repo
    assert op_svc.workflow_service is wf_svc

    sys_svc = await get_studio_system_config_service(system_repo=fake_repo)
    assert sys_svc.system_repo is fake_repo

    handler = get_llm_handler(repo=fake_repo)
    assert handler.repo is fake_repo

    mock_request = MagicMock()
    expected_pool = MagicMock()
    mock_request.app.state.arq_pool = expected_pool
    assert get_arq_pool(request=mock_request) is expected_pool

    mock_compiler = MagicMock()
    dag_executor = await get_dag_executor(
        exec_repo=fake_repo,
        workflow_repo=fake_repo,
        component_repo=fake_repo,
        identity_repo=fake_repo,
        audit_repo=fake_repo,
        system_repo=fake_repo,
        prompt_compiler=mock_compiler,
        prompt_block_repo=fake_repo,
        output_profile_repo=fake_repo,
    )
    assert dag_executor.exec_repo is fake_repo

    exec_service = await get_execution_service(
        exec_repo=fake_repo,
        workflow_repo=fake_repo,
        comp_repo=fake_repo,
        identity_repo=fake_repo,
        system_repo=fake_repo,
        usage_service=usage_svc,
        executor=dag_executor,
        prompt_block_repo=fake_repo,
        output_profile_repo=fake_repo,
    )
    assert exec_service.exec_repo is fake_repo
    assert exec_service.executor is dag_executor
