import logging

from fastapi import APIRouter, BackgroundTasks, Query, status
from fastapi.responses import JSONResponse, Response

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
