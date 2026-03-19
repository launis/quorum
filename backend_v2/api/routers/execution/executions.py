import asyncio
import logging

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse, Response, StreamingResponse

from backend_v2.api.dependencies import ArqPoolDep, CurrentUserDep, ExecutionServiceDep, RepoDep
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
    arq_pool: ArqPoolDep,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> ExecutionRecord:
    """Start an asynchronous workflow execution securely via SSOT."""
    return await execution_service.start_execution(
        initiator=current_user,
        payload=payload,
        arq_pool=arq_pool
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


@router.get("/{execution_id}/frozen_context")
async def download_frozen_context(
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
) -> Response:
    """Download the forensic frozen context JSON for an execution."""
    execution = await execution_service.get_execution(initiator=current_user, execution_id=execution_id)
    
    if execution.frozen_context_storage_path:
        from backend_v2.services.storage import get_storage_driver
        import json
        
        storage = get_storage_driver()
        try:
            raw_bytes = await storage.read(execution.frozen_context_storage_path)
            
            # Dynamically pretty-print the historic minified JSON blob
            parsed_data = json.loads(raw_bytes.decode('utf-8'))
            pretty_bytes = json.dumps(parsed_data, indent=2, ensure_ascii=False).encode('utf-8')
            
            return Response(
                content=pretty_bytes,
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="frozen_context_{execution_id}.json"'
                }
            )
        except Exception as strg_err:
            logger.warning(f"Failed to fetch frozen context from storage: {strg_err}")
            raise AppException(message="Forensic context file not found in storage", status_code=404, details={"error_code": ErrorCodes.NOT_FOUND.value})
            
    # Fallback to returning the embedded frozen context if not offloaded
    frozen_json = execution.frozen_context.model_dump_json(indent=2)
    return Response(
        content=frozen_json,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="frozen_context_{execution_id}.json"'
        }
    )


@router.get("/{execution_id}/render")
async def render_execution(
    request: Request,
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
        msg = f"Execution is not in COMPLETED state. Current status: {execution.status.value}"
        logger.error(f"[ExecutionRouter] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    # 2. Render based on requested format
    fmt = format.lower()

    if fmt == "json":
        from backend_v2.services.blueprint import BlueprintTransformer
        accept_language = request.headers.get("accept-language", None)
        # We pass execution_id as Transformer fetches again, or we could pass execution natively.
        transformer = BlueprintTransformer(repository)
        payload = await transformer.build_render_payload(execution_id, accept_language)
        return JSONResponse(content=payload)

    elif fmt == "flat":
        from backend_v2.services.flattener import FlatFileService
        flat_data = FlatFileService.flatten_results(execution)
        return JSONResponse(content=flat_data)

    elif fmt == "pdf":
        # 1. First check if async worker has already generated and offloaded the PDF
        if execution.pdf_report_path:
            from backend_v2.services.storage import get_storage_driver
            storage = get_storage_driver()
            try:
                pdf_bytes = await storage.read(execution.pdf_report_path)
                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="execution_{execution_id}.pdf"'
                    }
                )
            except Exception as strg_err:
                logger.warning(f"Failed to fetch pre-generated PDF from storage, falling back to sync generation: {strg_err}")

        # 2. Fallback to Synchronous generation if not yet ready
        from backend_v2.services.blueprint import BlueprintTransformer
        from backend_v2.services.pdf_generator import PdfReportService
        
        accept_language = request.headers.get("accept-language", None)
        if not accept_language and execution.metadata:
            accept_language = execution.metadata.get("target_locale")
            
        transformer = BlueprintTransformer(repository)
        blueprint_payload = await transformer.build_render_payload(execution_id, accept_language)
        
        # Passing repository inside PDF generator is safe as the execution was authorized
        pdf_service = PdfReportService(repository)
        pdf_bytes = await pdf_service.generate_execution_pdf(execution_id, blueprint_payload=blueprint_payload)

        # Self-Healing Mechanism: Save the newly generated PDF back to persistent storage
        try:
            from backend_v2.services.storage import get_storage_driver
            storage = get_storage_driver()
            output_path_rel = f"executions/{execution_id}/report.pdf"
            saved_path = await storage.save(output_path_rel, pdf_bytes)
            if not execution.pdf_report_path or execution.pdf_report_path != saved_path:
                await repository.update_execution(execution_id, {"pdf_report_path": saved_path})
            logger.info(f"[ExecutionRouter] Self-healed missing PDF for {execution_id} to {saved_path}")
        except Exception as heal_err:
            logger.warning(f"[ExecutionRouter] Failed to self-heal PDF storage for {execution_id}: {heal_err}")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="execution_{execution_id}.pdf"'
            }
        )

    else:
        msg = f"Unsupported format: {format}"
        logger.error(f"[ExecutionRouter] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

@router.post("/{execution_id}/render_pdf", status_code=status.HTTP_202_ACCEPTED)
async def generate_pdf_async(
    request: Request,
    execution_id: str,
    current_user: CurrentUserDep,
    execution_service: ExecutionServiceDep,
    arq_pool: ArqPoolDep,
) -> dict[str, str]:
    """Omni-channel render endpoint for asynchronous PDF Generation via BackgroundWorker."""
    # 1. Authorize connection first via Security Dependency
    await execution_service.get_execution(initiator=current_user, execution_id=execution_id)

    # 2. Extract locale
    accept_language = request.headers.get("accept-language", None)

    # 3. Queue the background task into Redis
    await arq_pool.enqueue_job("generate_pdf_job", execution_id=execution_id, accept_language=accept_language)

    # 4. Return 202 Accepted Fast
    return {"status": "Accepted", "message": "PDF Generation queued", "execution_id": execution_id}
