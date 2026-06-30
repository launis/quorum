"""Execution API Routers.

Provides the endpoints for managing asynchronous workflow executions,
including starting, resuming, tracking, and rendering results.
"""

import logging

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse, Response, StreamingResponse

from backend_v2.api.dependencies import ArqPoolDep, CurrentUserDep, DocumentExtractionServiceDep, ExecutionServiceDep
from backend_v2.models.v2_core import (
    EvidenceRejectionRequest,
    ExecutionCreate,
    ExecutionRecord,
    HumanOverrideRequest,
    JobAcceptedDTO,
)

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
        AppException: If fetching executions fails or permission is denied.
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
        AppException: If validation fails, quota exceeded, or permission denied.
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
        AppException: If the execution is not found or permission denied.
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
        AppException: If unresumable state, quota exceeded, or not found.
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
    """Stream execution status and results securely via Sever-Sent Events (SSE).

    Args:
        execution_id: The unique identifier of the execution.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        A StreamingResponse emitting SSE events.

    Raises:
        AppException: If the execution is not found or permission denied.
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
        AppException: If deletion fails or permission is denied.
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
        AppException: If the file is not found or permission is denied.
    """
    content, filename = await execution_service.get_frozen_context_bytes(
        initiator=current_user, execution_id=execution_id
    )
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{execution_id}/export")
async def download_execution_export(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> Response:
    """Download the forensic execution export as an Excel file.

    Args:
        execution_id: The unique identifier of the execution.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Returns:
        A Response containing the Excel file.

    Raises:
        AppException: If the file is not found or permission is denied.
    """
    content, filename = await execution_service.get_execution_export_bytes(
        initiator=current_user, execution_id=execution_id
    )
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{execution_id}/render")
async def render_execution(
    request: Request,
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    arq_pool: ArqPoolDep,
    format: str = Query("json", description="Output format: json, pdf, or flat"),
    profile_id: str | None = Query(None, description="The output profile to render"),
    custom_preface_md: str | None = Query(None, description="Custom preface markdown"),
    local_time_str: str | None = Query(None, description="Localized time string"),
) -> Response:
    """Omni-channel render endpoint for an execution.

    Args:
        request: The FastAPI request object.
        execution_id: The unique identifier of the execution.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.
        arq_pool: The Arq Redis connection pool.
        format: The desired output format (e.g., json, pdf, flat).
        profile_id: The identifier of the output profile to use.
        custom_preface_md: Optional custom preface content in Markdown.
        local_time_str: Optional localized time string for rendering.

    Returns:
        A Response object appropriately typed based on the format requested.

    Raises:
        AppException: If rendering fails, format is unsupported, or permission denied.
    """
    accept_language = request.headers.get("accept-language")

    content, media_type, filename = await execution_service.render_execution(
        initiator=current_user,
        execution_id=execution_id,
        format_type=format,
        profile_id=profile_id,
        accept_language=accept_language,
        arq_pool=arq_pool,
        custom_preface_md=custom_preface_md,
        local_time_str=local_time_str,
    )

    headers = {}
    if filename:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    if isinstance(content, JobAcceptedDTO):
        return JSONResponse(content=content.model_dump(mode="json"), status_code=status.HTTP_202_ACCEPTED)

    if isinstance(content, (dict, list)):
        return JSONResponse(content=content)

    return Response(content=content, media_type=media_type, headers=headers)


@router.post("/{execution_id}/render_pdf", response_model=JobAcceptedDTO, status_code=status.HTTP_202_ACCEPTED)
async def generate_pdf_async(
    request: Request,
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    arq_pool: ArqPoolDep,
    profile_id: str | None = Query(None),
    custom_preface_md: str | None = Query(None, description="Custom preface markdown"),
    local_time_str: str | None = Query(None, description="Localized time string"),
) -> JobAcceptedDTO:
    """Omni-channel render endpoint for asynchronous PDF Generation via BackgroundWorker.

    Args:
        request: The FastAPI request object.
        execution_id: The unique identifier of the execution.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.
        arq_pool: The Arq Redis connection pool.
        profile_id: The identifier of the output profile.
        custom_preface_md: Optional custom preface content in Markdown.
        local_time_str: Optional localized time string.

    Returns:
        A JobAcceptedDTO indicating the PDF generation has been queued.

    Raises:
        AppException: If queuing fails or permission is denied.
    """
    accept_language = request.headers.get("accept-language", None)
    prof_id = profile_id or "default"

    await execution_service.enqueue_pdf_generation(
        initiator=current_user,
        execution_id=execution_id,
        accept_language=accept_language,
        profile_id=prof_id,
        arq_pool=arq_pool,
        custom_preface_md=custom_preface_md,
        local_time_str=local_time_str,
    )

    return JobAcceptedDTO(status="Accepted", message="PDF Generation queued", execution_id=execution_id)


@router.delete("/{execution_id}/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_synthesis(
    execution_id: str,
    profile_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> None:
    """Clears the cached synthesis state for a specific profile.

    This forces the next render request to dispatch On-Demand Rendering.

    Args:
        execution_id: The unique identifier of the execution.
        profile_id: The specific profile identifier to clear.
        current_user: The authenticated user making the request.
        execution_service: The execution domain service.

    Raises:
        AppException: If the execution is not found or permission is denied.
    """
    await execution_service.clear_profile_synthesis(
        initiator=current_user, execution_id=execution_id, profile_id=profile_id
    )


@router.patch("/{execution_id}/atoms/{atom_id}/override", status_code=status.HTTP_200_OK)
async def override_atom(
    execution_id: str,
    atom_id: str,
    payload: HumanOverrideRequest,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> dict[str, str]:
    """Apply a human override to a scorecard atom."""
    await execution_service.override_atom(
        initiator=current_user,
        execution_id=execution_id,
        atom_id=atom_id,
        payload=payload,
    )
    return {"status": "ok", "message": "Atom overridden and execution recalculated successfully."}


@router.put("/{execution_id}/evidence/{evq_id}/reject", status_code=status.HTTP_200_OK)
async def reject_evidence_quote(
    execution_id: str,
    evq_id: str,
    payload: EvidenceRejectionRequest,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> dict[str, str]:
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
        AppException: If rejection fails or permission is denied.
    """
    await execution_service.reject_evidence_quote(
        initiator=current_user,
        execution_id=execution_id,
        evq_id=evq_id,
        reason=payload.rejection_reason,
    )
    return {"status": "ok", "message": "Evidence quote rejected successfully."}
