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
    IAuditRepository,
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IKnowledgeRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.database.repositories.component import ComponentRepositoryImpl
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.database.repositories.knowledge import KnowledgeRepositoryImpl
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import AuthenticationError
from backend_v2.llm.handler import LLMHandler
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.auth import AuthService
from backend_v2.services.document_extraction import DocumentExtractionService
from backend_v2.services.execution import ExecutionService
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.studio import StudioService
from backend_v2.services.usage_service import UsageService
from backend_v2.settings import Settings, get_settings

security = HTTPBearer(auto_error=False)


async def get_db_driver(settings: Annotated[Settings, Depends(get_settings)]) -> StorageDriver:
    return await get_driver(settings)


DriverDep = Annotated[StorageDriver, Depends(get_db_driver)]


async def get_execution_repo(driver: DriverDep) -> IExecutionRepository:
    return ExecutionRepositoryImpl(driver)


ExecutionRepoDep = Annotated[IExecutionRepository, Depends(get_execution_repo)]


async def get_identity_repo(driver: DriverDep) -> IIdentityRepository:
    return IdentityRepositoryImpl(driver)


IdentityRepoDep = Annotated[IIdentityRepository, Depends(get_identity_repo)]


async def get_workflow_repo(driver: DriverDep) -> IWorkflowRepository:
    return WorkflowRepositoryImpl(driver)


WorkflowRepoDep = Annotated[IWorkflowRepository, Depends(get_workflow_repo)]


async def get_component_repo(driver: DriverDep) -> IComponentRepository:
    return ComponentRepositoryImpl(driver)


ComponentRepoDep = Annotated[IComponentRepository, Depends(get_component_repo)]


async def get_knowledge_repo(driver: DriverDep) -> IKnowledgeRepository:
    return KnowledgeRepositoryImpl(driver)


KnowledgeRepoDep = Annotated[IKnowledgeRepository, Depends(get_knowledge_repo)]


async def get_system_repo(driver: DriverDep) -> ISystemRepository:
    return SystemRepositoryImpl(driver)


SystemRepoDep = Annotated[ISystemRepository, Depends(get_system_repo)]


async def get_audit_repo(driver: DriverDep) -> IAuditRepository:
    return AuditRepositoryImpl(driver)


AuditRepoDep = Annotated[IAuditRepository, Depends(get_audit_repo)]


def get_usage_service(identity_repo: IdentityRepoDep, audit_repo: AuditRepoDep) -> UsageService:
    return UsageService(identity_repo=identity_repo, audit_repo=audit_repo)


UsageServiceDep = Annotated[UsageService, Depends(get_usage_service)]


def get_auth_service(
    repo: IdentityRepoDep,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthService:
    return AuthService(repo=repo, use_firebase=settings.use_firebase_auth)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user_from_header(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: Annotated[HTTPAuthorizationCredentials | None, Security(security)] = None,
) -> TokenData:
    if not token:
        msg = "Missing authentication token"
        error_code = "AUTH_TOKEN_MISSING"
        logger.error("[Dependencies] %s", msg, extra={"error_code": error_code})
        raise AuthenticationError(message=msg, details={"error_code": error_code})
    return await auth_service.verify_token(token.credentials)


UserDep = Annotated[TokenData, Depends(get_current_user_from_header)]
CurrentUserDep = UserDep


def get_current_admin_user() -> Any:
    return AuthService.require_role(UserRole.ADMIN)()


def get_prompt_compiler() -> PromptCompiler:
    return PromptCompiler()


PromptCompilerDep = Annotated[PromptCompiler, Depends(get_prompt_compiler)]


def get_llm_task_executor(compiler: PromptCompilerDep) -> LLMTaskExecutor:
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
) -> DAGExecutor:
    return DAGExecutor(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=component_repo,
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
    usage_service: UsageServiceDep,
    executor: Annotated[DAGExecutor, Depends(get_dag_executor)],
) -> ExecutionService:
    return ExecutionService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        comp_repo=comp_repo,
        identity_repo=identity_repo,
        usage_service=usage_service,
        executor=executor,
    )


ExecutionServiceDep = Annotated[ExecutionService, Depends(get_execution_service)]


async def get_studio_service(
    workflow_repo: WorkflowRepoDep,
    component_repo: ComponentRepoDep,
    knowledge_repo: KnowledgeRepoDep,
    system_repo: SystemRepoDep,
) -> StudioService:
    return StudioService(
        workflow_repo=workflow_repo,
        component_repo=component_repo,
        knowledge_repo=knowledge_repo,
        system_repo=system_repo,
    )


StudioServiceDep = Annotated[StudioService, Depends(get_studio_service)]


def get_llm_handler(repo: ComponentRepoDep) -> LLMHandler:
    return LLMHandler(repo=repo)


LLMHandlerDep = Annotated[LLMHandler, Depends(get_llm_handler)]


def get_arq_pool(request: Request) -> ArqRedis:
    return cast(ArqRedis, request.app.state.arq_pool)


ArqPoolDep = Annotated[ArqRedis, Depends(get_arq_pool)]


def get_document_extraction_service() -> DocumentExtractionService:
    return DocumentExtractionService()


DocumentExtractionServiceDep = Annotated[DocumentExtractionService, Depends(get_document_extraction_service)]
