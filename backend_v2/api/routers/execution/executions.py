import asyncio
import logging

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

from backend_v2.api.dependencies import ArqPoolDep, CurrentUserDep, ExecutionServiceDep
from backend_v2.models.v2_core import ExecutionCreate, ExecutionRecord, ExecutionStatus

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
    request: Request,
    arq_pool: ArqPoolDep,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionRecord:
    """Start an asynchronous workflow execution securely via SSOT.

    EAGER EXTRACTION PATTERN: Intercepts PDF Base64 strings, resolves them
    via PyMuPDF, and replaces them with Raw Text before Pydantic validation.
    """
    import base64

    import fitz
    from fastapi.concurrency import run_in_threadpool

    from backend_v2.exceptions import AppException

    def _extract_pdf(file_bytes: bytes) -> str:
        """Isolated CPU-bound PyMuPDF extraction."""
        import pymupdf4llm

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        md_text = str(pymupdf4llm.to_markdown(doc))
        doc.close()
        return md_text.strip()

    try:
        data = await request.json()
    except Exception as e:
        raise AppException(
            message="Invalid JSON payload",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": "VALIDATION_FAILED"},
        ) from e

    raw_inputs = data.get("raw_inputs", {})
    if isinstance(raw_inputs, dict):
        for key, val in raw_inputs.items():
            if isinstance(val, dict) and "content_base64" in val:
                filename = val.get("filename", "unknown.pdf").lower()
                try:
                    file_bytes = base64.b64decode(val["content_base64"])
                    if filename.endswith(".pdf"):
                        logger.info(
                            "[EagerExtraction] Found binary PDF %s. Extracting synchronously at Router.", filename
                        )
                        extracted = await run_in_threadpool(_extract_pdf, file_bytes)
                        # Destroy base64 blob, replace with string
                        raw_inputs[key] = extracted
                    else:
                        logger.info("[EagerExtraction] Found text file %s. Decoding.", filename)
                        raw_inputs[key] = file_bytes.decode("utf-8", errors="ignore")
                except Exception as e:
                    logger.error("[EagerExtraction] Failed to extract %s", filename, exc_info=True)
                    raise AppException(
                        message=f"Failed to extract text from {filename}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "FILE_EXTRACTION_FAILED"},
                    ) from e

    from pydantic import ValidationError

    try:
        payload = ExecutionCreate(**data)
    except ValidationError as e:
        raise AppException(
            message=f"Payload validation failed: {str(e)}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"error_code": "VALIDATION_FAILED", "errors": e.errors()},
        ) from e

    return await execution_service.start_execution(initiator=current_user, payload=payload, arq_pool=arq_pool)


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
    # 1. Authorize connection first
    await execution_service.get_execution(initiator=current_user, execution_id=execution_id)

    from collections.abc import AsyncGenerator

    async def event_generator() -> AsyncGenerator[str]:
        try:
            while True:
                # Poll database (Fallback from Redis Pub/Sub for simpler local portability)
                # In true production, this should attach to a Redis Pub/Sub channel.
                record = await execution_service.get_execution(initiator=current_user, execution_id=execution_id)

                # V2 Protocol Requirement: JSON Payload inside 'data: '
                yield f"data: {record.model_dump_json()}\n\n"

                if record.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                    break

                await asyncio.sleep(2)
        except Exception as e:
            logger.error("SSE Error for execution %s: %s", execution_id, str(e), exc_info=True)
            yield f'data: {{"error": "SSE Stream Interrupted: {str(e)}"}}\n\n'

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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
) -> Response:
    """Omni-channel render endpoint for an execution."""
    accept_language = request.headers.get("accept-language", None)

    content, media_type, filename = await execution_service.render_execution(
        initiator=current_user,
        execution_id=execution_id,
        format_type=format,
        profile_id=profile_id,
        accept_language=accept_language,
        arq_pool=arq_pool,
    )

    headers = {}
    if filename:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    if isinstance(content, (dict, list)):
        if isinstance(content, dict) and content.get("status") == "pending":
            return JSONResponse(content=content, status_code=status.HTTP_202_ACCEPTED)
        return JSONResponse(content=content)

    return Response(content=content, media_type=media_type, headers=headers)


class JobAcceptedDTO(BaseModel):
    status: str
    message: str
    execution_id: str


@router.post("/{execution_id}/render_pdf", response_model=JobAcceptedDTO, status_code=status.HTTP_202_ACCEPTED)
async def generate_pdf_async(
    request: Request,
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    arq_pool: ArqPoolDep,
    profile_id: str | None = Query(None),
) -> JobAcceptedDTO:
    """Omni-channel render endpoint for asynchronous PDF Generation via BackgroundWorker."""
    # 1. Authorize connection first via Security Dependency
    await execution_service.get_execution(initiator=current_user, execution_id=execution_id)

    # 2. Extract locale
    accept_language = request.headers.get("accept-language", None)

    # 3. Queue the background task into Redis
    await arq_pool.enqueue_job(
        "generate_pdf_job", execution_id=execution_id, accept_language=accept_language, profile_id=profile_id
    )

    # 4. Return 202 Accepted Fast
    return JobAcceptedDTO(status="Accepted", message="PDF Generation queued", execution_id=execution_id)


@router.delete("/{execution_id}/profiles/{profile_id}", status_code=status.HTTP_200_OK)
async def delete_profile_synthesis(
    execution_id: str,
    profile_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> dict[str, str]:
    """Clears the cached synthesis state for a specific profile.
    This forces the next render request to dispatch On-Demand Rendering.
    """
    await execution_service.clear_profile_synthesis(
        initiator=current_user, execution_id=execution_id, profile_id=profile_id
    )
    return {"status": "success", "message": "Profile synthesis cache cleared"}
