"""Execution Stream Service for Server-Sent Events (SSE) status streaming."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable

import backend_v2.services.execution as execution
from backend_v2.database.interfaces import IExecutionRepository
from backend_v2.exceptions import AppException, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.enums import ExecutionStatus
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["ExecutionStreamService"]


class ExecutionStreamService:
    """Service streaming execution progress and state mutations via SSE."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        get_execution_fn: Callable[..., Awaitable[ExecutionRecord]] | None = None,
    ) -> None:
        self.exec_repo = exec_repo
        self._get_execution = get_execution_fn or self._default_get_execution

    async def _default_get_execution(
        self,
        initiator: TokenData,
        execution_id: str,
        hydrate: bool = False,
        skip_resumability: bool = True,
    ) -> ExecutionRecord:
        record = await self.exec_repo.get_execution(execution_id, hydrate=hydrate)
        if not record:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        org_id = initiator.organization_id
        if initiator.role != "ROOT" and record.organization_id != org_id and record.created_by != initiator.id:
            raise PermissionDeniedError("You do not have permission to access this execution.")
        return record

    async def stream_status(self, initiator: TokenData, execution_id: str) -> AsyncGenerator[str]:
        """Stream execution status and results securely via Server-Sent Events (SSE)."""
        await self._get_execution(initiator=initiator, execution_id=execution_id)

        settings = get_settings()
        retry_count = 0
        max_retries = settings.sse_max_transient_retries

        while True:
            try:
                record = await self._get_execution(
                    initiator=initiator,
                    execution_id=execution_id,
                    hydrate=False,
                    skip_resumability=True,
                )
                retry_count = 0
                yield f"data: {record.model_dump_json(exclude_none=True)}\n\n"

                if record.status in [ExecutionStatus.PASSED, ExecutionStatus.FAILED]:
                    break

                await execution.asyncio.sleep(settings.sse_polling_interval_seconds)
            except ResourceNotFoundError as e:
                retry_count += 1
                if retry_count <= max_retries:
                    logger.warning(
                        "Transient ResourceNotFoundError polling execution %s (attempt %d/%d): %s",
                        execution_id,
                        retry_count,
                        max_retries,
                        str(e),
                    )
                    await execution.asyncio.sleep(settings.sse_polling_interval_seconds)
                    continue

                logger.error("Exceeded retry count for %s: %s", execution_id, str(e), exc_info=True)
                err_data = json.dumps(
                    {"error": f"Execution interrupted: {str(e)}", "error_code": "SSE_STREAM_INTERRUPTED"}
                )
                yield f"event: error\ndata: {err_data}\n\n"
                break
            except (AppException, OSError, RuntimeError, ValueError) as e:
                logger.error("SSE Error for execution %s: %s", execution_id, str(e), exc_info=True)
                err_data = json.dumps(
                    {"error": f"Execution interrupted: {str(e)}", "error_code": "SSE_STREAM_INTERRUPTED"}
                )
                yield f"event: error\ndata: {err_data}\n\n"
                break
