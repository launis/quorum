import logging
from typing import Annotated

from fastapi import APIRouter
from pydantic import BaseModel, Field
from tinydb import Query

from backend.dependencies import DatabaseDep, RepositoryDep

from backend.exceptions import AppException, ResourceNotFoundError, ErrorCodes, ConflictError
from backend.models.dtos.config import DimensionDefinition, DimensionDeleteResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Ontology"])

@router.get(
    "/dimensions",
    summary="Get Known Dimensions",
    response_description="List of unique evaluation dimension IDs.",
    response_model=list[DimensionDefinition],
)
def get_known_dimensions(db: DatabaseDep) -> list[DimensionDefinition]:
    """Returns specific allowed dimension IDs from the ontology table.

    Auto-seeds defaults if table is empty.

    Args:
        db (DatabaseDep): Database dependency.

    Returns:
        list[DimensionDefinition]: Sorted list of dimensions.
    """
    try:
        table = db.table("dimensions")
        all_dims = table.all()

        return sorted([DimensionDefinition(**d) for d in all_dims], key=lambda x: x.id)
    except Exception as e:
        error_code = ErrorCodes.DIMENSION_LIST_FAILED
        logger.error(f"[Config] {error_code.value}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=500,
            details={"error_code": error_code}
        ) from e


@router.delete("/dimensions/{dim_id}", summary="Delete Dimension", response_description="Delete status.", response_model=DimensionDeleteResponse)
async def delete_dimension(
    dim_id: str,
    db: DatabaseDep,
    repo: RepositoryDep,
) -> DimensionDeleteResponse:
    """Deletes a dimension if it is not used in any matrix."""
    try:
        # 1. Existence Check
        table = db.table("dimensions")
        Dim = Query()

        if not table.contains(Dim.id == dim_id):
            raise ResourceNotFoundError("Dimension", dim_id, details={"error_code": ErrorCodes.DIMENSION_NOT_FOUND})

        # 2. Check Usage in Matrices (via Repo)
        used_in_components = await repo.get_components_using_dimension(dim_id)

        if used_in_components:
            error_code = ErrorCodes.DELETE_BLOCKED_BY_USAGE

            # Verify and fetch name of the first matrix
            matrix_id = used_in_components[0]
            matrix_name = "Unknown Matrix"

            comp_res = db.table("components").search(Query().id == matrix_id)
            if comp_res:
                matrix_name = comp_res[0].get("name", matrix_id)

            msg = (
                f"Dimension '{dim_id}' is used in matrix '{matrix_name}'. "
                "Remove it from the matrix first."
            )
            logger.warning(f"[Config] {error_code.value}: {msg}")

            raise ConflictError(
                message=msg,
                details={
                    "error_code": error_code,
                    "id": dim_id,
                    "name": matrix_name
                }
            )

        # 3. Delete
        table.remove(Dim.id == dim_id)
        return DimensionDeleteResponse(status="deleted", id=dim_id)

    except Exception as e:
        if isinstance(e, AppException):
             raise e
        
        error_code = ErrorCodes.DIMENSION_DELETE_FAILED
        logger.error(f"[Config] {error_code.value}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=500,
            details={"error_code": error_code}
        ) from e


@router.put("/dimensions/{dim_id}", summary="Update Dimension", response_description="Updated dimension.", response_model=DimensionDefinition)
async def update_dimension(
    dim_id: str,
    dimension: DimensionDefinition,
    db: DatabaseDep,
    repo: RepositoryDep,
) -> DimensionDefinition:
    """Updates an existing dimension."""
    try:
        if dim_id != dimension.id:
            raise AppException(
                message="Dimension ID mismatch.",
                status_code=400,
                details={"error_code": ErrorCodes.DIMENSION_ID_MISMATCH}
            )

        # 1. Existence Check
        table = db.table("dimensions")
        Dim = Query()

        if not table.contains(Dim.id == dim_id):
            raise ResourceNotFoundError("Dimension", dim_id, details={"error_code": ErrorCodes.DIMENSION_NOT_FOUND})

        # 2. Update
        table.update(dimension.model_dump(), Dim.id == dim_id)
        return dimension

    except Exception as e:
        if isinstance(e, AppException):
             raise e
        
        error_code = ErrorCodes.DIMENSION_UPDATE_FAILED
        logger.error(f"[Config] {error_code.value}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=500,
            details={"error_code": error_code}
        ) from e
