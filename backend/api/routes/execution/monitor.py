"""API Router for Execution Monitoring (GET and SSE)."""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, status
from sse_starlette.sse import EventSourceResponse

from backend.database.repository import AbstractWorkflowRepository
from backend.dependencies import get_async_repository
from backend.exceptions import AppException, ResourceNotFoundError
from backend.logging_config import log_error
from backend.services.auth import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get("/recent", summary="Get Recent Executions", response_model=list[dict[str, Any]])
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
            item = e.copy()
            if "execution_id" not in item and "id" in item:
                item["execution_id"] = item["id"]

            if "start_time" not in item:
                item["start_time"] = (
                    item.get("started_at") or item.get("timestamp") or datetime.now(timezone.utc)
                )

            if "results" in item and "result" not in item:
                item["result"] = item["results"]
            if "result" not in item:
                item["result"] = {}

            results.append(item)

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


@router.get("/{execution_id}", summary="Get Execution Details", response_model=dict[str, Any])
async def get_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
    current_user: Any = Depends(AuthService.get_current_user()),
):
    """Get execution details by ID."""
    try:
        execution = await repository.get_execution(execution_id)

        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

        item = execution.copy()
        if "execution_id" not in item and "id" in item:
            item["execution_id"] = item["id"]

        if "start_time" not in item:
            item["start_time"] = (
                item.get("started_at") or item.get("timestamp") or datetime.now(timezone.utc)
            )

        if "results" in item and "result" not in item:
            item["result"] = item["results"]
        if "result" not in item:
            item["result"] = {}

        return item

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
):
    """Server-Sent Events alias for monitoring."""
    logger.info(f"[Monitor] Request for execution_id: {execution_id}")
    
    # Pre-check existence to fail fast with 404
    exists = await repository.get_execution(execution_id)
    if not exists:
         logger.warning(f"[Monitor] Execution {execution_id} NOT FOUND in repository.")
         # Debug: List recent to see if it's there
         recent = await repository.get_all_executions()
         ids = [e.get("id") for e in recent]
         logger.info(f"[Monitor] available IDs: {ids}")
         raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")

    # Placeholder for SSE logic. Using basic polling fallback via client for now, or real SSE if implemented.
    # As per instructions, "Ensure SSE stream setup".
    # Since we don't have Redis PubSub implementation details in scope, we return 501 or basic stream.
    # Returning basic stream that yields once current status?

    import asyncio
    import json
    from fastapi.encoders import jsonable_encoder

    async def event_generator():
        # Simple polling simulator for now to satisfy contract without Redis
        # In prod, this listens to Redis channel
        cached_status = None
        
        try:
             # Poll more frequently for smoother UI updates (1s is fine for local)
             for i in range(120): # Increased to 2 min timeout
                  exec_data = await repository.get_execution(execution_id)
                  if not exec_data:
                      logger.error(f"[Monitor] Execution {execution_id} disappeared during polling!")
                      yield {"event": "error", "data": "Execution not found"}
                      break
    
                  # Yield full data if status changed OR every X ticks?
                  # For progress bar, we want updates even if status is 'running' but step changed.
                  # Ideally check hash or modified time. 
                  # For now, yield every time or check content change.
                  
                  # Simplify: Yield every second if running, or if status changed.
                  current_status = exec_data.get("status")
                  
                  # Map fields for Frontend compatibility (matches views.py logic)
                  formatted_data = exec_data.copy()
                  if "execution_id" not in formatted_data and "id" in formatted_data:
                      formatted_data["execution_id"] = formatted_data["id"]
                  
                  if "start_time" not in formatted_data:
                      formatted_data["start_time"] = (
                          formatted_data.get("started_at") or formatted_data.get("timestamp") or datetime.now(timezone.utc)
                      )

                  # Ensure result is mapped (Fix for Flutter client expecting 'result')
                  if "results" in formatted_data and "result" not in formatted_data:
                      formatted_data["result"] = formatted_data["results"]
                  if "result" not in formatted_data:
                      formatted_data["result"] = {}
    
                  # Serialize properly
                  try:
                      payload = json.dumps(jsonable_encoder(formatted_data))
                  except Exception as ser_err:
                        logger.error(f"[Monitor] Serialization Failed: {ser_err}")
                        yield {"event": "error", "data": "Serialization Failed"}
                        break

                  logger.info(f"[Monitor] Yielding update for {execution_id}. Payload len: {len(payload)}")
                  yield {"event": "update", "data": payload}
    
                  if current_status in ("completed", "failed", "cancelled", "rejected"):
                      # Send one last update then close? 
                      # Or keep open? Browser auto-reconnects on close.
                      # Let's verify we sent the 'completed' state then break.
                      logger.info(f"[Monitor] Execution {execution_id} finished ({current_status}). Closing stream.")
                      break
    
                  await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"[Monitor] Critical Generator Error: {e}", exc_info=True)
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())
