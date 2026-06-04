import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import ExecutionServiceDep, UserDep
from backend_v2.models.v2_core import WorkflowSchemaResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("/{workflow_id}/ui_schema", response_model=WorkflowSchemaResponse)
async def get_workflow_ui_schema(
    workflow_id: str,
    current_user: UserDep,
    execution_service: ExecutionServiceDep,
) -> WorkflowSchemaResponse:
    """Retrieve the expected inputs schema for frontend dynamic rendering."""
    return await execution_service.get_workflow_ui_schema(workflow_id)
