import logging
from typing import TYPE_CHECKING, Annotated, Any

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass

from arq.connections import ArqRedis
from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend_v2.database.factory import get_repository
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.auth import AuthService
from backend_v2.services.execution import ExecutionService
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.studio import StudioService
from backend_v2.settings import Settings, get_settings

security = HTTPBearer(auto_error=False)


async def get_repo(settings: Annotated[Settings, Depends(get_settings)]) -> AbstractWorkflowRepository:
    repo = await get_repository(settings)
    return repo


RepoDep = Annotated[AbstractWorkflowRepository, Depends(get_repo)]


def get_auth_service(
    repo: AbstractWorkflowRepository = Depends(get_repo),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(repo=repo, use_firebase=getattr(settings, "USE_FIREBASE_AUTH", False))


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

from backend_v2.exceptions import AuthenticationError


async def get_current_user_from_header(
    auth_service: AuthService = Depends(get_auth_service),
    token: HTTPAuthorizationCredentials | None = Security(security),
) -> TokenData:
    if not token:
        msg = "Missing authentication token"
        error_code = "AUTH_TOKEN_MISSING"
        logger.error(f"[Dependencies] {error_code}: {msg}")
        raise AuthenticationError(message=msg, details={"error_code": error_code})
    return await auth_service.verify_token(token.credentials)


UserDep = Annotated[TokenData, Depends(get_current_user_from_header)]
CurrentUserDep = UserDep
RepositoryDep = RepoDep


def get_current_admin_user() -> Any:
    return AuthService.require_role(UserRole.ADMIN)()


async def get_dag_executor(repo: AbstractWorkflowRepository = Depends(get_repo)) -> DAGExecutor:
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

    compiler = PromptCompiler()
    return DAGExecutor(repo, compiler)


ExecutorDep = Annotated[DAGExecutor, Depends(get_dag_executor)]


async def get_execution_service(
    repo: AbstractWorkflowRepository = Depends(get_repo), executor: DAGExecutor = Depends(get_dag_executor)
) -> ExecutionService:
    return ExecutionService(repo=repo, executor=executor)


ExecutionServiceDep = Annotated[ExecutionService, Depends(get_execution_service)]


async def get_studio_service(repo: AbstractWorkflowRepository = Depends(get_repo)) -> StudioService:
    return StudioService(repo=repo)


StudioServiceDep = Annotated[StudioService, Depends(get_studio_service)]


def get_llm_handler(repo: AbstractWorkflowRepository = Depends(get_repo)) -> Any:
    from backend_v2.llm.handler import LLMHandler

    return LLMHandler(repo=repo)


LLMHandlerDep = Annotated[Any, Depends(get_llm_handler)]

from typing import cast


def get_arq_pool(request: Request) -> ArqRedis:
    return cast(ArqRedis, request.app.state.arq_pool)


ArqPoolDep = Annotated[ArqRedis, Depends(get_arq_pool)]
