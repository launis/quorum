import logging
from typing import Annotated

from fastapi import APIRouter
from pydantic import BaseModel, Field
from tinydb import Query

from backend.dependencies import DatabaseDep, RepositoryDep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["Configuration"])


class DimensionDefinition(BaseModel):
    """Model definition for an evaluation dimension."""

    id: Annotated[str, Field(description="Unique dimension ID (e.g. 'analyysi').")]
    label: Annotated[str, Field(description="Human readable default label.")]
    description: Annotated[str | None, Field(description="Explanation of what this measures.")] = None
    is_system: Annotated[bool, Field(description="If true, is a core system dimension.")] = False


@router.get(
    "/ontology/dimensions",
    summary="Get Known Dimensions",
    response_description="List of unique evaluation dimension IDs.",
)
def get_known_dimensions(db: DatabaseDep):
    """Returns specific allowed dimension IDs from the ontology table.

    Auto-seeds defaults if table is empty.

    Args:
        db (DatabaseDep): Database dependency.

    Returns:
        list[dict]: Sorted list of dimensions.
    """
    table = db.table("dimensions")
    all_dims = table.all()

    return sorted(all_dims, key=lambda x: x["id"])


@router.delete("/ontology/dimensions/{dim_id}", summary="Delete Dimension", response_description="Delete status.")
async def delete_dimension(
    dim_id: str,
    db: DatabaseDep,
    repo: RepositoryDep,
):
    """Deletes a dimension if it is not used in any matrix."""
    # 1. Existence Check
    table = db.table("dimensions")
    Dim = Query()

    if not table.contains(Dim.id == dim_id):
        from backend.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("Dimension", dim_id, details={"error_code": "DIMENSION_NOT_FOUND"})

    # 2. Check Usage in Matrices (via Repo)
    used_in_components = await repo.get_components_using_dimension(dim_id)

    if used_in_components:
        from backend.exceptions import ConflictError

        error_code = "Errors.DeleteBlockedByMatrix"

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
        logger.warning(f"{error_code}: {msg}")

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
    return {"status": "deleted", "id": dim_id}


@router.put("/ontology/dimensions/{dim_id}", summary="Update Dimension", response_description="Updated dimension.")
async def update_dimension(
    dim_id: str,
    dimension: DimensionDefinition,
    db: DatabaseDep,
    repo: RepositoryDep,
):
    """Updates an existing dimension."""
    from backend.exceptions import AppError, ResourceNotFoundError

    if dim_id != dimension.id:
        raise AppError(
            "Dimension ID mismatch.",
            details={"error_code": "DIMENSION_ID_MISMATCH"}
        )

    # 1. Existence Check
    table = db.table("dimensions")
    Dim = Query()

    if not table.contains(Dim.id == dim_id):
        raise ResourceNotFoundError("Dimension", dim_id, details={"error_code": "DIMENSION_NOT_FOUND"})

    # 2. Update
    table.update(dimension.model_dump(), Dim.id == dim_id)
    return dimension
