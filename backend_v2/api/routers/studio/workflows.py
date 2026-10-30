"""Admin Studio Workflows API Router.

Provides endpoints to manage workflow configurations and retrieve UI rendering schemas.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Path, status

from backend_v2.api.dependencies import (
    CurrentUserDep,
    ExecutionServiceDep,
    StudioSimulationServiceDep,
    StudioWorkflowServiceDep,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.studio import (
    WorkflowAvailableExtensionsResponse,
    WorkflowDeleteResponse,
    WorkflowResponseDTO,
    WorkflowSimulationResponse,
)
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO

logger = logging.getLogger(__name__)

__all__ = ["get_workflow_ui_schema", "router"]

router = APIRouter(prefix="/workflows", tags=["Admin Studio V2 - Workflows"])


@router.get("/", response_model=list[WorkflowResponseDTO])
async def get_workflows(
    current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep
) -> list[WorkflowResponseDTO]:
    """Retrieve all V2 dynamic workflow definition blocks securely via SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        A list of all workflow definitions.

    Raises:
        AppException: With ErrorCodes.STATE_INTEGRITY_ERROR if fetching or validating workflows fails.
    """
    return await studio_workflow_service.list_workflows(current_user)


@router.post("/", response_model=WorkflowResponseDTO)
async def create_workflow(
    current_user: CurrentUserDep, studio_workflow_service: StudioWorkflowServiceDep
) -> WorkflowResponseDTO:
    """Create a new Workflow draft securely via SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The newly created workflow draft.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if no active model registries exist.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if modification rights are denied.
        AppException: With ErrorCodes.WORKFLOW_COMPILATION_ERROR or ErrorCodes.STATE_INTEGRITY_ERROR if creating the draft fails.
    """
    return await studio_workflow_service.create_workflow_draft(current_user)


@router.get("/{id}", response_model=WorkflowResponseDTO)
async def get_workflow(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    studio_workflow_service: StudioWorkflowServiceDep,
) -> WorkflowResponseDTO:
    """Retrieve a specific workflow definition by id securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the workflow.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The requested workflow definition.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the workflow is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant isolation is violated.
        AppException: With ErrorCodes.STATE_INTEGRITY_ERROR if fetching the workflow fails.
    """
    return await studio_workflow_service.get_workflow(current_user, id)


@router.get("/{id}/ui_schema", response_model=WorkflowSchemaResponseDTO)
async def get_workflow_ui_schema(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> WorkflowSchemaResponseDTO:
    """Retrieve the expected inputs schema for frontend dynamic rendering.

    Args:
        id: Canonical Opaque Stripe ID of the workflow blueprint.
        current_user: Authenticated user token claims making the request.
        execution_service: Execution domain service dependency.

    Returns:
        Workflow schema response containing the expected input definitions.

    Raises:
        ResourceNotFoundError: If the target workflow does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the authenticated user lacks permission to access the workflow
            (ErrorCodes.PERMISSION_DENIED).
    """
    return await execution_service.get_workflow_ui_schema(id)


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
        AppException: With ErrorCodes.WORKFLOW_COMPILATION_ERROR if the simulation fails.
    """
    return await studio_simulation_service.simulate_workflow(current_user, data)


@router.get("/{id}/available-extensions", response_model=WorkflowAvailableExtensionsResponse)
async def get_workflow_available_extensions(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    studio_workflow_service: StudioWorkflowServiceDep,
) -> WorkflowAvailableExtensionsResponse:
    """Calculate the union of all output_extensions defined across all Target Matrices within a specific DAG.

    Args:
        id: The unique identifier of the workflow.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        A WorkflowAvailableExtensionsResponse with a list of available extensions.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the workflow is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant isolation is violated.
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND if resolving prompt block extensions fails.
    """
    extensions = await studio_workflow_service.get_workflow_available_extensions(current_user, id)
    return WorkflowAvailableExtensionsResponse(available_extensions=extensions)


@router.post("/{id}/clone", response_model=WorkflowResponseDTO)
async def clone_workflow(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    studio_workflow_service: StudioWorkflowServiceDep,
) -> WorkflowResponseDTO:
    """Deep clone a workflow block securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the workflow to clone.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The newly cloned workflow definition.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the source workflow is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant isolation or modification rights are violated.
        AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.WORKFLOW_COMPILATION_ERROR if cloning the workflow fails.
    """
    return await studio_workflow_service.clone_workflow(current_user, id)


@router.put("/{id}", response_model=WorkflowResponseDTO)
async def save_workflow(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    data: Workflow,
    current_user: CurrentUserDep,
    studio_workflow_service: StudioWorkflowServiceDep,
) -> WorkflowResponseDTO:
    """Append or update a workflow definition block securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the workflow.
        data: The new configuration data for the workflow.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        The updated workflow definition.

    Raises:
        AppException: With ErrorCodes.ID_MISMATCH if path id does not match payload id.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the workflow is not found after save.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if modification rights are denied.
        AppException: With ErrorCodes.WORKFLOW_COMPILATION_ERROR or ErrorCodes.STATE_INTEGRITY_ERROR if updating the workflow fails.
    """
    if data.id != id:
        logger.error(
            "[WorkflowsRouter] %s: Path id '%s' does not match payload id '%s' (Initiator: %s).",
            ErrorCodes.ID_MISMATCH.name,
            id,
            data.id,
            current_user.id,
            exc_info=True,
            extra={"error_code": ErrorCodes.ID_MISMATCH.value, "workflow_id": id},
        )
        raise AppException(
            message=f"Path id '{id}' does not match payload id '{data.id}'",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.ID_MISMATCH.value},
        )

    return await studio_workflow_service.save_workflow(current_user, id, data)


@router.delete("/{id}", response_model=WorkflowDeleteResponse)
async def delete_workflow(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    studio_workflow_service: StudioWorkflowServiceDep,
) -> WorkflowDeleteResponse:
    """Delete a workflow definition block securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the workflow to delete.
        current_user: The authenticated user making the request.
        studio_workflow_service: The studio workflow service dependency.

    Returns:
        A WorkflowDeleteResponse confirming the deletion.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the workflow is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if modification rights are denied.
        AppException: With ErrorCodes.SYSTEM_PROTECTED_RESOURCE if deleting the workflow fails.
    """
    await studio_workflow_service.delete_workflow(current_user, id)
    return WorkflowDeleteResponse(status="success", deleted_id=id)
