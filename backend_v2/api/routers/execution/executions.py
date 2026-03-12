import asyncio
import logging

from fastapi import APIRouter, BackgroundTasks, Query, status
from fastapi.responses import JSONResponse, Response, StreamingResponse

from backend_v2.api.dependencies import CurrentUserDep, ExecutionServiceDep, RepoDep
from backend_v2.exceptions import AppException, ErrorCodes
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
    payload: ExecutionCreate,
    background_tasks: BackgroundTasks,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionRecord:
    """Start an asynchronous workflow execution securely via SSOT."""
    return await execution_service.start_execution(
        initiator=current_user,
        payload=payload,
        background_tasks=background_tasks
    )


@router.get("/{execution_id}", response_model=ExecutionRecord)
async def get_execution_status(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionRecord:
    """Retrieve the current status and results of an execution securely via SSOT."""
    return await execution_service.get_execution(initiator=current_user, execution_id=execution_id)


@router.get("/{execution_id}/stream")
async def stream_execution_status(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> StreamingResponse:
    """Stream execution status and results securely via Sever-Sent Events (SSE)."""
    # 1. Authorize connection first
    await execution_service.get_execution(initiator=current_user, execution_id=execution_id)

    async def event_generator():
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
            logger.error(f"SSE Error for execution {execution_id}: {e}")
            yield f"data: {{\"error\": \"SSE Stream Interrupted: {str(e)}\"}}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> None:
    """Delete an execution securely via SSOT."""
    await execution_service.delete_execution(initiator=current_user, execution_id=execution_id)


@router.get("/{execution_id}/render")
async def render_execution(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    repository: RepoDep,
    format: str = Query("json", description="Output format: json, pdf, or flat"),
) -> Response:
    """Omni-channel render endpoint for an execution."""
    # 1. Fetch securely using the user context
    execution = await execution_service.get_execution(initiator=current_user, execution_id=execution_id)

    if execution.status != ExecutionStatus.COMPLETED:
        logger.error(f"[ExecutionRouter] {ErrorCodes.VALIDATION_FAILED.name}: Error: Execution is not in COMPLETED state.")
        raise AppException(
            message=f"Execution is not in COMPLETED state. Current status: {execution.status.value}",
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    # 2. Render based on requested format
    fmt = format.lower()

    if fmt == "json":
        # Native V2 strict Pydantic dump
        return JSONResponse(content=execution.model_dump(mode="json"))

    elif fmt == "flat":
        from backend_v2.services.flattener import FlatFileService
        flat_data = FlatFileService.flatten_results(execution)
        return JSONResponse(content=flat_data)

    elif fmt == "pdf":
        from backend_v2.services.pdf_generator import PdfReportService
        # Passing repository inside PDF generator is safe as the execution was already authorized above
        pdf_service = PdfReportService(repository)
        pdf_bytes = await pdf_service.generate_execution_pdf(execution_id)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="execution_{execution_id}.pdf"'
            }
        )

    else:
        logger.error(f"[ExecutionRouter] {ErrorCodes.VALIDATION_FAILED.name}: Error: Unsupported format: {format}")
        raise AppException(
            message=f"Unsupported format: {format}",
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
