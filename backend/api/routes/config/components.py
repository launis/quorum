"""API Router for Configuration Components (Prompts, Mandates, etc)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Path
from fastapi import Query as APIQuery
from pydantic import TypeAdapter

from backend.dependencies import RepositoryDep

logger = logging.getLogger(__name__)

from backend.models.dtos.config import (
    ComponentCreate,
    ComponentDeleteResponse,
    ComponentResponse,
    ComponentUpdate,
    RegistryComponentItem,
)

# Adapter for Polymorphic Union
_component_adapter: TypeAdapter[ComponentResponse] = TypeAdapter(ComponentResponse)

router = APIRouter(tags=["Configuration"])


@router.get(
    "",
    summary="List Components",
    response_description="All configuration components.",
    response_model=list[ComponentResponse],
)
async def get_components(
    repo: RepositoryDep, type: str | None = None, exclude_type: Annotated[list[str] | None, APIQuery()] = None
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
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e


@router.get(
    "/{comp_id}",
    summary="Get Component",
    response_description="The requested component.",
    response_model=ComponentResponse,
)
async def get_component(
    repo: RepositoryDep, comp_id: str = Path(..., description="Component ID or Name")
) -> ComponentResponse:
    """Retrieves a single component by ID or Name."""
    res = await repo.get_component_by_id(comp_id)
    if not res:
        res = await repo.get_component_by_name(comp_id)

    if not res:
        from backend.exceptions import ResourceNotFoundError

        error_code = "COMPONENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
        raise ResourceNotFoundError("Component", comp_id, details={"error_code": error_code})

    # Normalize 'class' key for DTO if needed
    if "class" in res:
        res["component_class"] = res["class"]

    return _component_adapter.validate_python(res)


@router.get(
    "/registry_items", summary="List Registry Components", response_description="All components loaded from seed."
)
async def list_registry_items(repo: RepositoryDep) -> list[RegistryComponentItem]:
    """Retrieves all system components directly from the Repository."""
    # Refactored Feb 2026: Use Repository instead of in-memory singleton
    raw_components = await repo.get_all_components()
    items = []

    for comp_data in raw_components:
        c_id = comp_data.get("id")
        if not c_id:
            continue

        # Handle 'name' or 'label'
        c_name = comp_data.get("name") or comp_data.get("label") or c_id

        items.append(
            RegistryComponentItem(
                id=c_id,
                name=c_name,
                type=comp_data.get("type", "unknown"),
                description=comp_data.get("description"),
                content=comp_data.get("content"),
                citation=comp_data.get("citation"),
            )
        )
    return items


@router.post("", summary="Create Component", response_description="Status and ID.", response_model=ComponentResponse)
async def create_component(comp: ComponentCreate, repo: RepositoryDep) -> ComponentResponse:
    """Creates a new configuration component."""
    try:
        # Check existence
        existing = await repo.get_component_by_id(comp.id)
        if existing:
            from backend.exceptions import ConflictError

            error_code = "COMPONENT_ID_EXISTS"
            logger.error(f"{error_code}: ID {comp.id}", exc_info=True)
            raise ConflictError(message="Resource conflict", details={"error_code": error_code})

        new_comp = comp.model_dump()
        if "component_class" in new_comp:
            new_comp["class"] = new_comp.pop("component_class")

        await repo.create_component(new_comp)

        # Normalize data for response
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
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e


@router.put(
    "/{comp_id}", summary="Update Component", response_description="Update status.", response_model=ComponentResponse
)
async def update_component(comp_id: str, update: ComponentUpdate, repo: RepositoryDep) -> ComponentResponse:
    """Updates an existing component's content and metadata.

    Args:
        comp_id (str): The ID of the component to update.
        update (ComponentUpdate): The new data.
        repo (RepositoryDep): Repository dependency.

    Returns:
        ComponentResponse: The updated component.

    Raises:
        HTTPException: If not found (404).
    """
    try:
        # Find component (by ID or Name)
        current_data = await repo.get_component_by_id(comp_id)
        if not current_data:
            current_data = await repo.get_component_by_name(comp_id)

        if not current_data:
            from backend.exceptions import ResourceNotFoundError

            error_code = "COMPONENT_NOT_FOUND"
            logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
            raise ResourceNotFoundError("Component", comp_id, details={"error_code": error_code})

        # Real ID in case searched by name
        real_id = str(current_data.get("id"))

        update_data = {}
        if update.content is not None:
            update_data["content"] = update.content
        if update.description:
            update_data["description"] = update.description
        if update.citation:
            update_data["citation"] = update.citation
        if update.citation_full:
            update_data["citation_full"] = update.citation_full
        if update.type:
            update_data["type"] = update.type

        await repo.update_component(real_id, update_data)

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
        raise AppException(message=str(e), status_code=500, details={"error_code": error_code}) from e


@router.delete(
    "/{comp_id}",
    summary="Delete Component",
    response_description="Delete status.",
    response_model=ComponentDeleteResponse,
)
async def delete_component(comp_id: str, repo: RepositoryDep) -> ComponentDeleteResponse:
    """Deletes a component if it is not referenced by any existing steps OR executions."""
    # 1. Existence Check
    existing = await repo.get_component_by_id(comp_id)
    if not existing:
        existing = await repo.get_component_by_name(comp_id)

    if not existing:
        from backend.exceptions import ResourceNotFoundError

        error_code = "COMPONENT_NOT_FOUND"
        logger.error(f"{error_code}: ID {comp_id}", exc_info=True)
        raise ResourceNotFoundError("Component", comp_id, details={"error_code": error_code})

    # Store ID before deletion for response
    target_id = existing.get("id", comp_id)

    # 2. Referential Integrity Check 1: Steps
    steps = await repo.get_all_steps()
    used_in = []

    # Scan steps for usage
    for s in steps:
        if s.get("component") == target_id:
            used_in.append(s["id"])
            continue
        prompts = s.get("execution_config", {}).get("llm_prompts", [])
        if target_id in prompts:
            used_in.append(s["id"])

    # 3. Referential Integrity Check 2: Executions
    exec_count = await repo.count_executions_by_matrix(target_id)
    if exec_count > 0:
        # Use specific error for UI handling
        from backend.exceptions import ConflictError

        error_code = "Errors.DeleteBlockedByExecutions"
        msg = f"Cannot delete component because it has {exec_count} associated executions."
        logger.error(f"{error_code}: {msg}")
        raise ConflictError(
            message=msg,
            details={
                "error_code": error_code,
                "count": exec_count,
            },
        )

    if used_in:
        from backend.exceptions import ConflictError

        error_code = "COMPONENT_IN_USE"
        logger.error(f"{error_code}: ID {target_id} used in {used_in}", exc_info=True)
        raise ConflictError(message="Resource conflict", details={"error_code": error_code, **{"used_in": used_in}})

    await repo.delete_component(target_id)
    return ComponentDeleteResponse(status="deleted", id=target_id)
