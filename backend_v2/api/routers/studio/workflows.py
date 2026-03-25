import logging
from typing import Any

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.v2_core import Workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Admin Studio V2 - Workflows"])

@router.get("/", response_model=list[Workflow])
async def get_workflows(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> list[Workflow]:
    """Retrieve all V2 dynamic workflow definition blocks securely via SSOT Service Layer."""
    return await studio_service.list_workflows(current_user)

@router.get("/{id}", response_model=Workflow)
async def get_workflow(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Workflow:
    """Retrieve a specific workflow definition by id securely via SSOT Service Layer."""
    return await studio_service.get_workflow(current_user, id)



@router.put("/{id}", response_model=Workflow)
async def save_workflow(id: str, data: Workflow, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Workflow:
    """Append or update a workflow definition block securely via SSOT Service Layer."""
    return await studio_service.save_workflow(current_user, id, data)

@router.delete("/{id}")
async def delete_workflow(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> dict[str, Any]:
    """Delete a workflow definition block securely via SSOT Service Layer."""
    await studio_service.delete_workflow(current_user, id)
    return {"status": "success", "deleted_id": id}
