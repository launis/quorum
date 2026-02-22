"""API Router for AI Agents."""

import logging

from fastapi import APIRouter, Path
from pydantic import TypeAdapter

from backend.dependencies import RepositoryDep
from backend.models.dtos.config import AgentComponentResponse, ComponentUpdate

logger = logging.getLogger(__name__)

# Adapter for strict Agent model
_agent_adapter: TypeAdapter[AgentComponentResponse] = TypeAdapter(AgentComponentResponse)

router = APIRouter(tags=["Configuration - Agents"])


@router.get(
    "",
    summary="List Agents",
    response_description="All AI agent definitions.",
    response_model=list[AgentComponentResponse],
)
async def get_agents(repo: RepositoryDep) -> list[AgentComponentResponse]:
    """Retrieves all defined AI agents.

    Args:
        repo: Repository dependency.

    Returns:
        List of agent components.

    Raises:
        AppException: If retrieval fails.
    """
    try:
        raw_components = await repo.get_all_agents()
        return [_agent_adapter.validate_python(c) for c in raw_components]
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "AGENTS_LIST_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e


@router.get(
    "/{agent_id}",
    summary="Get Agent",
    response_description="The requested agent.",
    response_model=AgentComponentResponse,
)
async def get_agent(
    repo: RepositoryDep, agent_id: str = Path(..., description="Agent ID")
) -> AgentComponentResponse:
    """Retrieves a single AI agent by ID.

    Args:
        repo: Repository dependency.
        agent_id: Unique identifier for the agent.

    Returns:
        The matched agent component.
        
    Raises:
        ResourceNotFoundError: If the agent does not exist.
    """
    res = await repo.get_agent_by_id(agent_id)

    if not res:
        from backend.exceptions import ResourceNotFoundError

        error_code = "AGENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {agent_id}", exc_info=True)
        raise ResourceNotFoundError("Agent", agent_id, details={"error_code": error_code})

    # Normalize 'class' key for DTO if needed
    if "class" in res:
        res["component_class"] = res["class"]

    return _agent_adapter.validate_python(res)


@router.post(
    "", summary="Create Agent", response_description="Created explicit string ID.", response_model=str
)
async def create_agent(agent: AgentComponentResponse, repo: RepositoryDep) -> str:
    """Creates a new AI agent."""
    try:
        existing = await repo.get_agent_by_id(agent.id)
        if existing:
            from backend.exceptions import ConflictError
            error_code = "AGENT_ID_EXISTS"
            logger.error(f"{error_code}: ID {agent.id}", exc_info=True)
            raise ConflictError(message="Resource conflict", details={"error_code": error_code})

        new_agent = agent.model_dump()
        if "component_class" in new_agent:
            new_agent["class"] = new_agent.pop("component_class")

        await repo.create_agent(new_agent)
        return agent.id
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "AGENT_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e

@router.put(
    "/{agent_id}", summary="Update Agent", response_description="Update status"
)
async def update_agent(agent_id: str, updates: ComponentUpdate, repo: RepositoryDep) -> bool:
    """Updates an existing AI agent."""
    try:
        current_data = await repo.get_agent_by_id(agent_id)
        if not current_data:
            from backend.exceptions import ResourceNotFoundError
            error_code = "AGENT_NOT_FOUND"
            logger.error(f"{error_code}: ID {agent_id}", exc_info=True)
            raise ResourceNotFoundError("Agent", agent_id, details={"error_code": error_code})

        update_data = {}
        if updates.content is not None:
            update_data["content"] = updates.content
        if updates.description:
            update_data["description"] = updates.description
        if updates.citation:
            update_data["citation"] = updates.citation
        if updates.citation_full:
            update_data["citation_full"] = updates.citation_full

        return await repo.update_agent(agent_id, update_data)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "AGENT_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e

@router.delete(
    "/{agent_id}", summary="Delete Agent", response_description="Delete status"
)
async def delete_agent(agent_id: str, repo: RepositoryDep) -> bool:
    """Deletes an AI agent."""
    try:
        existing = await repo.get_agent_by_id(agent_id)
        if not existing:
            from backend.exceptions import ResourceNotFoundError
            error_code = "AGENT_NOT_FOUND"
            logger.error(f"{error_code}: ID {agent_id}", exc_info=True)
            raise ResourceNotFoundError("Agent", agent_id, details={"error_code": error_code})

        return await repo.delete_agent(agent_id)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "AGENT_DELETE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e
