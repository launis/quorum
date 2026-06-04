import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.dtos.studio import (
    StepDeleteResponse,
    StepResponseDTO,
    StepSimulationRequest,
    StepSimulationResponse,
)
from backend_v2.models.v2_core import Step

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/steps", tags=["Admin Studio V2 - Steps"])


@router.post("/simulate", response_model=StepSimulationResponse)
async def simulate_step(
    data: StepSimulationRequest,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> StepSimulationResponse:
    """Dry-run and validate a Step (TaskBlueprint) by compiling its prompt blocks."""
    result = await studio_service.simulate_step(current_user, data.step, data.mock_inputs)
    return StepSimulationResponse(**result)


@router.get("/", response_model=list[StepResponseDTO])
async def get_steps(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> list[Step]:
    """Retrieve all V2 dynamic step execution block schemas securely via SSOT."""
    return await studio_service.list_steps(current_user)


@router.post("/", response_model=StepResponseDTO)
async def create_step(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Step:
    """Create a new Step draft securely via SSOT."""
    return await studio_service.create_step_draft(current_user)


@router.get("/{id}", response_model=StepResponseDTO)
async def get_step(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Step:
    """Retrieve a specific Step securely via SSOT Service Layer."""
    return await studio_service.get_step(current_user, id)


@router.put("/{id}", response_model=StepResponseDTO)
async def save_step(id: str, data: Step, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Step:
    """Append or update a Step securely via SSOT Service Layer."""
    return await studio_service.save_step(current_user, id, data)


@router.delete("/{id}", response_model=StepDeleteResponse)
async def delete_step(
    id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep, force_delete: bool = False
) -> StepDeleteResponse:
    """Delete a Step securely via SSOT Service Layer."""
    await studio_service.delete_step(current_user, id, force_delete=force_delete)
    return StepDeleteResponse(status="success", deleted_id=id)


@router.post("/{id}/clone", response_model=StepResponseDTO)
async def clone_step(
    id: str,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> Step:
    """Deep clone a step securely via SSOT Service Layer."""
    return await studio_service.clone_step(current_user, id)
