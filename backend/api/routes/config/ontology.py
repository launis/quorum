import logging
from typing import Annotated

from fastapi import APIRouter, Depends
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
        list[str]: Sorted list of dimension IDs.
    """
    import logging


    logger = logging.getLogger(__name__)
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

        error_code = "DIMENSION_IN_USE_BY_MATRIX"
        # Truncate list if too long for UI message
        display_list = used_in_components[:3]
        if len(used_in_components) > 3:
            display_list.append("...")

        msg = f"Dimension '{dim_id}' is used in matrices: {', '.join(display_list)}"
        logger.warning(f"{error_code}: {msg}")

        raise ConflictError(
            message=msg,
            details={
                "error_code": error_code,
                "matrices": used_in_components # Send full list in details for UI handling
            }
        )

    # 3. Delete
    table.remove(Dim.id == dim_id)
    return {"status": "deleted", "id": dim_id}
