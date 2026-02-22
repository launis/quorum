"""API Router for Evaluation Dimensions."""

import logging

from fastapi import APIRouter, Path
from pydantic import TypeAdapter

from backend.dependencies import RepositoryDep
from backend.models.dtos.config import ComponentUpdate, DimensionDefinition

logger = logging.getLogger(__name__)

# Adapter for strict Dimension model
_dimension_adapter: TypeAdapter[DimensionDefinition] = TypeAdapter(DimensionDefinition)

router = APIRouter(tags=["Configuration - Dimensions"])


@router.get(
    "",
    summary="List Dimensions",
    response_description="All evaluation dimensions.",
    response_model=list[DimensionDefinition],
)
async def get_dimensions(repo: RepositoryDep) -> list[DimensionDefinition]:
    """Retrieves all defined evaluation dimensions.

    Args:
        repo: Repository dependency.

    Returns:
        List of dimension components.

    Raises:
        AppException: If retrieval fails.
    """
    try:
        raw_components = await repo.get_all_dimensions()
        return [_dimension_adapter.validate_python(c) for c in raw_components]
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "DIMENSIONS_LIST_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e


@router.get(
    "/{dimension_id}",
    summary="Get Dimension",
    response_description="The requested dimension.",
    response_model=DimensionDefinition,
)
async def get_dimension(
    repo: RepositoryDep, dimension_id: str = Path(..., description="Dimension ID")
) -> DimensionDefinition:
    """Retrieves a single evaluation dimension by ID.

    Args:
        repo: Repository dependency.
        dimension_id: Unique identifier for the dimension.

    Returns:
        The matched dimension component.

    Raises:
        ResourceNotFoundError: If the dimension does not exist.
    """
    res = await repo.get_dimension_by_id(dimension_id)

    if not res:
        from backend.exceptions import ResourceNotFoundError

        error_code = "DIMENSION_NOT_FOUND"
        logger.error(f"{error_code}: ID {dimension_id}", exc_info=True)
        raise ResourceNotFoundError("Dimension", dimension_id, details={"error_code": error_code})

    return _dimension_adapter.validate_python(res)


@router.post(
    "", summary="Create Dimension", response_description="Created explicit string ID.", response_model=str
)
async def create_dimension(dimension: DimensionDefinition, repo: RepositoryDep) -> str:
    """Creates a new evaluation dimension."""
    try:
        existing = await repo.get_dimension_by_id(dimension.id)
        if existing:
            from backend.exceptions import ConflictError
            error_code = "DIMENSION_ID_EXISTS"
            logger.error(f"{error_code}: ID {dimension.id}", exc_info=True)
            raise ConflictError(message="Resource conflict", details={"error_code": error_code})

        new_dimension = dimension.model_dump()
        if "component_class" in new_dimension:
            new_dimension["class"] = new_dimension.pop("component_class")

        await repo.create_dimension(new_dimension)
        return dimension.id
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "DIMENSION_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e

@router.put(
    "/{dimension_id}", summary="Update Dimension", response_description="Update status"
)
async def update_dimension(dimension_id: str, updates: ComponentUpdate, repo: RepositoryDep) -> bool:
    """Updates an existing evaluation dimension."""
    try:
        current_data = await repo.get_dimension_by_id(dimension_id)
        if not current_data:
            from backend.exceptions import ResourceNotFoundError
            error_code = "DIMENSION_NOT_FOUND"
            logger.error(f"{error_code}: ID {dimension_id}", exc_info=True)
            raise ResourceNotFoundError("Dimension", dimension_id, details={"error_code": error_code})

        update_data = {}
        if updates.content is not None:
            update_data["content"] = updates.content
        if updates.description:
            update_data["description"] = updates.description
        if updates.citation:
            update_data["citation"] = updates.citation
        if updates.citation_full:
            update_data["citation_full"] = updates.citation_full

        return await repo.update_dimension(dimension_id, update_data)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "DIMENSION_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e

@router.delete(
    "/{dimension_id}", summary="Delete Dimension", response_description="Delete status"
)
async def delete_dimension(dimension_id: str, repo: RepositoryDep) -> bool:
    """Deletes an evaluation dimension."""
    try:
        existing = await repo.get_dimension_by_id(dimension_id)
        if not existing:
            from backend.exceptions import ResourceNotFoundError
            error_code = "DIMENSION_NOT_FOUND"
            logger.error(f"{error_code}: ID {dimension_id}", exc_info=True)
            raise ResourceNotFoundError("Dimension", dimension_id, details={"error_code": error_code})

        return await repo.delete_dimension(dimension_id)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "DIMENSION_DELETE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e
