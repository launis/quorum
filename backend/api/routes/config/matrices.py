"""API Router for Evaluation Matrices."""

import logging

from fastapi import APIRouter, Path
from pydantic import TypeAdapter

from backend.dependencies import RepositoryDep
from backend.models.dtos.config import ComponentUpdate, MatrixComponentResponse

logger = logging.getLogger(__name__)

# Adapter for strict Matrix model
_matrix_adapter: TypeAdapter[MatrixComponentResponse] = TypeAdapter(MatrixComponentResponse)

router = APIRouter(tags=["Configuration - Matrices"])


@router.get(
    "",
    summary="List Matrices",
    response_description="All evaluation matrices.",
    response_model=list[MatrixComponentResponse],
)
async def get_matrices(repo: RepositoryDep) -> list[MatrixComponentResponse]:
    """Retrieves all defined evaluation matrices.

    Args:
        repo: Repository dependency.

    Returns:
        List of matrix components.

    Raises:
        AppException: If retrieval fails.
    """
    try:
        raw_components = await repo.get_all_matrices()
        return [_matrix_adapter.validate_python(c) for c in raw_components]
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "MATRICES_LIST_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e


@router.get(
    "/{matrix_id}",
    summary="Get Matrix",
    response_description="The requested matrix.",
    response_model=MatrixComponentResponse,
)
async def get_matrix(
    repo: RepositoryDep, matrix_id: str = Path(..., description="Matrix ID")
) -> MatrixComponentResponse:
    """Retrieves a single evaluation matrix by ID.

    Args:
        repo: Repository dependency.
        matrix_id: Unique identifier for the matrix.

    Returns:
        The matched matrix component.

    Raises:
        ResourceNotFoundError: If the matrix does not exist.
    """
    res = await repo.get_matrix_by_id(matrix_id)

    if not res:
        from backend.exceptions import ResourceNotFoundError

        error_code = "MATRIX_NOT_FOUND"
        logger.error(f"{error_code}: ID {matrix_id}", exc_info=True)
        raise ResourceNotFoundError("Matrix", matrix_id, details={"error_code": error_code})

    # Normalize 'class' key for DTO if needed
    if "class" in res:
        res["component_class"] = res["class"]

    return _matrix_adapter.validate_python(res)


@router.post(
    "", summary="Create Matrix", response_description="Created explicit string ID.", response_model=str
)
async def create_matrix(matrix: MatrixComponentResponse, repo: RepositoryDep) -> str:
    """Creates a new evaluation matrix."""
    try:
        existing = await repo.get_matrix_by_id(matrix.id)
        if existing:
            from backend.exceptions import ConflictError
            error_code = "MATRIX_ID_EXISTS"
            logger.error(f"{error_code}: ID {matrix.id}", exc_info=True)
            raise ConflictError(message="Resource conflict", details={"error_code": error_code})

        new_matrix = matrix.model_dump()
        if "component_class" in new_matrix:
            new_matrix["class"] = new_matrix.pop("component_class")

        await repo.create_matrix(new_matrix)
        return matrix.id
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "MATRIX_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e

@router.put(
    "/{matrix_id}", summary="Update Matrix", response_description="Update status"
)
async def update_matrix(matrix_id: str, updates: ComponentUpdate, repo: RepositoryDep) -> bool:
    """Updates an existing evaluation matrix."""
    try:
        current_data = await repo.get_matrix_by_id(matrix_id)
        if not current_data:
            from backend.exceptions import ResourceNotFoundError
            error_code = "MATRIX_NOT_FOUND"
            logger.error(f"{error_code}: ID {matrix_id}", exc_info=True)
            raise ResourceNotFoundError("Matrix", matrix_id, details={"error_code": error_code})

        update_data = {}
        if updates.content is not None:
            update_data["content"] = updates.content
        if updates.description:
            update_data["description"] = updates.description
        if updates.citation:
            update_data["citation"] = updates.citation
        if updates.citation_full:
            update_data["citation_full"] = updates.citation_full
        if updates.type:
            update_data["type"] = updates.type

        return await repo.update_matrix(matrix_id, update_data)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "MATRIX_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e

@router.delete(
    "/{matrix_id}", summary="Delete Matrix", response_description="Delete status"
)
async def delete_matrix(matrix_id: str, repo: RepositoryDep) -> bool:
    """Deletes an evaluation matrix."""
    try:
        existing = await repo.get_matrix_by_id(matrix_id)
        if not existing:
            from backend.exceptions import ResourceNotFoundError
            error_code = "MATRIX_NOT_FOUND"
            logger.error(f"{error_code}: ID {matrix_id}", exc_info=True)
            raise ResourceNotFoundError("Matrix", matrix_id, details={"error_code": error_code})

        return await repo.delete_matrix(matrix_id)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        error_code = "MATRIX_DELETE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e
