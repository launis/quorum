"""Admin Studio Workflows API Router.

Provides endpoints to manage workflow configurations.
"""

import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioSimulationServiceDep, StudioWorkflowServiceDep
from backend_v2.models.dtos.studio import (
    WorkflowAvailableExtensionsResponse,
    WorkflowDeleteResponse,
    WorkflowResponseDTO,
    WorkflowSimulationResponse,
)
from backend_v2.models.v2_core import Workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Admin Studio V2 - Workflows"])


@router.get("/", response_model=list[WorkflowResponseDTO])
async def get_workflows(
    current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep
) -> list[Workflow]:
    """Retrieve all V2 dynamic workflow definition blocks securely via SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        A list of all workflow definitions.

    Raises:
        AppException: If fetching workflows fails.
    """
    return await studio_workflow_service.list_workflows(current_user)


@router.post("/", response_model=WorkflowResponseDTO)
async def create_workflow(current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep) -> Workflow:
    """Create a new Workflow draft securely via SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The newly created workflow draft.

    Raises:
        AppException: If creating the draft fails.
    """
    return await studio_workflow_service.create_workflow_draft(current_user)


@router.get("/{id}", response_model=WorkflowResponseDTO)
async def get_workflow(
    id: str, current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep
) -> Workflow:
    """Retrieve a specific workflow definition by id securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the workflow.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The requested workflow definition.

    Raises:
        ResourceNotFoundError: If the workflow is not found.
        AppException: If fetching the workflow fails.
    """
    return await studio_workflow_service.get_workflow(current_user, id)


@router.post("/simulate", response_model=WorkflowSimulationResponse)
async def simulate_workflow(
    data: Workflow, current_user: CurrentUserDep, studio_simulation_service: StudioSimulationServiceDep
) -> WorkflowSimulationResponse:
    """Dry-run and validate a workflow DAG topology before saving.

    Args:
        data: The workflow definition to simulate.
        current_user: The authenticated user making the request.
        studio_simulation_service: The studio simulation service dependency.

    Returns:
        The results of the simulation.

    Raises:
        AppException: If the simulation fails.
    """
    result = await studio_simulation_service.simulate_workflow(current_user, data)
    return WorkflowSimulationResponse.model_validate(result)


@router.get("/{id}/available-extensions", response_model=WorkflowAvailableExtensionsResponse)
async def get_workflow_available_extensions(
    id: str, current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep
) -> WorkflowAvailableExtensionsResponse:
    """Calculate the union of all output_extensions defined across all Target Matrices within a specific DAG.

    Args:
        id: The unique identifier of the workflow.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        A WorkflowAvailableExtensionsResponse with a list of available extensions.

    Raises:
        ResourceNotFoundError: If the workflow is not found.
        AppException: If fetching the extensions fails.
    """
    extensions = await studio_workflow_service.get_workflow_available_extensions(current_user, id)
    return WorkflowAvailableExtensionsResponse(available_extensions=extensions)


@router.post("/{id}/clone", response_model=WorkflowResponseDTO)
async def clone_workflow(
    id: str, current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep
) -> Workflow:
    """Deep clone a workflow block securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the workflow to clone.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The newly cloned workflow definition.

    Raises:
        ResourceNotFoundError: If the source workflow is not found.
        AppException: If cloning the workflow fails.
    """
    return await studio_workflow_service.clone_workflow(current_user, id)


@router.put("/{id}", response_model=WorkflowResponseDTO)
async def save_workflow(
    id: str, data: Workflow, current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep
) -> Workflow:
    """Append or update a workflow definition block securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the workflow.
        data: The new configuration data for the workflow.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The updated workflow definition.

    Raises:
        ResourceNotFoundError: If the workflow is not found.
        AppException: If updating the workflow fails.
    """
    return await studio_workflow_service.save_workflow(current_user, id, data)


@router.delete("/{id}", response_model=WorkflowDeleteResponse)
async def delete_workflow(
    id: str, current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep
) -> WorkflowDeleteResponse:
    """Delete a workflow definition block securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the workflow to delete.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        A WorkflowDeleteResponse confirming the deletion.

    Raises:
        ResourceNotFoundError: If the workflow is not found.
        AppException: If deleting the workflow fails.
    """
    await studio_workflow_service.delete_workflow(current_user, id)
    return WorkflowDeleteResponse(status="success", deleted_id=id)
