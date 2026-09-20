from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from backend_v2.api.dependencies import (
    get_auth_service,
    get_current_user_from_header,
    get_document_extraction_service,
    get_studio_simulation_service,
)
from backend_v2.exceptions import AuthenticationError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.settings import Settings


@pytest.fixture
def mock_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_settings() -> Any:
    return Settings(use_firebase_auth=False)


def test_get_auth_service(mock_repo: Any, mock_settings: Any) -> None:
    auth_service = get_auth_service(repo=mock_repo, settings=mock_settings)
    assert auth_service is not None


@pytest.mark.asyncio
async def test_get_current_user_from_header_missing_token() -> None:
    """Test get_current_user_from_header raises exception when token is missing."""
    mock_auth_service = AsyncMock()

    with pytest.raises(AuthenticationError) as exc:
        await get_current_user_from_header(auth_service=mock_auth_service, token=None)

    assert "Missing authentication token" in str(exc.value)


@pytest.mark.asyncio
async def test_get_current_user_from_header_valid_token() -> None:
    """Test get_current_user_from_header returns user data for valid token."""
    mock_auth_service = AsyncMock()
    expected_user = TokenData(id="usr_123", email="test@test.com", role=UserRole.MEMBER)
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
    expected_user = TokenData(id="usr_query", email="query@test.com", role=UserRole.MEMBER)
    mock_auth_service.verify_token.return_value = expected_user

    user = await get_current_user_from_header(auth_service=mock_auth_service, token=None, token_query="query_token_123")
    assert user == expected_user
    mock_auth_service.verify_token.assert_called_once_with("query_token_123")


@pytest.mark.asyncio
async def test_get_studio_simulation_service(mock_repo: Any) -> None:
    """Test get_studio_simulation_service injection."""
    service = await get_studio_simulation_service(
        prompt_block_service=AsyncMock(),
    )  # noqa: E501
    assert service is not None
    assert service.prompt_block_service is not None


def test_get_document_extraction_service() -> None:
    """Test get_document_extraction_service."""
    service = get_document_extraction_service()
    assert service is not None


@pytest.mark.asyncio
async def test_require_role_root_and_matches() -> None:
    """Test require_role dependency checker for root and matching roles."""
    from backend_v2.api.dependencies import require_role
    from backend_v2.exceptions import PermissionDeniedError

    checker = require_role(UserRole.ADMIN)

    # Root user bypasses role requirement
    root_user = TokenData(id="usr_root", email="root@test.com", role=UserRole.ROOT)
    assert await checker(user=root_user) == root_user

    # Admin user matches ADMIN requirement
    admin_user = TokenData(id="usr_admin", email="admin@test.com", role=UserRole.ADMIN)
    assert await checker(user=admin_user) == admin_user

    # Member user fails ADMIN requirement
    member_user = TokenData(id="usr_member", email="member@test.com", role=UserRole.MEMBER)
    with pytest.raises(PermissionDeniedError):
        await checker(user=member_user)


def test_compiler_and_executor_dependencies() -> None:
    """Test prompt compiler and LLM task executor factory dependencies."""
    from backend_v2.api.dependencies import get_llm_task_executor, get_prompt_compiler

    compiler = get_prompt_compiler()
    assert compiler is not None
    executor = get_llm_task_executor(compiler=compiler)
    assert executor is not None


@pytest.mark.asyncio
async def test_repository_factory_dependencies() -> None:
    """Test repository factory dependencies."""
    from backend_v2.api.dependencies import (
        get_agent_repo,
        get_audit_repo,
        get_component_repo,
        get_execution_repo,
        get_identity_repo,
        get_knowledge_repo,
        get_output_profile_repo,
        get_prompt_block_repo,
        get_report_artifact_repo,
        get_system_repo,
        get_task_blueprint_repo,
        get_workflow_repo,
    )

    mock_driver = MagicMock()
    assert await get_execution_repo(driver=mock_driver) is not None
    assert await get_report_artifact_repo(driver=mock_driver) is not None
    assert await get_identity_repo(driver=mock_driver) is not None
    assert await get_workflow_repo(driver=mock_driver) is not None
    assert await get_component_repo(driver=mock_driver) is not None
    assert await get_prompt_block_repo(driver=mock_driver) is not None
    assert await get_agent_repo(driver=mock_driver) is not None
    assert await get_task_blueprint_repo(driver=mock_driver) is not None
    assert await get_output_profile_repo(driver=mock_driver) is not None
    assert await get_knowledge_repo(driver=mock_driver) is not None
    assert await get_system_repo(driver=mock_driver) is not None
    assert await get_audit_repo(driver=mock_driver) is not None


@pytest.mark.asyncio
async def test_service_factory_dependencies() -> None:
    """Test service factory dependencies."""
    from backend_v2.api.dependencies import (
        get_arq_pool,
        get_dag_executor,
        get_execution_service,
        get_export_service,
        get_llm_handler,
        get_report_service,
        get_studio_output_profile_service,
        get_studio_prompt_block_service,
        get_studio_system_config_service,
        get_studio_workflow_service,
        get_usage_service,
    )

    mock_driver = MagicMock()
    mock_identity_repo = AsyncMock()
    mock_audit_repo = AsyncMock()
    mock_comp_repo = AsyncMock()
    mock_workflow_repo = AsyncMock()
    mock_output_profile_repo = AsyncMock()
    mock_prompt_block_repo = AsyncMock()
    mock_system_repo = AsyncMock()

    usage_svc = get_usage_service(identity_repo=mock_identity_repo, audit_repo=mock_audit_repo)
    assert usage_svc is not None

    export_svc = await get_export_service(comp_repo=mock_comp_repo)
    assert export_svc is not None

    report_svc = await get_report_service(driver=mock_driver, comp_repo=mock_comp_repo)
    assert report_svc is not None

    wf_svc = await get_studio_workflow_service(
        workflow_repo=mock_workflow_repo,
        output_profile_repo=mock_output_profile_repo,
        prompt_block_repo=mock_prompt_block_repo,
        system_repo=mock_system_repo,
    )
    assert wf_svc is not None

    pb_svc = await get_studio_prompt_block_service(
        prompt_block_repo=mock_prompt_block_repo,
        system_repo=mock_system_repo,
    )
    assert pb_svc is not None

    op_svc = await get_studio_output_profile_service(
        output_profile_repo=mock_output_profile_repo,
        workflow_service=wf_svc,
    )
    assert op_svc is not None

    sys_svc = await get_studio_system_config_service(system_repo=mock_system_repo)
    assert sys_svc is not None

    handler = get_llm_handler(repo=mock_comp_repo)
    assert handler is not None

    mock_request = MagicMock()
    mock_request.app.state.arq_pool = MagicMock()
    assert get_arq_pool(request=mock_request) is not None

    mock_compiler = MagicMock()
    mock_exec_repo = AsyncMock()
    dag_executor = await get_dag_executor(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        component_repo=mock_comp_repo,
        identity_repo=mock_identity_repo,
        audit_repo=mock_audit_repo,
        system_repo=mock_system_repo,
        prompt_compiler=mock_compiler,
        prompt_block_repo=mock_prompt_block_repo,
        output_profile_repo=mock_output_profile_repo,
    )
    assert dag_executor is not None

    exec_service = await get_execution_service(
        exec_repo=mock_exec_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=mock_comp_repo,
        identity_repo=mock_identity_repo,
        system_repo=mock_system_repo,
        usage_service=usage_svc,
        executor=dag_executor,
        prompt_block_repo=mock_prompt_block_repo,
        output_profile_repo=mock_output_profile_repo,
    )
    assert exec_service is not None
