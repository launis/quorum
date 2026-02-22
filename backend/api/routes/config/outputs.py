"""API Router for Output Configurations."""

import logging

from fastapi import APIRouter, Path
from pydantic import TypeAdapter

from backend.dependencies import RepositoryDep
from backend.models.dtos.config import ComponentUpdate, ConfigComponentResponse

logger = logging.getLogger(__name__)

# Adapter for strict Output Config model
_output_adapter: TypeAdapter[ConfigComponentResponse] = TypeAdapter(ConfigComponentResponse)

router = APIRouter(tags=["Configuration - Outputs"])


@router.get(
    "",
    summary="List Output Configurations",
    response_description="All output configurations.",
    response_model=list[ConfigComponentResponse],
)
async def get_outputs(repo: RepositoryDep) -> list[ConfigComponentResponse]:
    """Retrieves all defined output configurations.

    Args:
        repo: Repository dependency.

    Returns:
        List of output config components.

    Raises:
        AppException: If retrieval fails.
    """
    try:
        raw_components = await repo.get_all_output_configs()
        return [_output_adapter.validate_python(c) for c in raw_components]
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "OUTPUTS_LIST_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e


@router.get(
    "/{output_id}",
    summary="Get Output Configuration",
    response_description="The requested output config.",
    response_model=ConfigComponentResponse,
)
async def get_output(
    repo: RepositoryDep, output_id: str = Path(..., description="Output ID")
) -> ConfigComponentResponse:
    """Retrieves a single output configuration by ID.

    Args:
        repo: Repository dependency.
        output_id: Unique identifier for the output config.

    Returns:
        The matched config component.

    Raises:
        ResourceNotFoundError: If the config does not exist.
    """
    res = await repo.get_output_config_by_id(output_id)

    if not res:
        from backend.exceptions import ResourceNotFoundError

        error_code = "OUTPUT_NOT_FOUND"
        logger.error(f"{error_code}: ID {output_id}", exc_info=True)
        raise ResourceNotFoundError("Output Config", output_id, details={"error_code": error_code})

    return _output_adapter.validate_python(res)


@router.post(
    "", summary="Create Output Config", response_description="Created explicit string ID.", response_model=str
)
async def create_output(output: ConfigComponentResponse, repo: RepositoryDep) -> str:
    """Creates a new output configuration."""
    try:
        existing = await repo.get_output_config_by_id(output.id)
        if existing:
            from backend.exceptions import ConflictError
            error_code = "OUTPUT_ID_EXISTS"
            logger.error(f"{error_code}: ID {output.id}", exc_info=True)
            raise ConflictError(message="Resource conflict", details={"error_code": error_code})

        new_output = output.model_dump()
        if "component_class" in new_output:
            new_output["class"] = new_output.pop("component_class")

        await repo.create_output_config(new_output)
        return output.id
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "OUTPUT_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e

@router.put(
    "/{output_id}", summary="Update Output Config", response_description="Update status"
)
async def update_output(output_id: str, updates: ComponentUpdate, repo: RepositoryDep) -> bool:
    """Updates an existing output configuration."""
    try:
        current_data = await repo.get_output_config_by_id(output_id)
        if not current_data:
            from backend.exceptions import ResourceNotFoundError
            error_code = "OUTPUT_NOT_FOUND"
            logger.error(f"{error_code}: ID {output_id}", exc_info=True)
            raise ResourceNotFoundError("Output Config", output_id, details={"error_code": error_code})

        update_data = {}
        if updates.content is not None:
            update_data["content"] = updates.content
        if updates.description:
            update_data["description"] = updates.description
        if updates.citation:
            update_data["citation"] = updates.citation
        if updates.citation_full:
            update_data["citation_full"] = updates.citation_full

        return await repo.update_output_config(output_id, update_data)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "OUTPUT_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e

@router.delete(
    "/{output_id}", summary="Delete Output Config", response_description="Delete status"
)
async def delete_output(output_id: str, repo: RepositoryDep) -> bool:
    """Deletes an output configuration."""
    try:
        existing = await repo.get_output_config_by_id(output_id)
        if not existing:
            from backend.exceptions import ResourceNotFoundError
            error_code = "OUTPUT_NOT_FOUND"
            logger.error(f"{error_code}: ID {output_id}", exc_info=True)
            raise ResourceNotFoundError("Output Config", output_id, details={"error_code": error_code})

        return await repo.delete_output_config(output_id)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "OUTPUT_DELETE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e
