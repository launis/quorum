import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.studio import WorkflowDeleteResponse, WorkflowResponseDTO, WorkflowSimulationResponse
from backend_v2.models.v2_core import Workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["Admin Studio V2 - Workflows"])


@router.get("/", response_model=list[WorkflowResponseDTO])
async def get_workflows(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> list[Workflow]:
    """Retrieve all V2 dynamic workflow definition blocks securely via SSOT Service Layer."""
    return await studio_service.list_workflows(current_user)


@router.post("/", response_model=WorkflowResponseDTO)
async def create_workflow(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Workflow:
    """Create a new Workflow draft securely via SSOT Service Layer."""
    return await studio_service.create_workflow_draft(current_user)


@router.get("/{id}", response_model=WorkflowResponseDTO)
async def get_workflow(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Workflow:
    """Retrieve a specific workflow definition by id securely via SSOT Service Layer."""
    return await studio_service.get_workflow(current_user, id)


@router.post("/simulate", response_model=WorkflowSimulationResponse)
async def simulate_workflow(
    data: Workflow, current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> WorkflowSimulationResponse:
    """Dry-run and validate a workflow DAG topology before saving."""
    result = await studio_service.simulate_workflow(current_user, data)
    return WorkflowSimulationResponse(**result)


@router.post("/{id}/clone", response_model=WorkflowResponseDTO)
async def clone_workflow(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> Workflow:
    """Deep clone a workflow block securely via SSOT Service Layer."""
    return await studio_service.clone_workflow(current_user, id)


@router.put("/{id}", response_model=WorkflowResponseDTO)
async def save_workflow(
    id: str, data: Workflow, current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> Workflow:
    """Append or update a workflow definition block securely via SSOT Service Layer."""
    return await studio_service.save_workflow(current_user, id, data)


@router.delete("/{id}", response_model=WorkflowDeleteResponse)
async def delete_workflow(
    id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> WorkflowDeleteResponse:
    """Delete a workflow definition block securely via SSOT Service Layer."""
    try:
        await studio_service.delete_workflow(current_user, id)
        return WorkflowDeleteResponse(status="success", deleted_id=id)
    except Exception as e:
        if isinstance(e, AppException):
            raise
        logger.error(
            "[WorkflowsRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "target_id": id, "error": str(e)},
        )
        raise AppException(
            message="Internal delete failure",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
