"""Workflow Execution Router.

Provides endpoints for retrieving workflow schema expectations required for
dynamic frontend rendering.
"""

import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, ExecutionServiceDep
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("/{workflow_id}/ui_schema", response_model=WorkflowSchemaResponseDTO)
async def get_workflow_ui_schema(
    workflow_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> WorkflowSchemaResponseDTO:
    """Retrieve the expected inputs schema for frontend dynamic rendering.

    Args:
        workflow_id: The unique identifier of the workflow blueprint.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        A WorkflowSchemaResponseDTO containing the UI structure.

    Raises:
        AppException: If the workflow is not found or user lacks permission.
    """
    return await execution_service.get_workflow_ui_schema(workflow_id)
