import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.v2_core import Step

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/steps", tags=["Admin Studio V2 - Steps"])

class StepSimulationRequest(BaseModel):
    step: Step
    mock_inputs: dict[str, Any] = {}

@router.post("/simulate", response_model=dict[str, Any])
async def simulate_step(
    data: StepSimulationRequest,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> dict[str, Any]:
    """Dry-run and validate a Step (TaskBlueprint) by compiling its prompt blocks."""
    return await studio_service.simulate_step(current_user, data.step, data.mock_inputs)

@router.get("/", response_model=list[Step])
async def get_steps(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> list[Step]:
    """Retrieve all independent Steps securely via SSOT Service Layer."""
    return await studio_service.list_steps(current_user)


@router.get("/{id}", response_model=Step)
async def get_step(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Step:
    """Retrieve a specific Step securely via SSOT Service Layer."""
    return await studio_service.get_step(current_user, id)

@router.put("/{id}", response_model=Step)
async def save_step(id: str, data: Step, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Step:
    """Append or update a Step securely via SSOT Service Layer."""
    return await studio_service.save_step(current_user, id, data)

@router.delete("/{id}")
async def delete_step(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep, force_delete: bool = False) -> dict[str, Any]:
    """Delete a Step securely via SSOT Service Layer."""
    await studio_service.delete_step(current_user, id, force_delete=force_delete)
    return {"status": "success", "deleted_id": id}

@router.post("/{id}/clone", response_model=Step)
async def clone_step(
    id: str,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> Step:
    """Deep clone a step securely via SSOT Service Layer."""
    return await studio_service.clone_step(current_user, id)
