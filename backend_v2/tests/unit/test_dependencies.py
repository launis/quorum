"""Unit tests for FastAPI dependency injection providers in backend_v2/api/dependencies.py."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from backend_v2.api.dependencies import (
    get_arq_pool,
    get_audit_repo,
    get_auth_service,
    get_current_admin_user,
    get_current_user_from_header,
    get_dag_executor,
    get_document_extraction_service,
    get_execution_repo,
    get_execution_service,
    get_export_service,
    get_identity_repo,
    get_llm_handler,
    get_llm_task_executor,
    get_output_profile_repo,
    get_prompt_block_repo,
    get_prompt_compiler,
    get_report_artifact_repo,
    get_report_service,
    get_revocation_cache,
    get_studio_output_profile_service,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
    get_studio_system_config_service,
    get_studio_task_brief_service,
    get_studio_workflow_service,
    get_system_repo,
    get_task_brief_repo,
    get_tenant_rate_limit_service,
    get_uow_factory,
    get_usage_service,
    get_workflow_repo,
    require_role,
)
from backend_v2.core.redis_security import RevocationCache
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.repositories.components.task_brief import TaskBriefRepositoryImpl
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.database.repositories.report_artifact import ReportArtifactRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import (
    AuthenticationError,
    ErrorCodes,
    PermissionDeniedError,
    ServiceUnavailableError,
)
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


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


def test_get_uow_factory() -> None:
    """Test get_uow_factory delegates to get_registered_uow_factory."""

    def expected_factory() -> InMemoryUnitOfWork:
        return InMemoryUnitOfWork()

    with patch(
        "backend_v2.api.dependencies.get_registered_uow_factory",
        return_value=expected_factory,
    ) as mock_registered:
        resolved = get_uow_factory()
        assert resolved is expected_factory
        mock_registered.assert_called_once_with()


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
    assert exc.value.details == {"error_code": ErrorCodes.AUTHENTICATION_FAILED.value}
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

    assert exc.value.details == {"error_code": ErrorCodes.AUTHENTICATION_FAILED.value}
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
async def test_get_current_user_from_header_revocation_cache_failure_and_error() -> None:
    """Verify get_current_user_from_header invokes RevocationCache.assert_not_revoked immediately after verify_token."""
    mock_auth_service = AsyncMock()
    user_id = generate_opaque_id(EntityPrefix.USER)
    expected_user = TokenData(
        id=user_id,
        email="revoked@test.com",
        role=UserRole.MEMBER,
        jti="0195f3a0-0000-7000-8000-000000000001",
    )
    mock_auth_service.verify_token.return_value = expected_user
    mock_credentials = MagicMock(spec=HTTPAuthorizationCredentials)
    mock_credentials.credentials = "jwt_token_abc"

    mock_redis = AsyncMock()
    mock_redis.mget.return_value = [None, None]
    revocation_cache = RevocationCache(redis=mock_redis)

    # 1. Unrevoked token passes
    verified = await get_current_user_from_header(
        auth_service=mock_auth_service,
        token=mock_credentials,
        revocation_cache=revocation_cache,
    )
    assert verified == expected_user
    mock_redis.mget.assert_awaited_once_with(
        f"revoked:usr:{user_id}",
        "revoked:jti:0195f3a0-0000-7000-8000-000000000001",
    )

    # 2. Revoked token raises 401 AuthenticationError (AUTH_TOKEN_EXPIRED)
    mock_redis.mget.return_value = [None, "1"]
    with pytest.raises(AuthenticationError) as exc_revoked:
        await get_current_user_from_header(
            auth_service=mock_auth_service,
            token=mock_credentials,
            revocation_cache=revocation_cache,
        )
    assert exc_revoked.value.status_code == 401
    assert exc_revoked.value.details["error_code"] == ErrorCodes.AUTH_TOKEN_EXPIRED.value

    # 3. Redis connection error enforces Fail-Closed 503 ServiceUnavailableError
    mock_redis.mget.side_effect = ConnectionError("Redis offline")
    with pytest.raises(ServiceUnavailableError) as exc_down:
        await get_current_user_from_header(
            auth_service=mock_auth_service,
            token=mock_credentials,
            revocation_cache=revocation_cache,
        )
    assert exc_down.value.status_code == 503
    assert exc_down.value.details["error_code"] == ErrorCodes.SERVICE_UNAVAILABLE.value


def test_get_revocation_cache_and_tenant_rate_limit_service() -> None:
    """Verify get_revocation_cache and get_tenant_rate_limit_service bind request.app.state.arq_pool."""
    mock_request = MagicMock()
    expected_pool = MagicMock()
    mock_request.app.state.arq_pool = expected_pool

    rev_cache = get_revocation_cache(request=mock_request)
    assert rev_cache is not None
    assert rev_cache.redis is expected_pool

    rate_limiter = get_tenant_rate_limit_service(request=mock_request)
    assert rate_limiter.redis is expected_pool


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

    assert exc.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value
    assert exc.value.details["required_role"] == UserRole.ADMIN.value
    assert exc.value.details["current_role"] == UserRole.MEMBER.value
    assert any(ErrorCodes.PERMISSION_DENIED.name in rec.message for rec in caplog.records)


@pytest.mark.asyncio
async def test_require_role_multi_role_sequence_boundary(caplog: pytest.LogCaptureFixture) -> None:
    """Contract: require_role([UserRole.ADMIN, UserRole.MANAGER]) permits ROOT/ADMIN/MANAGER and rejects MEMBER/VIEWER."""
    checker = require_role([UserRole.ADMIN, UserRole.MANAGER])

    for allowed_role in (UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER):
        user = TokenData(
            id=generate_opaque_id(EntityPrefix.USER),
            email=f"{allowed_role.value}@test.com",
            role=allowed_role,
        )
        assert await checker(user=user) == user

    for denied_role in (UserRole.MEMBER, UserRole.VIEWER):
        denied_user = TokenData(
            id=generate_opaque_id(EntityPrefix.USER),
            email=f"{denied_role.value}@test.com",
            role=denied_role,
        )
        caplog.clear()
        with caplog.at_level(logging.ERROR), pytest.raises(PermissionDeniedError) as exc:
            await checker(user=denied_user)
        assert exc.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value
        assert exc.value.details["current_role"] == denied_role.value
        assert any(ErrorCodes.PERMISSION_DENIED.name in rec.message for rec in caplog.records)


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
    """Test repository factory dependencies bind the injected UnitOfWork factory."""
    uow = InMemoryUnitOfWork()

    def uow_factory() -> InMemoryUnitOfWork:
        return uow

    assert isinstance(await get_execution_repo(uow_factory=uow_factory), ExecutionRepositoryImpl)
    assert isinstance(await get_report_artifact_repo(uow_factory=uow_factory), ReportArtifactRepositoryImpl)
    assert isinstance(await get_identity_repo(uow_factory=uow_factory), IdentityRepositoryImpl)
    assert isinstance(await get_workflow_repo(uow_factory=uow_factory), WorkflowRepositoryImpl)
    assert isinstance(await get_prompt_block_repo(uow_factory=uow_factory), PromptBlockRepositoryImpl)
    assert isinstance(await get_task_brief_repo(uow_factory=uow_factory), TaskBriefRepositoryImpl)
    assert isinstance(await get_output_profile_repo(uow_factory=uow_factory), OutputProfileRepositoryImpl)
    assert isinstance(await get_system_repo(uow_factory=uow_factory), SystemRepositoryImpl)
    assert isinstance(await get_audit_repo(uow_factory=uow_factory), AuditRepositoryImpl)


@pytest.mark.asyncio
async def test_service_factory_dependencies(fake_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Test service factory dependencies wire repositories and sub-services accurately."""
    uow = InMemoryUnitOfWork()

    def uow_factory() -> InMemoryUnitOfWork:
        return uow

    usage_svc = get_usage_service(identity_repo=fake_repo, audit_repo=fake_repo)
    assert usage_svc.identity_repo is fake_repo
    assert usage_svc.audit_repo is fake_repo

    export_svc = await get_export_service(prompt_block_repo=fake_repo)
    assert export_svc.prompt_block_repo is fake_repo

    report_svc = await get_report_service(prompt_block_repo=fake_repo, uow_factory=uow_factory)
    assert report_svc.export_service.prompt_block_repo is fake_repo

    wf_svc = await get_studio_workflow_service(
        workflow_repo=fake_repo,
        output_profile_repo=fake_repo,
        prompt_block_repo=fake_repo,
        system_repo=fake_repo,
        uow_factory=uow_factory,
    )
    assert wf_svc.workflow_repo is fake_repo

    pb_svc = await get_studio_prompt_block_service(
        prompt_block_repo=fake_repo,
        system_repo=fake_repo,
    )
    assert pb_svc.prompt_block_repo is fake_repo

    tb_svc = await get_studio_task_brief_service(
        task_brief_repo=fake_repo,
    )
    assert tb_svc.task_brief_repo is fake_repo

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
        identity_repo=fake_repo,
        system_repo=fake_repo,
        usage_service=usage_svc,
        executor=dag_executor,
        prompt_block_repo=fake_repo,
        task_brief_repo=fake_repo,
        output_profile_repo=fake_repo,
    )
    assert exec_service.exec_repo is fake_repo
    assert exec_service.executor is dag_executor
