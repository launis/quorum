"""Execution API Routers.

Provides the endpoints for managing asynchronous workflow executions,
including starting, resuming, and tracking execution lifecycle.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response, StreamingResponse

from backend_v2.api.dependencies import (
    ArqPoolDep,
    CurrentUserDep,
    DocumentExtractionServiceDep,
    ExecutionServiceDep,
    require_role,
)
from backend_v2.models.auth import (
    ExecutionAssignmentBatchCreateDTO,
    ExecutionAssignmentBatchResponseDTO,
    ExecutionAssignmentCreateDTO,
    ExecutionAssignmentDraftDTO,
    ExecutionAssignmentOnboardingRequestDTO,
    ExecutionAssignmentPreviewDTO,
    ExecutionAssignmentResponseDTO,
    ExecutionAssignmentSubmitDTO,
    TokenData,
    TokenExchangeResponseDTO,
    UserRole,
)
from backend_v2.models.domain.execution import (
    EvidenceRejectionRequest,
    ExecutionCreate,
    ExecutionRecord,
)
from backend_v2.models.dtos.base import GenericStatusResponseDTO
from backend_v2.models.dtos.matrix_scorecard import HumanOverrideRequest

__all__ = ["router"]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Executions"])
ManagerOrAdminDep = Annotated[
    TokenData,
    Depends(require_role([UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER])),
]


@router.get("/", response_model=list[ExecutionRecord])
async def list_executions(
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> list[ExecutionRecord]:
    """Retrieve all executions securely via SSOT.

    Args:
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        A list of execution records accessible by the user.

    Raises:
        AppException: If repository lookup or resumability evaluation fails
            (ErrorCodes.INTERNAL_SERVER_ERROR).
    """
    return await execution_service.list_executions(initiator=current_user)


@router.post("/", response_model=ExecutionRecord, status_code=status.HTTP_202_ACCEPTED)
async def start_execution(
    payload: ExecutionCreate,
    arq_pool: ArqPoolDep,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    doc_service: DocumentExtractionServiceDep,
) -> ExecutionRecord:
    """Start an asynchronous workflow execution securely via SSOT.

    Args:
        payload: The execution creation payload containing workflow ID and inputs.
        arq_pool: The Arq Redis connection pool for background tasks.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.
        doc_service: Document extraction service for eager extraction.

    Returns:
        The newly created execution record in a pending/running state.

    Raises:
        ResourceNotFoundError: If workflow, profile, or model registry does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the initiator lacks access to the workflow
            (ErrorCodes.PERMISSION_DENIED).
        ConfigurationError: If a referenced step or prompt block blueprint is missing
            (ErrorCodes.CONFIGURATION_ERROR).
        AppException: If quota is exceeded (ErrorCodes.RATE_LIMIT_EXCEEDED), input or
            profile validation fails (ErrorCodes.VALIDATION_FAILED), or a required
            repository dependency is missing (ErrorCodes.SERVICE_DEPENDENCY_MISSING).
    """
    return await execution_service.start_execution(
        initiator=current_user, payload=payload, arq_pool=arq_pool, doc_service=doc_service
    )


@router.get("/assignments", response_model=list[ExecutionAssignmentResponseDTO])
async def list_execution_assignments(
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> list[ExecutionAssignmentResponseDTO]:
    """List workflow execution assignments scoped to the authenticated user.

    Args:
        current_user: Authenticated caller token data.
        execution_service: Execution domain service.

    Returns:
        List of ExecutionAssignmentResponseDTO accessible to the caller.

    Raises:
        AppException: If assignment repository dependency is missing
            (ErrorCodes.SERVICE_DEPENDENCY_MISSING).
    """
    return await execution_service.list_assignments(initiator=current_user)


@router.post(
    "/assignments",
    response_model=ExecutionAssignmentResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_execution_assignment(
    payload: ExecutionAssignmentCreateDTO,
    current_user: ManagerOrAdminDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionAssignmentResponseDTO:
    """Create a single time-bound workflow execution assignment.

    Args:
        payload: Validated ExecutionAssignmentCreateDTO.
        current_user: Authenticated ROOT, ADMIN, or MANAGER caller.
        execution_service: Execution domain service.

    Returns:
        Created ExecutionAssignmentResponseDTO.

    Raises:
        PermissionDeniedError: If caller lacks assignment privileges
            (ErrorCodes.PERMISSION_DENIED).
        ResourceNotFoundError: If workflow or organization does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        AppException: If workflow input key partitioning or email dispatch fails
            (ErrorCodes.VALIDATION_FAILED, ErrorCodes.EMAIL_DELIVERY_FAILED).
    """
    return await execution_service.create_assignment(initiator=current_user, payload=payload)


@router.post(
    "/assignments/batch",
    response_model=ExecutionAssignmentBatchResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_execution_assignment_batch(
    payload: ExecutionAssignmentBatchCreateDTO,
    current_user: ManagerOrAdminDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionAssignmentBatchResponseDTO:
    """Create a cohort batch of time-bound workflow execution assignments.

    Args:
        payload: Validated ExecutionAssignmentBatchCreateDTO (1 to 500 recipients).
        current_user: Authenticated ROOT, ADMIN, or MANAGER caller.
        execution_service: Execution domain service.

    Returns:
        ExecutionAssignmentBatchResponseDTO with batch_id and created assignments.

    Raises:
        PermissionDeniedError: If caller lacks assignment privileges
            (ErrorCodes.PERMISSION_DENIED).
        ResourceNotFoundError: If workflow or organization does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        AppException: If duplicate emails, input partitioning, or email delivery fails
            (ErrorCodes.VALIDATION_FAILED, ErrorCodes.EMAIL_DELIVERY_FAILED).
    """
    return await execution_service.create_assignment_batch(initiator=current_user, payload=payload)


@router.get("/assignments/preview", response_model=ExecutionAssignmentPreviewDTO)
async def preview_execution_assignment(
    token: Annotated[str, Query(min_length=10)],
    execution_service: ExecutionServiceDep,
) -> ExecutionAssignmentPreviewDTO:
    """Perform a SafeLinks-immune side-effect-free preview of a task assignment.

    Args:
        token: Raw single-use assignment token from query string.
        execution_service: Execution domain service.

    Returns:
        ExecutionAssignmentPreviewDTO with masked email and deadline metadata.

    Raises:
        ResourceNotFoundError: If the assignment token hash does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        AppException: If the assignment is expired or revoked
            (ErrorCodes.TASK_ASSIGNMENT_EXPIRED).
    """
    return await execution_service.preview_assignment(raw_token=token)


@router.post("/assignments/onboard", response_model=TokenExchangeResponseDTO)
async def onboard_execution_assignee(
    token: Annotated[str, Query(min_length=10)],
    payload: ExecutionAssignmentOnboardingRequestDTO,
    execution_service: ExecutionServiceDep,
) -> TokenExchangeResponseDTO:
    """Execute combined Just-In-Time (JIT) user onboarding + 2FA for a task assignee.

    Args:
        token: Raw single-use assignment token from query string.
        payload: Onboarding request DTO with Firebase ID token and display name.
        execution_service: Execution domain service.

    Returns:
        TokenExchangeResponseDTO containing a signed 15-minute Quorum Local JWT.

    Raises:
        ResourceNotFoundError: If the assignment token hash does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If Firebase email does not match assignee_email
            (ErrorCodes.ASSIGNEE_EMAIL_MISMATCH) or 2FA is not enrolled
            (ErrorCodes.MFA_REQUIRED).
        AppException: If the assignment is expired
            (ErrorCodes.TASK_ASSIGNMENT_EXPIRED).
    """
    return await execution_service.onboard_assignee(raw_token=token, payload=payload)


@router.post(
    "/assignments/{assignment_id}/resend",
    response_model=ExecutionAssignmentResponseDTO,
)
async def resend_execution_assignment_email(
    assignment_id: str,
    current_user: ManagerOrAdminDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionAssignmentResponseDTO:
    """Rotate the 256-bit assignment token and resend the task magic-link email.

    Args:
        assignment_id: Canonical Task Assignment ID (tsk_<hex32>).
        current_user: Authenticated ROOT, ADMIN, or MANAGER caller.
        execution_service: Execution domain service.

    Returns:
        Updated ExecutionAssignmentResponseDTO.

    Raises:
        PermissionDeniedError: If caller lacks assignment management rights
            (ErrorCodes.PERMISSION_DENIED).
        ResourceNotFoundError: If assignment does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        AppException: If assignment is already submitted or revoked
            (ErrorCodes.VALIDATION_FAILED).
    """
    return await execution_service.resend_assignment_email(
        initiator=current_user,
        assignment_id=assignment_id,
    )


@router.post(
    "/assignments/{assignment_id}/activate",
    response_model=ExecutionAssignmentResponseDTO,
)
async def activate_execution_assignment(
    assignment_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionAssignmentResponseDTO:
    """Explicitly activate a task assignment and start its relative countdown timer.

    Args:
        assignment_id: Canonical Task Assignment ID (tsk_<hex32>).
        current_user: Authenticated assignee token data.
        execution_service: Execution domain service.

    Returns:
        Activated ExecutionAssignmentResponseDTO.

    Raises:
        PermissionDeniedError: If caller is not the assigned user
            (ErrorCodes.PERMISSION_DENIED).
        ResourceNotFoundError: If assignment does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        AppException: If assignment is expired or in an invalid state
            (ErrorCodes.TASK_ASSIGNMENT_EXPIRED, ErrorCodes.VALIDATION_FAILED).
    """
    return await execution_service.activate_assignment(
        initiator=current_user,
        assignment_id=assignment_id,
    )


@router.put(
    "/assignments/{assignment_id}/draft",
    response_model=ExecutionAssignmentResponseDTO,
)
async def save_execution_assignment_draft(
    assignment_id: str,
    payload: ExecutionAssignmentDraftDTO,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionAssignmentResponseDTO:
    """Auto-save assignee draft inputs on an active task assignment.

    Args:
        assignment_id: Canonical Task Assignment ID (tsk_<hex32>).
        payload: Draft inputs DTO.
        current_user: Authenticated assignee token data.
        execution_service: Execution domain service.

    Returns:
        Updated ExecutionAssignmentResponseDTO with persisted draft_inputs.

    Raises:
        PermissionDeniedError: If caller is not the assigned user or attempts to
            mutate locked_inputs (ErrorCodes.PERMISSION_DENIED).
        ResourceNotFoundError: If assignment does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        AppException: If assignment has expired or is already submitted
            (ErrorCodes.TASK_ASSIGNMENT_EXPIRED, ErrorCodes.TASK_ASSIGNMENT_ALREADY_SUBMITTED).
    """
    return await execution_service.save_draft_inputs(
        initiator=current_user,
        assignment_id=assignment_id,
        payload=payload,
    )


@router.post(
    "/assignments/{assignment_id}/submit",
    response_model=ExecutionRecord,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_execution_assignment(
    assignment_id: str,
    payload: ExecutionAssignmentSubmitDTO,
    arq_pool: ArqPoolDep,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    doc_service: DocumentExtractionServiceDep,
) -> ExecutionRecord:
    """Submit a time-bound task assignment and trigger single-shot workflow execution.

    Args:
        assignment_id: Canonical Task Assignment ID (tsk_<hex32>).
        payload: Submitted assignee inputs DTO.
        arq_pool: Arq Redis connection pool.
        current_user: Authenticated assignee token data.
        execution_service: Execution domain service.
        doc_service: Document extraction service.

    Returns:
        Initialized ExecutionRecord.

    Raises:
        PermissionDeniedError: If caller is not the assigned user or attempts to
            mutate locked_inputs (ErrorCodes.PERMISSION_DENIED).
        ResourceNotFoundError: If assignment does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        AppException: If assignment is already submitted or expired
            (ErrorCodes.TASK_ASSIGNMENT_ALREADY_SUBMITTED, ErrorCodes.TASK_ASSIGNMENT_EXPIRED).
    """
    return await execution_service.submit_assignment(
        initiator=current_user,
        assignment_id=assignment_id,
        payload=payload,
        arq_pool=arq_pool,
        doc_service=doc_service,
    )


@router.get("/{execution_id}", response_model=ExecutionRecord)
async def get_execution_status(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionRecord:
    """Retrieve the current status and results of an execution securely via SSOT.

    Args:
        execution_id: The unique identifier of the execution.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        The requested execution record.

    Raises:
        ResourceNotFoundError: If the execution record does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the initiator lacks access to the execution
            (ErrorCodes.PERMISSION_DENIED).
    """
    return await execution_service.get_execution(initiator=current_user, execution_id=execution_id)


@router.post("/{execution_id}/resume", response_model=ExecutionRecord, status_code=status.HTTP_202_ACCEPTED)
async def resume_execution(
    execution_id: str,
    arq_pool: ArqPoolDep,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionRecord:
    """Resume a failed execution securely via SSOT.

    Args:
        execution_id: The unique identifier of the failed execution.
        arq_pool: The Arq Redis connection pool.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        The resumed execution record in a running state.

    Raises:
        ResourceNotFoundError: If the execution record does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the initiator lacks access to the execution
            (ErrorCodes.PERMISSION_DENIED).
        AppException: If the execution state is unresumable
            (ErrorCodes.UNRESUMABLE_STATE_ERROR) or organization quota is exceeded
            (ErrorCodes.RATE_LIMIT_EXCEEDED).
    """
    return await execution_service.resume_execution(
        initiator=current_user, execution_id=execution_id, arq_pool=arq_pool
    )


@router.get("/{execution_id}/stream")
async def stream_execution_status(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> StreamingResponse:
    """Stream execution status and results securely via Server-Sent Events (SSE).

    Args:
        execution_id: The unique identifier of the execution.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        A StreamingResponse emitting SSE events.

    Raises:
        ResourceNotFoundError: If the execution record does not exist on preflight check
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the initiator lacks access to the execution on preflight
            check (ErrorCodes.PERMISSION_DENIED).
    """
    return StreamingResponse(
        execution_service.stream_status(initiator=current_user, execution_id=execution_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> None:
    """Delete an execution securely via SSOT.

    Args:
        execution_id: The unique identifier of the execution to delete.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Raises:
        ResourceNotFoundError: If the execution record does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the initiator lacks deletion rights
            (ErrorCodes.PERMISSION_DENIED).
        AppException: If cascading storage or repository deletion fails
            (ErrorCodes.INTERNAL_SERVER_ERROR).
    """
    await execution_service.delete_execution(initiator=current_user, execution_id=execution_id)


@router.get("/{execution_id}/frozen_context")
async def download_frozen_context(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> Response:
    """Download the forensic frozen context JSON for an execution.

    Args:
        execution_id: The unique identifier of the execution.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        A Response containing the frozen context file.

    Raises:
        ResourceNotFoundError: If the execution record does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the initiator lacks access to the execution
            (ErrorCodes.PERMISSION_DENIED).
        AppException: If reading the offloaded frozen context blob from storage fails
            (ErrorCodes.RESOURCE_NOT_FOUND).
    """
    content, filename = await execution_service.get_frozen_context_bytes(
        initiator=current_user, execution_id=execution_id
    )
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{execution_id}/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_synthesis(
    execution_id: str,
    profile_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> None:
    """Clear the cached synthesis state for a specific profile.

    Args:
        execution_id: The unique identifier of the execution.
        profile_id: The specific profile identifier to clear.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Raises:
        ResourceNotFoundError: If the execution or workflow record does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the initiator lacks access to the execution
            (ErrorCodes.PERMISSION_DENIED).
        AppException: If deleting the cached PDF report blob fails
            (ErrorCodes.INTERNAL_SERVER_ERROR).
    """
    await execution_service.clear_profile_synthesis(
        initiator=current_user, execution_id=execution_id, profile_id=profile_id
    )


@router.patch(
    "/{execution_id}/atoms/{atom_id}/override",
    response_model=GenericStatusResponseDTO,
    status_code=status.HTTP_200_OK,
)
async def override_atom(
    execution_id: str,
    atom_id: str,
    payload: HumanOverrideRequest,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> GenericStatusResponseDTO:
    """Apply a human override to a scorecard atom.

    Args:
        execution_id: The unique identifier of the execution.
        atom_id: The opaque identifier of the atom to override.
        payload: The human override request payload containing the reason and new status.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        A success message indicating the atom was overridden and the execution recalculated.

    Raises:
        ResourceNotFoundError: If the execution record does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the initiator lacks permission to modify the execution
            (ErrorCodes.PERMISSION_DENIED).
        AppException: If the target atom is not found (ErrorCodes.RESOURCE_NOT_FOUND) or
            required repositories are missing (ErrorCodes.CONFIGURATION_ERROR).
    """
    await execution_service.override_atom(
        initiator=current_user,
        execution_id=execution_id,
        atom_id=atom_id,
        payload=payload,
    )
    return GenericStatusResponseDTO(status="ok", message="Atom overridden and execution recalculated successfully.")


@router.put(
    "/{execution_id}/evidence/{evq_id}/reject",
    response_model=GenericStatusResponseDTO,
    status_code=status.HTTP_200_OK,
)
async def reject_evidence_quote(
    execution_id: str,
    evq_id: str,
    payload: EvidenceRejectionRequest,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> GenericStatusResponseDTO:
    """Reject an evidence quote and soft delete it from the synthesis.

    Args:
        execution_id: The unique identifier of the execution.
        evq_id: The opaque evidence quote ID.
        payload: The rejection request payload containing the reason.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        A success message.

    Raises:
        ResourceNotFoundError: If the execution record does not exist
            (ErrorCodes.RESOURCE_NOT_FOUND).
        PermissionDeniedError: If the initiator lacks permission to modify the execution
            (ErrorCodes.PERMISSION_DENIED).
    """
    await execution_service.reject_evidence_quote(
        initiator=current_user,
        execution_id=execution_id,
        evq_id=evq_id,
        reason=payload.rejection_reason,
    )
    return GenericStatusResponseDTO(status="ok", message="Evidence quote rejected successfully.")
