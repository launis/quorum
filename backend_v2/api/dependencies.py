"""FastAPI dependency injection module.

Provides global dependencies for the FastAPI routers, handling everything
from database drivers to complex service layer instantiations.
"""

import logging
from typing import TYPE_CHECKING, Annotated, Any, cast

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass

from arq.connections import ArqRedis
from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend_v2.database.driver import StorageDriver
from backend_v2.database.factory import get_driver
from backend_v2.database.interfaces import (
    IAgentRepository,
    IAuditRepository,
    IComponentRepository,
    IExecutionPersonaRepository,
    IExecutionRepository,
    IExtractionProtocolRepository,
    IIdentityRepository,
    IKnowledgeRepository,
    IMatrixRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    IRoleRepository,
    ISystemRepository,
    ITaskBlueprintRepository,
    IWorkflowRepository,
)
from backend_v2.database.repositories.agent import AgentRepositoryImpl
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.database.repositories.knowledge import KnowledgeRepositoryImpl
from backend_v2.database.repositories.output_profile import OutputProfileRepositoryImpl
from backend_v2.database.repositories.prompt_block import PromptBlockRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.task_blueprint import TaskBlueprintRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import AuthenticationError, PermissionDeniedError
from backend_v2.llm.handler import LLMHandler
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.auth import AuthService
from backend_v2.services.document_extraction import DocumentExtractionService
from backend_v2.services.execution import ExecutionService
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.studio import (
    StudioLexiconService,
    StudioOutputProfileService,
    StudioPromptBlockService,
    StudioSimulationService,
    StudioSystemConfigService,
    StudioWorkflowService,
)
from backend_v2.services.usage_service import UsageService
from backend_v2.settings import Settings, get_settings

security = HTTPBearer(auto_error=False)


async def get_db_driver(settings: Annotated[Settings, Depends(get_settings)]) -> StorageDriver:
    """Retrieve the global database storage driver.

    Args:
        settings: Application settings.

    Returns:
        The instantiated storage driver.
    """
    return await get_driver(settings)


DriverDep = Annotated[StorageDriver, Depends(get_db_driver)]


async def get_execution_repo(driver: DriverDep) -> IExecutionRepository:
    """Instantiate the execution repository.

    Args:
        driver: Storage driver.

    Returns:
        Execution repository instance.
    """
    return ExecutionRepositoryImpl(driver)


ExecutionRepoDep = Annotated[IExecutionRepository, Depends(get_execution_repo)]


async def get_identity_repo(driver: DriverDep) -> IIdentityRepository:
    """Instantiate the identity repository.

    Args:
        driver: Storage driver.

    Returns:
        Identity repository instance.
    """
    return IdentityRepositoryImpl(driver)


IdentityRepoDep = Annotated[IIdentityRepository, Depends(get_identity_repo)]


async def get_workflow_repo(driver: DriverDep) -> IWorkflowRepository:
    """Instantiate the workflow repository.

    Args:
        driver: Storage driver.

    Returns:
        Workflow repository instance.
    """
    return WorkflowRepositoryImpl(driver)


WorkflowRepoDep = Annotated[IWorkflowRepository, Depends(get_workflow_repo)]


async def get_component_repo(driver: DriverDep) -> IComponentRepository:
    """Instantiate the component repository.

    Args:
        driver: Storage driver.

    Returns:
        Component repository instance.
    """
    return ComponentRepositoryImpl(driver)


ComponentRepoDep = Annotated[
    IComponentRepository,
    IMatrixRepository,
    IRoleRepository,
    IExecutionPersonaRepository,
    IExtractionProtocolRepository,
    Depends(get_component_repo),
]


async def get_prompt_block_repo(driver: DriverDep) -> IPromptBlockRepository:
    return PromptBlockRepositoryImpl(driver)


PromptBlockRepoDep = Annotated[IPromptBlockRepository, Depends(get_prompt_block_repo)]


async def get_agent_repo(driver: DriverDep) -> IAgentRepository:
    return AgentRepositoryImpl(driver)


AgentRepoDep = Annotated[IAgentRepository, Depends(get_agent_repo)]


async def get_task_blueprint_repo(driver: DriverDep) -> ITaskBlueprintRepository:
    return TaskBlueprintRepositoryImpl(driver)


TaskBlueprintRepoDep = Annotated[ITaskBlueprintRepository, Depends(get_task_blueprint_repo)]


async def get_output_profile_repo(driver: DriverDep) -> IOutputProfileRepository:
    return OutputProfileRepositoryImpl(driver)


OutputProfileRepoDep = Annotated[IOutputProfileRepository, Depends(get_output_profile_repo)]


async def get_knowledge_repo(driver: DriverDep) -> IKnowledgeRepository:
    """Instantiate the knowledge repository.

    Args:
        driver: Storage driver.

    Returns:
        Knowledge repository instance.
    """
    return KnowledgeRepositoryImpl(driver)


KnowledgeRepoDep = Annotated[IKnowledgeRepository, Depends(get_knowledge_repo)]


async def get_system_repo(driver: DriverDep) -> ISystemRepository:
    """Instantiate the system repository.

    Args:
        driver: Storage driver.

    Returns:
        System repository instance.
    """
    return SystemRepositoryImpl(driver)


SystemRepoDep = Annotated[ISystemRepository, Depends(get_system_repo)]


async def get_audit_repo(driver: DriverDep) -> IAuditRepository:
    """Instantiate the audit repository.

    Args:
        driver: Storage driver.

    Returns:
        Audit repository instance.
    """
    return AuditRepositoryImpl(driver)


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


def get_auth_service(
    repo: IdentityRepoDep,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthService:
    """Instantiate the authentication service.

    Args:
        repo: Identity repository.
        settings: Application settings.

    Returns:
        Auth service instance.
    """
    return AuthService(repo=repo, use_firebase=settings.use_firebase_auth)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user_from_header(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[HTTPAuthorizationCredentials | None, Security(security)] = None,
) -> TokenData:
    """Extract and verify the current user from the authorization header.

    Args:
        auth_service: Authentication service.
        token: HTTP bearer token.

    Returns:
        Verified token data.

    Raises:
        AuthenticationError: If the token is missing or invalid.
    """
    if not token:
        msg = "Missing authentication token"
        error_code = "AUTH_TOKEN_MISSING"
        logger.error("[Dependencies] %s", msg, extra={"error_code": error_code})
        raise AuthenticationError(message=msg, details={"error_code": error_code})
    return await auth_service.verify_token(token.credentials)


UserDep = Annotated[TokenData, Depends(get_current_user_from_header)]
CurrentUserDep = UserDep


def require_role(required_role: UserRole) -> Any:
    """Returns a dependency that validates the user has the required role.

    Implicitly allows ROOT for everything.

    Args:
        required_role: The minimum user role required.

    Returns:
        A FastAPI dependency checker function.
    """

    async def _role_checker(user: TokenData = Depends(get_current_user_from_header)) -> TokenData:
        if user.role == UserRole.ROOT:
            return user
        if user.role != required_role:
            raise PermissionDeniedError(
                message=f"Insufficient privileges. Required: {required_role.value}",
                details={"required_role": required_role.value, "current_role": user.role.value},
            )
        return user

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
    component_repo: ComponentRepoDep,
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
        component_repo: Component repository.
        identity_repo: Identity repository.
        audit_repo: Audit repository.
        system_repo: System repository.
        prompt_compiler: Prompt compiler.

    Returns:
        DAG executor instance.
    """
    return DAGExecutor(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=component_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        identity_repo=identity_repo,
        audit_repo=audit_repo,
        system_repo=system_repo,
        prompt_compiler=prompt_compiler,
    )


ExecutorDep = Annotated[DAGExecutor, Depends(get_dag_executor)]


async def get_execution_service(
    exec_repo: ExecutionRepoDep,
    workflow_repo: WorkflowRepoDep,
    comp_repo: ComponentRepoDep,
    identity_repo: IdentityRepoDep,
    system_repo: SystemRepoDep,
    usage_service: UsageServiceDep,
    executor: Annotated[DAGExecutor, Depends(get_dag_executor)],
    prompt_block_repo: PromptBlockRepoDep,
    output_profile_repo: OutputProfileRepoDep,
) -> ExecutionService:
    """Instantiate the high-level execution service.

    Args:
        exec_repo: Execution repository.
        workflow_repo: Workflow repository.
        comp_repo: Component repository.
        identity_repo: Identity repository.
        system_repo: System repository.
        usage_service: Usage service.
        executor: DAG executor.

    Returns:
        Execution service instance.
    """
    return ExecutionService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=comp_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=output_profile_repo,
        identity_repo=identity_repo,
        system_repo=system_repo,
        usage_service=usage_service,
        executor=executor,
    )


ExecutionServiceDep = Annotated[ExecutionService, Depends(get_execution_service)]


async def get_studio_workflow_service(
    workflow_repo: WorkflowRepoDep,
    output_profile_repo: OutputProfileRepoDep,
    prompt_block_repo: PromptBlockRepoDep,
) -> StudioWorkflowService:
    """Instantiate the studio workflow service.

    Args:
        workflow_repo: Workflow repository.
        output_profile_repo: Output profile repository.
        prompt_block_repo: Prompt block repository.

    Returns:
        Studio workflow service instance.
    """
    return StudioWorkflowService(
        workflow_repo=workflow_repo,
        output_profile_repo=output_profile_repo,
        prompt_block_repo=prompt_block_repo,
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


async def get_studio_lexicon_service(
    system_repo: SystemRepoDep,
) -> StudioLexiconService:
    """Instantiate the studio lexicon service.

    Args:
        system_repo: System repository.

    Returns:
        Studio lexicon service instance.
    """
    return StudioLexiconService(system_repo=system_repo)


StudioLexiconServiceDep = Annotated[StudioLexiconService, Depends(get_studio_lexicon_service)]


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


def get_llm_handler(repo: ComponentRepoDep) -> LLMHandler:
    """Instantiate the direct LLM handler.

    Args:
        repo: Component repository.

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
