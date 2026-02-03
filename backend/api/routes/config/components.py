"""API Router for Configuration Components (Prompts, Mandates, etc)."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Path
from pydantic import BaseModel, Field
from tinydb import Query

from backend.dependencies import DatabaseDep, RepositoryDep
from backend.services.component_registry import ComponentRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["Configuration"])


class ComponentUpdate(BaseModel):
    """Payload for updating a configuration component.

    Attributes:
        content (str | dict | list): The template content.
        description (str): Metadata description.
        citation (str): Short citation anchor.
        citation_full (str): Complete bibliographic reference.
        type (str): Component categorization.
    """

    content: Annotated[
        str | dict[str, Any] | list[Any],
        Field(description="The template content (prompt text, rule text, or config object)."),
    ]
    description: Annotated[str | None, Field(description="Metadata description.")] = None
    citation: Annotated[str | None, Field(description="Short citation anchor.")] = None
    citation_full: Annotated[str | None, Field(description="Complete bibliographic reference.")] = None
    type: Annotated[
        str | None,
        Field(description="Component categorization (e.g. 'mandate', 'prompt', 'evaluation_matrix')."),
    ] = None


class ComponentCreate(BaseModel):
    """Payload for creating a new component."""

    id: Annotated[str, Field(description="Unique Identifier for the component.")]
    name: Annotated[str, Field(description="Human readable name.")]
    type: Annotated[str, Field(description="Component Type (header, prompt, evaluation_matrix, etc).")]
    content: Annotated[str | dict[str, Any] | list[Any], Field(description="The content (text or JSON object).")]
    description: Annotated[str | None, Field(description="Description of purpose.")] = None
    citation: Annotated[str | None, Field(description="Short citation.")] = None
    citation_full: Annotated[str | None, Field(description="Full citation.")] = None
    module: Annotated[str | None, Field(description="Source module (legacy).")] = "config"
    component_class: Annotated[str | None, Field(description="Class name.")] = "ConfigComponent"


@router.get("/components", summary="List Components", response_description="All configuration components.")
def get_components(db: DatabaseDep, type: str | None = None):
    """Retrieves all defined configuration components (Prompts, Mandates, Rules, etc).

    Args:
        db (DatabaseDep): Database dependency.
        type (str | None): Optional filter by component type.

    Returns:
        list[dict]: List of configuration components.
    """
    if type:
        Component = Query()
        return db.table("components").search(Component.type == type)
    return db.table("components").all()


@router.get("/components/{comp_id}", summary="Get Component", response_description="The requested component.")
def get_component(db: DatabaseDep, comp_id: str = Path(..., description="Component ID or Name")):
    """Retrieves a single component by ID or Name."""
    Component = Query()
    res = db.table("components").search(Component.id == comp_id)
    if not res:
        res = db.table("components").search(Component.name == comp_id)

    if not res:
        from backend.exceptions import ResourceNotFoundError

        error_code = "COMPONENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
        raise ResourceNotFoundError("Component", comp_id, details={"error_code": error_code})
    return res[0]


class RegistryComponentItem(BaseModel):
    """Schema for a component item in the registry list."""

    id: Annotated[
        str,
        Field(description="Component ID", json_schema_extra={"x-ui-label": "ID"}),
    ]
    name: Annotated[
        str,
        Field(description="Meaningful Label", json_schema_extra={"x-ui-label": "Label"}),
    ]
    type: Annotated[
        str,
        Field(description="Type category", json_schema_extra={"x-ui-label": "Type"}),
    ]
    description: Annotated[
        str | None,
        Field(
            description="Short description",
            json_schema_extra={"x-ui-label": "Description"},
        ),
    ] = None
    content: Annotated[
        Any,
        Field(description="The actual content", json_schema_extra={"x-ui-label": "Content"}),
    ] = None
    citation: Annotated[
        str | None,
        Field(description="Short reference", json_schema_extra={"x-ui-label": "Citation"}),
    ] = None


@router.get("/registry_items", summary="List Registry Components", response_description="All components loaded from seed.")
def list_registry_items() -> list[RegistryComponentItem]:
    """Retrieves all system components directly from the in-memory ComponentRegistry."""
    registry = ComponentRegistry()
    items = []
    # Registry _components is dict[id, dict]
    for comp_id, comp_data in registry._components.items():
        # Ensure 'id' exists in data, fallback to key
        c_id = comp_data.get("id", comp_id)
        # Handle 'name' or 'label'
        c_name = comp_data.get("name") or comp_data.get("label") or c_id

        items.append(RegistryComponentItem(
            id=c_id,
            name=c_name,
            type=comp_data.get("type", "unknown"),
            description=comp_data.get("description"),
            content=comp_data.get("content"),
            citation=comp_data.get("citation")
        ))
    return items


@router.post("/components", summary="Create Component", response_description="Status and ID.")
def create_component(comp: ComponentCreate, db: DatabaseDep):
    """Creates a new configuration component."""
    table = db.table("components")
    if table.search(Query().id == comp.id):
        from backend.exceptions import ConflictError

        error_code = "COMPONENT_ID_EXISTS"
        logger.error(f"{error_code}: ID {comp.id}", exc_info=True)
        raise ConflictError(message="Resource conflict", details={"error_code": error_code})

    new_comp = comp.model_dump()
    if "component_class" in new_comp:
        new_comp["class"] = new_comp.pop("component_class")

    table.insert(new_comp)
    return {"status": "created", "id": comp.id}


@router.put("/components/{comp_id}", summary="Update Component", response_description="Update status.")
def update_component(comp_id: str, update: ComponentUpdate, db: DatabaseDep):
    """Updates an existing component's content and metadata.

    Args:
        comp_id (str): The ID of the component to update.
        update (ComponentUpdate): The new data.
        db (DatabaseDep): Database dependency.

    Returns:
        dict: Status and ID.

    Raises:
        HTTPException: If not found (404).
    """
    Component = Query()
    table = db.table("components")

    exists = table.search((Component.id == comp_id) | (Component.name == comp_id))
    if not exists:
        from backend.exceptions import ResourceNotFoundError

        error_code = "COMPONENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
        raise ResourceNotFoundError("Component", comp_id, details={"error_code": error_code})

    update_data = {"content": update.content}
    if update.description:
        update_data["description"] = update.description
    if update.citation:
        update_data["citation"] = update.citation
    if update.citation_full:
        update_data["citation_full"] = update.citation_full
    if update.type:
        update_data["type"] = update.type

    table.update(update_data, (Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "updated", "id": comp_id}


@router.delete("/components/{comp_id}", summary="Delete Component", response_description="Delete status.")
async def delete_component(
    comp_id: str,
    db: DatabaseDep,
    repo: RepositoryDep
):
    """Deletes a component if it is not referenced by any existing steps OR executions."""
    # 1. Existence Check (via TinyDB/Generic Table - maintaining local consistency)
    table = db.table("components")
    Component = Query()

    # We still use direct DB access for component existence as 'repo' might be specialized for Workflow/Execution
    # but strictly speaking we should use repo.get_component_by_id.
    # For now, keeping legacy check to avoid breaking TinyDB specifics if any,
    # but ideally we migrate fully to repo.
    exists = table.search((Component.id == comp_id) | (Component.name == comp_id))
    if not exists:
        from backend.exceptions import ResourceNotFoundError

        error_code = "COMPONENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
        raise ResourceNotFoundError("Component", comp_id, details={"error_code": error_code})

    # 2. Referential Integrity Check 1: Steps (Legacy TinyDB method)
    # TODO: Migrate to repo.get_steps_using_component(comp_id)
    steps = db.table("steps").all()
    used_in = []
    for s in steps:
        if s.get("component") == comp_id:
            used_in.append(s["id"])
            continue
        prompts = s.get("execution_config", {}).get("llm_prompts", [])
        if comp_id in prompts:
            used_in.append(s["id"])

    # 3. Referential Integrity Check 2: Executions (Abstract Repository)
    # This enables Firestore support without leaking implementation details
    exec_count = await repo.count_executions_by_matrix(comp_id)
    if exec_count > 0:
         # Use specific error for UI handling
        from backend.exceptions import ConflictError

        error_code = "Errors.DeleteBlockedByExecutions"
        msg = (
            f"Cannot delete component because it has {exec_count} associated executions."
        )
        logger.error(f"{error_code}: {msg}")
        raise ConflictError(
            message=msg,
            details={
                "error_code": error_code,
                "count": exec_count,
            }
        )

    if used_in:
        from backend.exceptions import ConflictError

        error_code = "COMPONENT_IN_USE"
        logger.error(f"{error_code}: ID {comp_id} used in {used_in}", exc_info=True)
        raise ConflictError(message="Resource conflict", details={"error_code": error_code, **{"used_in": used_in}})

    table.remove((Component.id == comp_id) | (Component.name == comp_id))
    return {"status": "deleted", "id": comp_id}
