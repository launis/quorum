"""Workflow Execution Router.

Provides endpoints for retrieving workflow schema expectations required for
dynamic frontend rendering.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, ExecutionServiceDep
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO

__all__ = ["get_workflow_ui_schema", "router"]

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
        workflow_id: Canonical Opaque Stripe ID of the workflow blueprint.
        current_user: Authenticated user token claims making the request.
        execution_service: Execution domain service dependency.

    Returns:
        Workflow schema response containing the expected input definitions.

    Raises:
        ResourceNotFoundError: If the target workflow does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the authenticated user lacks permission to access the workflow
            (ErrorCodes.PERMISSION_DENIED).
    """
    return await execution_service.get_workflow_ui_schema(workflow_id)
