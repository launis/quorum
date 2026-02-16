"""API Router for Configuration Components (Prompts, Mandates, etc)."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Path
from fastapi import Query as APIQuery
from pydantic import BaseModel, Field, TypeAdapter
from tinydb import Query

from backend.dependencies import DatabaseDep, RepositoryDep
from backend.services.component_registry import ComponentRegistry

logger = logging.getLogger(__name__)

from backend.models.dtos.config import (
    ComponentCreate,
    ComponentDeleteResponse,
    ComponentResponse,
    ComponentUpdate,
    RegistryComponentItem,
)

# Adapter for Polymorphic Union
_component_adapter = TypeAdapter(ComponentResponse)

router = APIRouter(tags=["Configuration"])


@router.get("", summary="List Components", response_description="All configuration components.", response_model=list[ComponentResponse])
async def get_components(
    repo: RepositoryDep,
    type: str | None = None,
    exclude_type: Annotated[list[str] | None, APIQuery()] = None
) -> list[ComponentResponse]:
    """Retrieves all defined configuration components (Prompts, Mandates, Rules, etc).

    Args:
        repo (RepositoryDep): Repository dependency.
        type (str | None): Optional filter by component type.
        exclude_type (list[str] | None): Optional types to exclude.

    Returns:
        list[ComponentResponse]: List of configuration components.
    """
    try:
        raw_components = await repo.get_all_components(type=type, exclude_types=exclude_type)
        # Use Adapter for Union
        return [_component_adapter.validate_python(c) for c in raw_components]
    except Exception as e:
        from backend.exceptions import AppException
        
        error_code = "COMPONENTS_LIST_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.get("/{comp_id}", summary="Get Component", response_description="The requested component.", response_model=ComponentResponse)
def get_component(db: DatabaseDep, comp_id: str = Path(..., description="Component ID or Name")) -> ComponentResponse:
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
    
    return _component_adapter.validate_python(res[0])





@router.get("/registry_items", summary="List Registry Components", response_description="All components loaded from seed.")
async def list_registry_items(repo: RepositoryDep) -> list[RegistryComponentItem]:
    """Retrieves all system components directly from the Repository."""
    # Refactored Feb 2026: Use Repository instead of in-memory singleton
    raw_components = await repo.get_all_components()
    items = []
    
    for comp_data in raw_components:
        c_id = comp_data.get("id")
        if not c_id: continue
        
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


@router.post("", summary="Create Component", response_description="Status and ID.", response_model=ComponentResponse)
def create_component(comp: ComponentCreate, db: DatabaseDep) -> ComponentResponse:
    """Creates a new configuration component."""
    try:
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
        # Re-map class back to component_class for DTO if needed, or DTO allows extra
        # But ComponentResponse uses component_class.
        # We should normalize data for response.
        response_data = new_comp.copy()
        if "class" in response_data:
             response_data["component_class"] = response_data.pop("class")
        
        return _component_adapter.validate_python(response_data)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e

        error_code = "COMPONENT_CREATION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.put("/{comp_id}", summary="Update Component", response_description="Update status.", response_model=ComponentResponse)
def update_component(comp_id: str, update: ComponentUpdate, db: DatabaseDep) -> ComponentResponse:
    """Updates an existing component's content and metadata.

    Args:
        comp_id (str): The ID of the component to update.
        update (ComponentUpdate): The new data.
        db (DatabaseDep): Database dependency.

    Returns:
        ComponentResponse: The updated component.

    Raises:
        HTTPException: If not found (404).
    """
    try:
        Component = Query()
        table = db.table("components")

        # Find component (by ID or Name)
        query = (Component.id == comp_id) | (Component.name == comp_id)
        exists = table.search(query)
        if not exists:
            from backend.exceptions import ResourceNotFoundError

            error_code = "COMPONENT_NOT_FOUND"
            logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
            raise ResourceNotFoundError("Component", comp_id, details={"error_code": error_code})
        
        current_data = exists[0]

        update_data = {"content": update.content}
        if update.description:
            update_data["description"] = update.description
        if update.citation:
            update_data["citation"] = update.citation
        if update.citation_full:
            update_data["citation_full"] = update.citation_full
        if update.type:
            update_data["type"] = update.type

        table.update(update_data, query)
        
        # Merge for response
        updated_comp = {**current_data, **update_data}
        
        # Normalize 'class' key for DTO if present
        if "class" in updated_comp:
            updated_comp["component_class"] = updated_comp["class"]

        return _component_adapter.validate_python(updated_comp)
    except Exception as e:
        from backend.exceptions import AppException
        if isinstance(e, AppException):
            raise e
        
        error_code = "COMPONENT_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=500, details={"error_code": error_code}
        ) from e


@router.delete("/{comp_id}", summary="Delete Component", response_description="Delete status.", response_model=ComponentDeleteResponse)
async def delete_component(
    comp_id: str,
    db: DatabaseDep,
    repo: RepositoryDep
) -> ComponentDeleteResponse:
    """Deletes a component if it is not referenced by any existing steps OR executions."""
    # 1. Existence Check (via TinyDB/Generic Table - maintaining local consistency)
    table = db.table("components")
    Component = Query()

    # We still use direct DB access for component existence as 'repo' might be specialized for Workflow/Execution
    # but strictly speaking we should use repo.get_component_by_id.
    # For now, keeping legacy check to avoid breaking TinyDB specifics if any,
    # but ideally we migrate fully to repo.
    query = (Component.id == comp_id) | (Component.name == comp_id)
    exists = table.search(query)
    if not exists:
        from backend.exceptions import ResourceNotFoundError

        error_code = "COMPONENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
        raise ResourceNotFoundError("Component", comp_id, details={"error_code": error_code})
    
    # Store ID before deletion for response
    target_id = exists[0].get("id", comp_id)

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

    table.remove(query)
    return ComponentDeleteResponse(status="deleted", id=target_id)
