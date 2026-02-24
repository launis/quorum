"""API Router for Execution Artifacts (PDFs, Downloads)."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import FileResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse

from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import get_arq_pool, get_async_repository, get_storage_service_dep
from backend.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend.logging_config import log_error
from backend.models.auth import TokenData, UserRole
from backend.models.dtos.execution import (
    PDFCancelResponse,
    PDFDownloadCheckResponse,
    PDFQueuedResponse,
)
from backend.services.auth import AuthService
from backend.services.drivers.local_file_driver import LocalFileDriver
from backend.services.file_driver import FileDriver

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Executions"])


def _enforce_pdf_access(user: TokenData, execution: dict[str, Any]) -> None:
    """Enforces strict RBAC for PDF access."""
    if user.role == UserRole.ROOT:
        return

    if user.role == UserRole.ADMIN:
        # Admins are allowed to view reports (Debugging/Audit)
        return

    if user.role == UserRole.MANAGER:
        exec_org = execution.get("organization_id")
        user_org = user.organization_id
        if exec_org != user_org:
            raise AppException(
                message="Managers can only access executions within their organization.",
                status_code=status.HTTP_403_FORBIDDEN,
                details={"error_code": "ORG_MISMATCH", "exec_org": exec_org, "user_org": user_org},
            )
        return

    exec_user = execution.get("user_id")
    if str(exec_user) != str(user.id):
        raise AppException(
            message="You do not have permission to access this execution.",
            status_code=status.HTTP_403_FORBIDDEN,
            details={"error_code": "OWNERSHIP_REQUIRED"},
        )


@router.get(
    "/{execution_id}/pdf/download",
    summary="Download Execution PDF",
    description="Securely download the PDF report. Enqueues generation if missing.",
    response_model=PDFDownloadCheckResponse | PDFQueuedResponse | None,
)
async def download_execution_pdf(
    execution_id: str,
    check_local: bool = False,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: TokenData = Depends(AuthService.get_current_user()),
    arq_pool: Any = Depends(get_arq_pool),
    storage: FileDriver = Depends(get_storage_service_dep),
):
    """Download PDF, Queue Generation, or Check Local Existence."""
    try:
        # 1. Fetch & Check Access
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution {execution_id} not found")

        from pydantic import BaseModel
        exec_data: dict[str, Any] = execution.model_dump() if isinstance(execution, BaseModel) else dict(execution) if isinstance(execution, dict) else {}
        _enforce_pdf_access(current_user, exec_data)

        # 2. Check File
        rel_path = f"executions/{execution_id}/report.pdf"

        if await storage.exists(rel_path):
            if check_local:
                # Return JSON with local path if available
                # Use LocalFileDriver check
                local_path = None
                if isinstance(storage, LocalFileDriver):
                    local_path = str(storage.base_path / rel_path)

                return PDFDownloadCheckResponse(status="ready", exists=True, local_path=local_path)

            if isinstance(storage, LocalFileDriver):
                full_path = storage.base_path / rel_path
                return FileResponse(
                    path=full_path,
                    filename=f"report_{execution_id}.pdf",
                    media_type="application/pdf",
                    content_disposition_type="attachment",
                )
            else:
                content = await storage.read(rel_path)
                from fastapi.responses import Response

                return Response(
                    content=content,
                    media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="report_{execution_id}.pdf"'},
                )

        # If check_local is true but file missing
        if check_local:
            return PDFDownloadCheckResponse(status="missing", exists=False, local_path=None)

        # 3. Queue Job if missing
        if arq_pool:
            await arq_pool.enqueue_job("generate_pdf_job", execution_id=execution_id)

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content=PDFQueuedResponse(
                    status="accepted", message="PDF generation queued."
                ).model_dump(),  # JSONResponse expects dict/list
            )
        else:
            raise AppException(
                message="Background worker unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                details={"error_code": "WORKER_UNAVAILABLE"},
            )

    except AppException:
        raise
    except Exception as e:
        error_code = ErrorCodes.PDF_DOWNLOAD_FAILED
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code}
        ) from e


@router.get(
    "/{execution_id}/pdf/progress",
    summary="Track PDF Generation Progress",
    description="Server-Sent Events (SSE) for PDF generation progress.",
)
async def get_pdf_progress(
    request: Request,
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: TokenData = Depends(AuthService.get_current_user()),
    arq_pool: Any = Depends(get_arq_pool),
):
    """SSE Endpoint for Progress."""
    try:
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution {execution_id} not found")

        from pydantic import BaseModel
        exec_data: dict[str, Any] = execution.model_dump() if isinstance(execution, BaseModel) else dict(execution) if isinstance(execution, dict) else {}
        _enforce_pdf_access(current_user, exec_data)

        async def event_generator():
            import asyncio
            import json

            # Using ارq pool as redis client proxy if available
            # Ideally depends(get_redis_client) but keeping scope small
            if not arq_pool:
                yield {"data": json.dumps({"error": "Worker unavailable"})}
                return

            redis = arq_pool
            key = f"progress:{execution_id}:pdf_gen"

            while True:
                if await request.is_disconnected():
                    break

                try:
                    data_raw = await redis.get(key)
                except Exception:
                    # Redis might expose different interface on Arq pool depending on version
                    # Fallback or assume error
                    data_raw = None

                if data_raw:
                    yield {"data": data_raw}

                    try:
                        data = json.loads(data_raw)
                        if data.get("progress") >= 1.0 or data.get("progress") < 0:
                            break
                    except Exception:
                        pass
                else:
                    yield {"data": json.dumps({"progress": 0.0, "message": "Waiting for worker..."})}

                await asyncio.sleep(0.5)

        return EventSourceResponse(event_generator())

    except Exception as e:
        log_error(logger, e)
        raise AppException(str(e), 500) from e


@router.delete(
    "/{execution_id}/pdf/cancel",
    summary="Cancel PDF Generation",
    description="Cancels the download process and cleans up files.",
    response_model=PDFCancelResponse,
)
async def cancel_pdf_generation(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: TokenData = Depends(AuthService.get_current_user()),
    storage: FileDriver = Depends(get_storage_service_dep),
) -> PDFCancelResponse:
    """Cancel endpoint (Clean up)."""
    try:
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution {execution_id} not found")

        from pydantic import BaseModel
        exec_data: dict[str, Any] = execution.model_dump() if isinstance(execution, BaseModel) else dict(execution) if isinstance(execution, dict) else {}
        _enforce_pdf_access(current_user, exec_data)

        # Depends on get_storage_client usually, but here we instantiate fresh if needed or reuse?
        # Actually it's cleaner to depend on get_storage_service_dep like the download endpoint
        # The storage dependency was added to args above.

        rel_path = f"executions/{execution_id}/report.pdf"

        # Safe delete via driver
        await storage.delete(rel_path)

        return PDFCancelResponse(status="success", message="PDF cancelled and file removed.")

    except Exception as e:
        log_error(logger, e)
        raise AppException(str(e), 500) from e
