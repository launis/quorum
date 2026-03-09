import logging
from typing import Any

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.v2_core import TaskBlueprint

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/task-blueprints", tags=["Admin Studio V2 - Task Blueprints"])

@router.get("/", response_model=list[TaskBlueprint])
async def get_task_blueprints(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> list[TaskBlueprint]:
    """Retrieve all independent Task Blueprints securely via SSOT Service Layer."""
    return await studio_service.list_task_blueprints(current_user)

@router.get("/{id}", response_model=TaskBlueprint)
async def get_task_blueprint(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> TaskBlueprint:
    """Retrieve a specific Task Blueprint securely via SSOT Service Layer."""
    return await studio_service.get_task_blueprint(current_user, id)

@router.put("/{id}", response_model=TaskBlueprint)
async def save_task_blueprint(id: str, data: TaskBlueprint, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> TaskBlueprint:
    """Append or update a Task Blueprint securely via SSOT Service Layer."""
    return await studio_service.save_task_blueprint(current_user, id, data)

@router.delete("/{id}")
async def delete_task_blueprint(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> dict[str, Any]:
    """Delete a Task Blueprint securely via SSOT Service Layer."""
    await studio_service.delete_task_blueprint(current_user, id)
    return {"status": "success", "deleted_id": id}
