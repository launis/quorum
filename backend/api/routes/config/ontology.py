"""API Router for Ontology and Dimensions."""

from typing import Annotated

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.dependencies import DatabaseDep

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

    from backend.exceptions import ResourceNotFoundError

    logger = logging.getLogger(__name__)
    table = db.table("dimensions")
    all_dims = table.all()

    if not all_dims:
        error_code = "NO_DIMENSIONS_FOUND"
        logger.error(f"{error_code}: Ontology table is empty.", exc_info=True)
        raise ResourceNotFoundError(
            "Dimensions", "all", details={"error_code": error_code, "help": "Run seed script."}
        )

    return sorted([d["id"] for d in all_dims])
