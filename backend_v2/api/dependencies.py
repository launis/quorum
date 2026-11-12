"""FastAPI dependency injection module.

Provides global dependencies for the FastAPI routers, handling everything
from database drivers to complex service layer instantiations.
"""

import logging
from collections.abc import Awaitable, Callable, Sequence
from typing import Annotated, Any, cast

from arq.connections import ArqRedis
from fastapi import Depends, Query, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.datastructures import State

from backend_v2.core.redis_security import RevocationCache, TenantRateLimitService
from backend_v2.database.interfaces import (
    IAuditRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    IReportArtifactRepository,
    ISystemRepository,
    ITaskBriefRepository,
    IWorkflowRepository,
    UnitOfWorkFactory,
    get_registered_uow_factory,
)
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.database.repositories.components.output_profile import OutputProfileRepositoryImpl
from backend_v2.database.repositories.components.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.repositories.components.task_brief import TaskBriefRepositoryImpl
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.database.repositories.report_artifact import ReportArtifactRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AuthenticationError, ErrorCodes, PermissionDeniedError
from backend_v2.llm.handler import LLMHandler
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.auth import AuthService
from backend_v2.services.document_extraction import DocumentExtractionService
from backend_v2.services.execution import ExecutionService
from backend_v2.services.export import ExportService
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.services.report import ReportService
from backend_v2.services.studio import (
    StudioOutputProfileService,
    StudioPromptBlockService,
    StudioSimulationService,
    StudioSystemConfigService,
    StudioTaskBriefService,
    StudioWorkflowService,
)
from backend_v2.services.usage_service import UsageService
from backend_v2.settings import Settings, get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "ArqPoolDep",
    "AuditRepoDep",
    "AuthServiceDep",
    "CurrentUserDep",
    "DocumentExtractionServiceDep",
    "ExecutionRepoDep",
    "ExecutionServiceDep",
    "ExecutorDep",
    "ExportServiceDep",
    "IdentityRepoDep",
    "LLMHandlerDep",
    "LLMTaskExecutorDep",
    "OutputProfileRepoDep",
    "PromptBlockRepoDep",
    "PromptCompilerDep",
    "ReportArtifactRepoDep",
    "ReportServiceDep",
    "RevocationCacheDep",
    "StudioOutputProfileServiceDep",
    "StudioPromptBlockServiceDep",
    "StudioSimulationServiceDep",
    "StudioSystemConfigServiceDep",
    "StudioTaskBriefServiceDep",
    "StudioWorkflowServiceDep",
    "SystemRepoDep",
    "TaskBriefRepoDep",
    "TenantRateLimitServiceDep",
    "UoWFactoryDep",
    "UsageServiceDep",
    "UserDep",
    "WorkflowRepoDep",
    "get_arq_pool",
    "get_audit_repo",
    "get_auth_service",
    "get_current_admin_user",
    "get_current_user_from_header",
    "get_dag_executor",
    "get_document_extraction_service",
    "get_execution_repo",
    "get_execution_service",
    "get_export_service",
    "get_identity_repo",
    "get_llm_handler",
    "get_llm_task_executor",
    "get_output_profile_repo",
    "get_prompt_block_repo",
    "get_prompt_compiler",
    "get_report_artifact_repo",
    "get_report_service",
    "get_revocation_cache",
    "get_studio_output_profile_service",
    "get_studio_prompt_block_service",
    "get_studio_simulation_service",
    "get_studio_system_config_service",
    "get_studio_task_brief_service",
    "get_studio_workflow_service",
    "get_system_repo",
    "get_task_brief_repo",
    "get_tenant_rate_limit_service",
    "get_uow_factory",
    "get_usage_service",
    "get_workflow_repo",
    "require_role",
    "security",
]

security = HTTPBearer(auto_error=False)


def get_uow_factory() -> UnitOfWorkFactory | None:
    """Return the process-scoped UnitOfWorkFactory registered for transactional boundaries.

    Returns:
        Registered UnitOfWorkFactory callable or None.
    """
    return get_registered_uow_factory()


UoWFactoryDep = Annotated[UnitOfWorkFactory | None, Depends(get_uow_factory)]


async def get_execution_repo(uow_factory: UoWFactoryDep = None) -> IExecutionRepository:
    """Instantiate the execution repository.

    Args:
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        Execution repository instance.
    """
    return ExecutionRepositoryImpl(uow_factory)


ExecutionRepoDep = Annotated[IExecutionRepository, Depends(get_execution_repo)]


async def get_report_artifact_repo(uow_factory: UoWFactoryDep = None) -> IReportArtifactRepository:
    """Instantiate the report artifact repository.

    Args:
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        Report artifact repository instance.
    """
    return ReportArtifactRepositoryImpl(uow_factory)


ReportArtifactRepoDep = Annotated[IReportArtifactRepository, Depends(get_report_artifact_repo)]


async def get_identity_repo(uow_factory: UoWFactoryDep = None) -> IIdentityRepository:
    """Instantiate the identity repository.

    Args:
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        Identity repository instance.
    """
    return IdentityRepositoryImpl(uow_factory)


IdentityRepoDep = Annotated[IIdentityRepository, Depends(get_identity_repo)]


async def get_workflow_repo(uow_factory: UoWFactoryDep = None) -> IWorkflowRepository:
    """Instantiate the workflow repository.

    Args:
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        Workflow repository instance.
    """
    return WorkflowRepositoryImpl(uow_factory)


WorkflowRepoDep = Annotated[IWorkflowRepository, Depends(get_workflow_repo)]


async def get_prompt_block_repo(uow_factory: UoWFactoryDep = None) -> IPromptBlockRepository:
    """Instantiate the prompt block repository.

    Args:
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        Prompt block repository instance.
    """
    return PromptBlockRepositoryImpl(uow_factory)


PromptBlockRepoDep = Annotated[IPromptBlockRepository, Depends(get_prompt_block_repo)]


async def get_task_brief_repo(uow_factory: UoWFactoryDep = None) -> ITaskBriefRepository:
    """Instantiate the task brief repository.

    Args:
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        Task brief repository instance.
    """
    return TaskBriefRepositoryImpl(uow_factory)


TaskBriefRepoDep = Annotated[ITaskBriefRepository, Depends(get_task_brief_repo)]


async def get_output_profile_repo(uow_factory: UoWFactoryDep = None) -> IOutputProfileRepository:
    """Instantiate the output profile repository.

    Args:
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        Output profile repository instance.
    """
    return OutputProfileRepositoryImpl(uow_factory)


OutputProfileRepoDep = Annotated[IOutputProfileRepository, Depends(get_output_profile_repo)]


async def get_system_repo(uow_factory: UoWFactoryDep = None) -> ISystemRepository:
    """Instantiate the system repository.

    Args:
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        System repository instance.
    """
    return SystemRepositoryImpl(uow_factory)


SystemRepoDep = Annotated[ISystemRepository, Depends(get_system_repo)]


async def get_audit_repo(uow_factory: UoWFactoryDep = None) -> IAuditRepository:
    """Instantiate the audit repository.

    Args:
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        Audit repository instance.
    """
    return AuditRepositoryImpl(uow_factory)


AuditRepoDep = Annotated[IAuditRepository, Depends(get_audit_repo)]


def get_usage_service(identity_repo: IdentityRepoDep, audit_repo: AuditRepoDep) -> UsageService:
    """Instantiate the usage service.

    Args:
        identity_repo: Identity repository.
        audit_repo: Audit repository.

    Returns:
        Usage service instance.
    """
    return UsageService(identity_repo=identity_repo, audit_repo=audit_repo)


UsageServiceDep = Annotated[UsageService, Depends(get_usage_service)]


def get_revocation_cache(request: Request) -> RevocationCache | None:
    """Instantiate the Redis revocation cache from the application Arq Redis pool.

    Args:
        request: Current HTTP request.

    Returns:
        Configured RevocationCache instance when Redis state is initialized, or None.
    """
    if not isinstance(request.app.state, State):
        return RevocationCache(redis=request.app.state.arq_pool)
    if "arq_pool" not in request.app.state._state:
        return None
    return RevocationCache(redis=request.app.state.arq_pool)


RevocationCacheDep = Annotated[RevocationCache | None, Depends(get_revocation_cache)]


def get_tenant_rate_limit_service(request: Request) -> TenantRateLimitService:
    """Instantiate the per-tenant Redis sliding-window rate limiter from application state.

    Args:
        request: Current HTTP request.

    Returns:
        Configured TenantRateLimitService instance.
    """
    if not isinstance(request.app.state, State):
        return TenantRateLimitService(redis=request.app.state.arq_pool)
    if "arq_pool" not in request.app.state._state:
        return TenantRateLimitService(redis=None)
    return TenantRateLimitService(redis=request.app.state.arq_pool)


TenantRateLimitServiceDep = Annotated[TenantRateLimitService, Depends(get_tenant_rate_limit_service)]


def get_auth_service(
    repo: IdentityRepoDep,
    settings: Annotated[Settings, Depends(get_settings)],
    revocation_cache: Annotated[RevocationCache | None, Depends(get_revocation_cache)] = None,
) -> AuthService:
    """Instantiate the authentication service.

    Args:
        repo: Identity repository.
        settings: Application settings.
        revocation_cache: Optional Redis revocation cache for kill-switch enforcement.

    Returns:
        Auth service instance.
    """
    return AuthService(
        repo=repo,
        use_firebase=settings.use_firebase_auth,
        revocation_cache=revocation_cache,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user_from_header(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[HTTPAuthorizationCredentials | None, Security(security)] = None,
    token_query: Annotated[str | None, Query(alias="token")] = None,
    revocation_cache: Annotated[RevocationCache | None, Depends(get_revocation_cache)] = None,
) -> TokenData:
    """Extract and verify the current user from the authorization header or query parameter.

    Args:
        auth_service: Authentication service.
        token: Optional HTTP bearer token.
        token_query: Optional query parameter token fallback for file streaming.
        revocation_cache: Optional Redis revocation cache for Dual-Key MGET kill-switch enforcement.

    Returns:
        Verified token data.

    Raises:
        AuthenticationError: With ErrorCodes.AUTHENTICATION_FAILED if the token is missing or invalid,
            or ErrorCodes.AUTH_TOKEN_EXPIRED if revoked in Redis.
        ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE if Redis kill-switch check fails.
    """
    raw_token = token_query
    if token is not None:
        raw_token = token.credentials
    if not raw_token:
        msg = "Missing authentication token"
        logger.error(
            "[Dependencies] %s: %s",
            ErrorCodes.AUTHENTICATION_FAILED.name,
            msg,
            extra={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
        )
        raise AuthenticationError(
            message=msg,
            details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value},
        )
    token_data = await auth_service.verify_token(raw_token)
    if revocation_cache is not None:
        await revocation_cache.assert_not_revoked(token_data)
    return token_data


UserDep = Annotated[TokenData, Depends(get_current_user_from_header)]
CurrentUserDep = UserDep


def require_role(allowed_roles: Sequence[UserRole] | UserRole) -> Callable[..., Awaitable[TokenData]]:
    """Return a dependency that validates the user possesses one of the allowed roles.

    Implicitly allows ROOT for all operations.

    Args:
        allowed_roles: A single UserRole or sequence of allowed UserRole values.

    Returns:
        A FastAPI dependency checker function.
    """
    role_tuple: tuple[UserRole, ...] = (allowed_roles,) if isinstance(allowed_roles, UserRole) else tuple(allowed_roles)
    required_display = (
        allowed_roles.value if isinstance(allowed_roles, UserRole) else ", ".join(r.value for r in role_tuple)
    )

    async def _role_checker(user: TokenData = Depends(get_current_user_from_header)) -> TokenData:
        """Verify that the authenticated user possesses an allowed role.

        Args:
            user: Authenticated user token data.

        Returns:
            Verified user token data.

        Raises:
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks an allowed role.
        """
        if user.role == UserRole.ROOT or user.role in role_tuple:
            return user
        msg = f"Insufficient privileges. Required: {required_display}"
        logger.error(
            "[Dependencies] %s: %s",
            ErrorCodes.PERMISSION_DENIED.name,
            msg,
            extra={
                "error_code": ErrorCodes.PERMISSION_DENIED.value,
                "required_role": required_display,
                "current_role": user.role.value,
            },
        )
        raise PermissionDeniedError(
            message=msg,
            details={
                "error_code": ErrorCodes.PERMISSION_DENIED.value,
                "required_role": required_display,
                "current_role": user.role.value,
            },
        )

    return _role_checker


def get_current_admin_user() -> Any:
    """Retrieve the current user and ensure they possess admin privileges.

    Returns:
        Admin user dependency object.
    """
    return require_role(UserRole.ADMIN)()


def get_prompt_compiler() -> PromptCompiler:
    """Instantiate the prompt compiler.

    Returns:
        Prompt compiler instance.
    """
    return PromptCompiler()


PromptCompilerDep = Annotated[PromptCompiler, Depends(get_prompt_compiler)]


def get_llm_task_executor(compiler: PromptCompilerDep) -> LLMTaskExecutor:
    """Instantiate the LLM task executor.

    Args:
        compiler: Prompt compiler.

    Returns:
        LLM task executor instance.
    """
    return LLMTaskExecutor(prompt_compiler=compiler)


LLMTaskExecutorDep = Annotated[LLMTaskExecutor, Depends(get_llm_task_executor)]


async def get_dag_executor(
    exec_repo: ExecutionRepoDep,
    workflow_repo: WorkflowRepoDep,
    identity_repo: IdentityRepoDep,
    audit_repo: AuditRepoDep,
    system_repo: SystemRepoDep,
    prompt_compiler: PromptCompilerDep,
    prompt_block_repo: PromptBlockRepoDep,
    output_profile_repo: OutputProfileRepoDep,
) -> DAGExecutor:
    """Instantiate the execution DAG orchestrator.

    Args:
        exec_repo: Execution repository.
        workflow_repo: Workflow repository.
        identity_repo: Identity repository.
        audit_repo: Audit repository.
        system_repo: System repository.
        prompt_compiler: Prompt compiler.
        prompt_block_repo: Prompt block repository.
        output_profile_repo: Output profile repository.

    Returns:
        DAG executor instance.
    """
    rag_preflight = RAGPreflightService(
        workflow_repo=workflow_repo,
        system_repo=system_repo,
        prompt_compiler=prompt_compiler,
    )
    return DAGExecutor(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        identity_repo=identity_repo,
        audit_repo=audit_repo,
        system_repo=system_repo,
        prompt_compiler=prompt_compiler,
        rag_preflight=rag_preflight,
    )


ExecutorDep = Annotated[DAGExecutor, Depends(get_dag_executor)]


async def get_execution_service(
    exec_repo: ExecutionRepoDep,
    workflow_repo: WorkflowRepoDep,
    identity_repo: IdentityRepoDep,
    system_repo: SystemRepoDep,
    usage_service: UsageServiceDep,
    executor: Annotated[DAGExecutor, Depends(get_dag_executor)],
    prompt_block_repo: PromptBlockRepoDep,
    task_brief_repo: TaskBriefRepoDep,
    output_profile_repo: OutputProfileRepoDep,
) -> ExecutionService:
    """Instantiate the high-level execution service.

    Args:
        exec_repo: Execution repository.
        workflow_repo: Workflow repository.
        identity_repo: Identity repository.
        system_repo: System repository.
        usage_service: Usage service.
        executor: DAG executor.
        prompt_block_repo: Prompt block repository.
        task_brief_repo: Task brief repository.
        output_profile_repo: Output profile repository.

    Returns:
        Execution service instance.
    """
    return ExecutionService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        prompt_block_repo=prompt_block_repo,
        task_brief_repo=task_brief_repo,
        output_profile_repo=output_profile_repo,
        identity_repo=identity_repo,
        system_repo=system_repo,
        usage_service=usage_service,
        executor=executor,
    )


ExecutionServiceDep = Annotated[ExecutionService, Depends(get_execution_service)]


async def get_export_service(
    prompt_block_repo: PromptBlockRepoDep,
) -> ExportService:
    """Instantiate the export service.

    Args:
        prompt_block_repo: Prompt block repository.

    Returns:
        Export service instance.
    """
    return ExportService(prompt_block_repo=prompt_block_repo)


ExportServiceDep = Annotated[ExportService, Depends(get_export_service)]


async def get_report_service(
    prompt_block_repo: PromptBlockRepoDep,
    uow_factory: UoWFactoryDep = None,
) -> ReportService:
    """Instantiate the report artifact service.

    Args:
        prompt_block_repo: Prompt block repository.
        uow_factory: Optional UnitOfWork factory override.

    Returns:
        Report service instance.
    """
    repo = UnifiedWorkflowRepository(uow_factory)
    export_service = ExportService(prompt_block_repo=prompt_block_repo)
    return ReportService(repo=repo, export_service=export_service)


ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]


async def get_studio_workflow_service(
    workflow_repo: WorkflowRepoDep,
    output_profile_repo: OutputProfileRepoDep,
    prompt_block_repo: PromptBlockRepoDep,
    system_repo: SystemRepoDep,
    uow_factory: UoWFactoryDep = None,
) -> StudioWorkflowService:
    """Instantiate the studio workflow service.

    Args:
        workflow_repo: Workflow repository.
        output_profile_repo: Output profile repository.
        prompt_block_repo: Prompt block repository.
        system_repo: System repository.
        uow_factory: Optional UnitOfWork factory for multi-entity transactions.

    Returns:
        Studio workflow service instance.
    """
    resolved_uow_factory: UnitOfWorkFactory | None = get_registered_uow_factory()
    if uow_factory is not None:
        resolved_uow_factory = uow_factory
    return StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
        uow_factory=resolved_uow_factory,
    )


StudioWorkflowServiceDep = Annotated[StudioWorkflowService, Depends(get_studio_workflow_service)]


async def get_studio_prompt_block_service(
    prompt_block_repo: PromptBlockRepoDep,
    system_repo: SystemRepoDep,
) -> StudioPromptBlockService:
    """Instantiate the studio prompt block service.

    Args:
        prompt_block_repo: Prompt block repository.
        system_repo: System repository.

    Returns:
        Studio prompt block service instance.
    """
    return StudioPromptBlockService(
        prompt_block_repo=prompt_block_repo,
        system_repo=system_repo,
    )


StudioPromptBlockServiceDep = Annotated[StudioPromptBlockService, Depends(get_studio_prompt_block_service)]


async def get_studio_task_brief_service(
    task_brief_repo: TaskBriefRepoDep,
) -> StudioTaskBriefService:
    """Instantiate the studio task brief service.

    Args:
        task_brief_repo: Task brief repository.

    Returns:
        Studio task brief service instance.
    """
    return StudioTaskBriefService(
        task_brief_repo=task_brief_repo,
    )


StudioTaskBriefServiceDep = Annotated[StudioTaskBriefService, Depends(get_studio_task_brief_service)]


async def get_studio_output_profile_service(
    output_profile_repo: OutputProfileRepoDep,
    workflow_service: StudioWorkflowServiceDep,
) -> StudioOutputProfileService:
    """Instantiate the studio output profile service.

    Args:
        output_profile_repo: Output profile repository.
        workflow_service: Studio workflow service.

    Returns:
        Studio output profile service instance.
    """
    return StudioOutputProfileService(
        output_profile_repo=output_profile_repo,
        workflow_service=workflow_service,
    )


StudioOutputProfileServiceDep = Annotated[StudioOutputProfileService, Depends(get_studio_output_profile_service)]


async def get_studio_system_config_service(
    system_repo: SystemRepoDep,
) -> StudioSystemConfigService:
    """Instantiate the studio system config service.

    Args:
        system_repo: System repository.

    Returns:
        Studio system config service instance.
    """
    return StudioSystemConfigService(system_repo=system_repo)


StudioSystemConfigServiceDep = Annotated[StudioSystemConfigService, Depends(get_studio_system_config_service)]


async def get_studio_simulation_service(
    prompt_block_service: StudioPromptBlockServiceDep,
) -> StudioSimulationService:
    """Instantiate the studio simulation service.

    Args:
        prompt_block_service: Studio prompt block service.

    Returns:
        Studio simulation service instance.
    """
    return StudioSimulationService(
        prompt_block_service=prompt_block_service,
    )


StudioSimulationServiceDep = Annotated[StudioSimulationService, Depends(get_studio_simulation_service)]


def get_llm_handler(repo: SystemRepoDep) -> LLMHandler:
    """Instantiate the direct LLM handler.

    Args:
        repo: System repository.

    Returns:
        LLM handler instance.
    """
    return LLMHandler(repo=repo)


LLMHandlerDep = Annotated[LLMHandler, Depends(get_llm_handler)]


def get_arq_pool(request: Request) -> ArqRedis:
    """Retrieve the Arq Redis connection pool from application state.

    Args:
        request: Current HTTP request.

    Returns:
        ArqRedis connection pool.
    """
    return cast(ArqRedis, request.app.state.arq_pool)


ArqPoolDep = Annotated[ArqRedis, Depends(get_arq_pool)]


def get_document_extraction_service() -> DocumentExtractionService:
    """Instantiate the document extraction service.

    Returns:
        Document extraction service instance.
    """
    return DocumentExtractionService()


DocumentExtractionServiceDep = Annotated[DocumentExtractionService, Depends(get_document_extraction_service)]
