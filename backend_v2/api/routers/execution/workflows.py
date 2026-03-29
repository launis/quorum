import logging
from typing import Any

from fastapi import APIRouter
from pydantic import RootModel

from backend_v2.api.dependencies import RepoDep, UserDep
from backend_v2.exceptions import ErrorCodes, ResourceNotFoundError
from backend_v2.models.v2_core import Workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])

class WorkflowSchemaResponse(RootModel[dict[str, Any]]):
    pass

@router.get("/{workflow_id}/ui_schema", response_model=WorkflowSchemaResponse)
async def get_workflow_ui_schema(
    workflow_id: str,
    current_user: UserDep,
    repository: RepoDep,
) -> WorkflowSchemaResponse:
    """Retrieve the expected inputs schema for frontend dynamic rendering."""
    workflow_dict = await repository.get_workflow_by_id(workflow_id)
    if not workflow_dict:
        msg = f"Workflow {workflow_id} not found."
        logger.error(
            "[WorkflowRouter] %s",
            msg,
            extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": workflow_id},
        )
        raise ResourceNotFoundError(resource_type="workflow", resource_id=workflow_id)

    workflow = Workflow.model_validate(workflow_dict)

    return WorkflowSchemaResponse(workflow.ui_schema)
