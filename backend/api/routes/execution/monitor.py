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


@router.get("/{execution_id}/monitor", summary="Monitor Execution (SSE)")
async def monitor_execution(
    execution_id: str,
    repository: AbstractWorkflowRepository = Depends(get_async_repository),
):
    """Server-Sent Events alias for monitoring."""
    # Placeholder for SSE logic. Using basic polling fallback via client for now, or real SSE if implemented.
    # As per instructions, "Ensure SSE stream setup".
    # Since we don't have Redis PubSub implementation details in scope, we return 501 or basic stream.
    # Returning basic stream that yields once current status?

    import asyncio

    async def event_generator():
        # Simple polling simulator for now to satisfy contract without Redis
        # In prod, this listens to Redis channel
        last_status = None
        for _ in range(60): # 1 min timeout
             exec_data = await repository.get_execution(execution_id)
             if not exec_data:
                 yield {"event": "error", "data": "Execution not found"}
                 break

             status = exec_data.get("status")
             if status != last_status:
                 yield {"event": "status_change", "data": status}
                 last_status = status

             if status in ("completed", "failed", "cancelled"):
                 yield {"event": "scanned_update", "data": "done"} # Signal to client
                 break

             await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
