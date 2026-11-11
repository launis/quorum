"""Admin Studio Task Briefs API Router.

Provides CRUD and clone endpoints for reusable human-facing TaskBrief entities.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Path, status

from backend_v2.api.dependencies import (
    CurrentUserDep,
    StudioTaskBriefServiceDep,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.dtos.studio import (
    TaskBriefDeleteResponse,
    TaskBriefResponseDTO,
)

logger = logging.getLogger(__name__)

__all__ = ["router"]

router = APIRouter(prefix="/task-briefs", tags=["Admin Studio V2 - Task Briefs"])


@router.get("/", response_model=list[TaskBriefResponseDTO])
async def get_task_briefs(
    current_user: CurrentUserDep,
    task_brief_service: StudioTaskBriefServiceDep,
) -> list[TaskBrief]:
    """Retrieve all TaskBrief records accessible to the authenticated tenant.

    Args:
        current_user: The authenticated user making the request.
        task_brief_service: The task brief service dependency.

    Returns:
        A list of accessible TaskBrief domain models.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if persisted records fail validation.
    """
    return await task_brief_service.list_task_briefs(current_user)


@router.post("/", response_model=TaskBriefResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_task_brief(
    current_user: CurrentUserDep,
    task_brief_service: StudioTaskBriefServiceDep,
) -> TaskBrief:
    """Create a new TaskBrief draft securely via the SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        task_brief_service: The task brief service dependency.

    Returns:
        The newly created TaskBrief draft.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the created draft cannot be reloaded.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant modification rights are violated.
    """
    return await task_brief_service.create_task_brief_draft(current_user)


@router.get("/{id}", response_model=TaskBriefResponseDTO)
async def get_task_brief(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    task_brief_service: StudioTaskBriefServiceDep,
) -> TaskBrief:
    """Retrieve a specific TaskBrief by its unique Opaque Stripe ID.

    Args:
        id: The unique tbr_<32_hex> identifier of the task brief.
        current_user: The authenticated user making the request.
        task_brief_service: The task brief service dependency.

    Returns:
        The requested TaskBrief domain model.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the task brief is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant access isolation is violated.
    """
    return await task_brief_service.get_task_brief(current_user, id)


@router.post("/{id}/clone", response_model=TaskBriefResponseDTO, status_code=status.HTTP_201_CREATED)
async def clone_task_brief(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    task_brief_service: StudioTaskBriefServiceDep,
) -> TaskBrief:
    """Deep clone an existing TaskBrief under a newly generated Opaque Stripe ID.

    Args:
        id: The unique tbr_<32_hex> identifier of the source task brief to clone.
        current_user: The authenticated user making the request.
        task_brief_service: The task brief service dependency.

    Returns:
        The newly cloned TaskBrief domain model.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the source task brief is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant access or modification rights are violated.
    """
    return await task_brief_service.clone_task_brief(current_user, id)


@router.put("/{id}", response_model=TaskBriefResponseDTO)
async def save_task_brief(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    data: TaskBrief,
    current_user: CurrentUserDep,
    task_brief_service: StudioTaskBriefServiceDep,
) -> TaskBrief:
    """Create or update a TaskBrief in-place under its authoritative ID.

    Args:
        id: The unique tbr_<32_hex> identifier of the task brief.
        data: The updated TaskBrief domain model payload.
        current_user: The authenticated user making the request.
        task_brief_service: The task brief service dependency.

    Returns:
        The saved TaskBrief domain model.

    Raises:
        AppException: With ErrorCodes.ID_MISMATCH if path id does not match payload id.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the task brief is not found after save.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant modification rights are violated.
    """
    if data.id != id:
        logger.error(
            "[TaskBriefsRouter] %s: Path id '%s' does not match payload id '%s' (Initiator: %s).",
            ErrorCodes.ID_MISMATCH.name,
            id,
            data.id,
            current_user.id,
            exc_info=True,
            extra={"error_code": ErrorCodes.ID_MISMATCH.value, "task_brief_id": id},
        )
        raise AppException(
            message=f"Path id '{id}' does not match payload id '{data.id}'",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.ID_MISMATCH.value},
        )

    return await task_brief_service.save_task_brief(current_user, id, data)


@router.delete("/{id}", response_model=TaskBriefDeleteResponse)
async def delete_task_brief(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    task_brief_service: StudioTaskBriefServiceDep,
) -> TaskBriefDeleteResponse:
    """Delete a TaskBrief by its unique Opaque Stripe ID.

    Args:
        id: The unique tbr_<32_hex> identifier of the task brief to delete.
        current_user: The authenticated user making the request.
        task_brief_service: The task brief service dependency.

    Returns:
        TaskBriefDeleteResponse confirming the deleted ID.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the task brief does not exist.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant modification rights are violated.
        AppException: With ErrorCodes.DELETE_BLOCKED_BY_USAGE if referenced by an assignment.
    """
    await task_brief_service.delete_task_brief(current_user, id)
    return TaskBriefDeleteResponse(status="deleted", deleted_id=id)
