"""Admin Studio Steps API Router.

Provides endpoints to manage step configurations.
"""

import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioSimulationServiceDep, StudioWorkflowServiceDep
from backend_v2.models.dtos.studio import (
    StepDeleteResponse,
    StepResponseDTO,
    StepSimulationRequest,
    StepSimulationResponse,
)
from backend_v2.models.v2_core import Step

logger = logging.getLogger(__name__)

__all__ = ["router"]

router = APIRouter(prefix="/steps", tags=["Admin Studio V2 - Steps"])


@router.post("/simulate", response_model=StepSimulationResponse)
async def simulate_step(
    data: StepSimulationRequest,
    current_user: CurrentUserDep,
    studio_simulation_service: StudioSimulationServiceDep,
) -> StepSimulationResponse:
    """Dry-run and validate a Step (TaskBlueprint) by compiling its prompt blocks.

    Args:
        data: The simulation request containing the step and mock inputs.
        current_user: The authenticated user making the request.
        studio_simulation_service: The studio simulation service dependency.

    Returns:
        The results of the simulation.

    Raises:
        AppException: If the simulation fails.
    """
    result = await studio_simulation_service.simulate_step(current_user, data.step, data.mock_inputs)
    return StepSimulationResponse.model_validate(result)


@router.get("/", response_model=list[StepResponseDTO])
async def get_steps(current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep) -> list[Step]:
    """Retrieve all V2 dynamic step execution block schemas securely via SSOT.

    Args:
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        A list of all steps.

    Raises:
        AppException: If fetching steps fails.
    """
    return await studio_workflow_service.list_steps(current_user)


@router.post("/", response_model=StepResponseDTO)
async def create_step(current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep) -> Step:
    """Create a new Step draft securely via SSOT.

    Args:
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The newly created step draft.

    Raises:
        AppException: If creating the draft fails.
    """
    return await studio_workflow_service.create_step_draft(current_user)


@router.get("/{id}", response_model=StepResponseDTO)
async def get_step(id: str, current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep) -> Step:
    """Retrieve a specific Step securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the step.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The requested step.

    Raises:
        ResourceNotFoundError: If the step is not found.
        AppException: If fetching the step fails.
    """
    return await studio_workflow_service.get_step(current_user, id)


@router.put("/{id}", response_model=StepResponseDTO)
async def save_step(
    id: str, data: Step, current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep
) -> Step:
    """Append or update a Step securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the step.
        data: The new configuration data for the step.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The updated step.

    Raises:
        ResourceNotFoundError: If the step is not found.
        AppException: If updating the step fails.
    """
    return await studio_workflow_service.save_step(current_user, id, data)


@router.delete("/{id}", response_model=StepDeleteResponse)
async def delete_step(
    id: str, current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep, force_delete: bool = False
) -> StepDeleteResponse:
    """Delete a Step securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the step to delete.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.
        force_delete: Whether to force delete the step.

    Returns:
        A StepDeleteResponse confirming the deletion.

    Raises:
        ResourceNotFoundError: If the step is not found.
        AppException: If deleting the step fails.
    """
    await studio_workflow_service.delete_step(current_user, id, force_delete=force_delete)
    return StepDeleteResponse(status="success", deleted_id=id)


@router.post("/{id}/clone", response_model=StepResponseDTO)
async def clone_step(
    id: str,
    current_user: CurrentUserDep,
    studio_workflow_service: StudioWorkflowServiceDep,
) -> Step:
    """Deep clone a step securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the step to clone.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The newly cloned step.

    Raises:
        ResourceNotFoundError: If the source step is not found.
        AppException: If cloning the step fails.
    """
    return await studio_workflow_service.clone_step(current_user, id)
