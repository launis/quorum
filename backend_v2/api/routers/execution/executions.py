"""Execution API Routers.

Provides the endpoints for managing asynchronous workflow executions,
including starting, resuming, and tracking execution lifecycle.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, status
from fastapi.responses import Response, StreamingResponse

from backend_v2.api.dependencies import (
    ArqPoolDep,
    CurrentUserDep,
    DocumentExtractionServiceDep,
    ExecutionServiceDep,
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
