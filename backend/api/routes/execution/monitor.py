"""API Router for Execution Monitoring (GET and SSE)."""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, status
from sse_starlette.sse import EventSourceResponse

from backend.database.repository import AbstractWorkflowRepository
from backend.api.bff_transformer import AssessmentTransformer
from backend.dependencies import get_async_repository
from backend.exceptions import AppException, ResourceNotFoundError
from backend.logging_config import log_error
from backend.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Executions"])


from backend.api.schemas import ExecutionResponse

@router.get("/recent", summary="Get Recent Executions", response_model=list[ExecutionResponse])
async def get_recent_executions(
    limit: int = 10,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Get a list of recent executions."""
    try:
        user_id = current_user.uid if current_user else None
        executions = await repository.get_all_executions(user_id=user_id)

        def get_time(e):
            return e.get("started_at") or e.get("timestamp") or ""

        executions.sort(key=get_time, reverse=True)

        results = []
        for e in executions[:limit]:
            # Use DTO to normalize
            try:
                dto = ExecutionResponse.model_validate(e)
                results.append(dto)
            except Exception as validation_err:
                logger.warning(f"Skipping malformed execution in recent list: {validation_err}")
                continue

        return results

    except Exception as e:
        error_code = "EXECUTION_FETCH_FAILED"
        wrapped_error = AppException(
            message="Failed to fetch recent executions",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "original_error": str(e)},
        )
        log_error(logger, wrapped_error)
        raise wrapped_error from e


@router.get("/{execution_id}", summary="Get Execution Details", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Get execution details by ID. Returns standardized ExecutionResponse."""
    try:
        execution = await repository.get_execution(execution_id)

        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        # Normalize via DTO
        return ExecutionResponse.model_validate(execution)

    except ResourceNotFoundError as e:
        if "error_code" not in e.details:
            e.details["error_code"] = "EXECUTION_NOT_FOUND"
        log_error(logger, e)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": "EXECUTION_NOT_FOUND"}
        ) from e
    except Exception as e:
        error_code = "EXECUTION_FETCH_FAILED"
        wrapped = AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        )
        log_error(logger, wrapped)
        raise wrapped from e


@router.get("/{execution_id}/events", summary="Monitor Execution (SSE)")
async def monitor_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    view: str = "assessment",  # 'assessment' or 'raw'
):
    """Server-Sent Events alias for monitoring."""
    logger.info(f"[Monitor] Request for execution_id: {execution_id}, view: {view}")
    
    # Pre-check existence to fail fast with 404
    exists = await repository.get_execution(execution_id)
    if not exists:
         logger.warning(f"[Monitor] Execution {execution_id} NOT FOUND in repository.")
         raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

    # Fetch Workflow Definition (Strict SSOT)
    workflow_id = exists.get("workflow_id")
    workflow_definition = None
    if workflow_id:
        workflow_definition = await repository.get_workflow_definition(workflow_id)

    import asyncio
    import json
    from fastapi.encoders import jsonable_encoder

    async def event_generator():
        # Simple polling simulator for now to satisfy contract without Redis
        try:
             # Poll more frequently for smoother UI updates (1s is fine for local)
             for i in range(120): # Increased to 2 min timeout
                  exec_data = await repository.get_execution(execution_id)
                  if not exec_data:
                      yield {"event": "error", "data": "Execution not found"}
                      break
    
                  current_status = exec_data.get("status")
                  payload = ""
                  
                  if view == "raw":
                       # Option B: Explicit DTO Layer
                       # Normalize data using Pydantic Schema
                       try:
                           dto = ExecutionResponse.model_validate(exec_data)
                           payload = dto.model_dump_json(warnings=False)
                       except Exception as validation_err:
                           logger.error(f"[Monitor] DTO Validation Failed: {validation_err}")
                           # Fallback to rough dump if validation fails to keep stream alive?
                           # No, user requested NO fallbacks. But we should probably send error event.
                           yield {"event": "error", "data": f"Serialization Error: {validation_err}"}
                           break
                  else:
                      # Default: AssessmentTransformer for BFF (Frontend Compatibility)
                      try:
                          transformer = AssessmentTransformer(language="fi") # Default to Finnish for Monitoring
                          assessment_view = transformer.transform(exec_data, workflow_definition)
                          payload = assessment_view.model_dump_json()
                      except Exception as trans_err:
                            logger.error(f"[Monitor] Transformation Failed: {trans_err}")
                            yield {"event": "error", "data": "Transformation Failed"}
                            break

                  # logger.debug(f"[Monitor] Yielding update for {execution_id}. Payload len: {len(payload)}")
                  yield {"event": "update", "data": payload}
    
                  if current_status in ("completed", "failed", "cancelled", "rejected"):
                      logger.info(f"[Monitor] Execution {execution_id} finished ({current_status}). Closing stream.")
                      break
    
                  await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"[Monitor] Critical Generator Error: {e}", exc_info=True)
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())
