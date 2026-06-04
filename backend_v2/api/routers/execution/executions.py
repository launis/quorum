import logging

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse, Response, StreamingResponse

from backend_v2.api.dependencies import ArqPoolDep, CurrentUserDep, DocumentExtractionServiceDep, ExecutionServiceDep
from backend_v2.models.v2_core import ExecutionCreate, ExecutionRecord, JobAcceptedDTO

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get("/", response_model=list[ExecutionRecord])
async def list_executions(
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> list[ExecutionRecord]:
    """Retrieve all executions securely via SSOT."""
    return await execution_service.list_executions(initiator=current_user)


@router.post("/", response_model=ExecutionRecord, status_code=status.HTTP_202_ACCEPTED)
async def start_execution(
    payload: ExecutionCreate,
    arq_pool: ArqPoolDep,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    doc_service: DocumentExtractionServiceDep,
) -> ExecutionRecord:
    """Start an asynchronous workflow execution securely via SSOT."""
    return await execution_service.start_execution(
        initiator=current_user, payload=payload, arq_pool=arq_pool, doc_service=doc_service
    )


@router.get("/{execution_id}", response_model=ExecutionRecord)
async def get_execution_status(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionRecord:
    """Retrieve the current status and results of an execution securely via SSOT."""
    return await execution_service.get_execution(initiator=current_user, execution_id=execution_id)


@router.post("/{execution_id}/resume", response_model=ExecutionRecord, status_code=status.HTTP_202_ACCEPTED)
async def resume_execution(
    execution_id: str,
    arq_pool: ArqPoolDep,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionRecord:
    """Resume a failed execution securely via SSOT."""
    return await execution_service.resume_execution(
        initiator=current_user, execution_id=execution_id, arq_pool=arq_pool
    )


@router.get("/{execution_id}/stream")
async def stream_execution_status(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> StreamingResponse:
    """Stream execution status and results securely via Sever-Sent Events (SSE)."""
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
    """Delete an execution securely via SSOT."""
    await execution_service.delete_execution(initiator=current_user, execution_id=execution_id)


@router.get("/{execution_id}/frozen_context")
async def download_frozen_context(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> Response:
    """Download the forensic frozen context JSON for an execution."""
    content, filename = await execution_service.get_frozen_context_bytes(
        initiator=current_user, execution_id=execution_id
    )
    return Response(
        content=content,
        media_type="application/json",
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
    """Omni-channel render endpoint for an execution."""
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

    if isinstance(content, (dict, list)):
        if isinstance(content, dict) and "status" in content and content["status"] == "pending":
            return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)
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
    """Omni-channel render endpoint for asynchronous PDF Generation via BackgroundWorker."""
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

    # 4. Return 202 Accepted Fast
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
    """
    await execution_service.clear_profile_synthesis(
        initiator=current_user, execution_id=execution_id, profile_id=profile_id
    )
