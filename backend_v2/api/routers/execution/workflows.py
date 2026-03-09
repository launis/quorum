from fastapi import APIRouter

from backend_v2.api.dependencies import RepoDep, UserDep
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.v2_core import Workflow

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.get("/{workflow_id}/ui_schema", response_model=dict[str, str])
async def get_workflow_ui_schema(
    workflow_id: str,
    current_user: UserDep,
    repository: RepoDep,
) -> dict[str, str]:
    """Retrieve the expected inputs schema for frontend dynamic rendering."""
    workflow_dict = await repository.get_workflow_by_id(workflow_id)
    if not workflow_dict:
        raise ResourceNotFoundError(resource_type="workflow", resource_id=workflow_id)

    workflow = Workflow.model_validate(workflow_dict)

    return workflow.expected_inputs
