"""Execution Stream Service for Server-Sent Events (SSE) status streaming."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable

from backend_v2.database.interfaces import IExecutionRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
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
        """Initialize the execution stream service with repository dependencies.

        Args:
            exec_repo: Execution repository for fetching state snapshots.
            get_execution_fn: Optional custom callable to fetch and validate execution records.
        """
        self.exec_repo = exec_repo
        self._get_execution = get_execution_fn or self._default_get_execution

    async def _default_get_execution(
        self,
        initiator: TokenData,
        execution_id: str,
        hydrate: bool = False,
        skip_resumability: bool = True,
    ) -> ExecutionRecord:
        """Default internal execution resolver validating existence and tenant permissions.

        Args:
            initiator: Authenticated user token claims.
            execution_id: Canonical Opaque Stripe ID of the execution.
            hydrate: Whether to hydrate offloaded blobs.
            skip_resumability: Whether to skip resumability checking.

        Returns:
            Validated ExecutionRecord.

        Raises:
            ResourceNotFoundError: If the execution does not exist.
            PermissionDeniedError: If initiator lacks access.
        """
        record = await self.exec_repo.get_execution(execution_id, hydrate=hydrate)
        if not record:
            logger.error(
                "[ExecutionStreamService] %s: Execution '%s' not found",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                execution_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        org_id = initiator.organization_id
        if initiator.role != "ROOT" and record.organization_id != org_id and record.created_by != initiator.id:
            logger.error(
                "[ExecutionStreamService] %s: User '%s' denied access to execution '%s'",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                execution_id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("You do not have permission to access this execution.")
        return record

    async def stream_status(self, initiator: TokenData, execution_id: str) -> AsyncGenerator[str]:
        r"""Stream execution status and results securely via Server-Sent Events (SSE).

        Args:
            initiator: Authenticated user token claims.
            execution_id: Canonical Opaque Stripe ID of the target execution.

        Yields:
            Formatted SSE text event frames (`data: {...}\n\n` or `event: error\ndata: {...}\n\n`).

        Raises:
            ResourceNotFoundError: If the execution does not exist on initial preflight check.
            PermissionDeniedError: If initiator lacks access to the execution on preflight.
        """
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

                await asyncio.sleep(settings.sse_polling_interval_seconds)
            except ResourceNotFoundError as e:
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                retry_count += 1
                if retry_count <= max_retries:
                    logger.warning(
                        "Transient ResourceNotFoundError polling execution %s (attempt %d/%d): %s",
                        execution_id,
                        retry_count,
                        max_retries,
                        str(e),
                    )
                    await asyncio.sleep(settings.sse_polling_interval_seconds)
                    continue

                logger.error(
                    "[ExecutionStreamService] %s: Exceeded retry count for %s: %s",
                    ErrorCodes.INTERNAL_SERVER_ERROR.name,
                    execution_id,
                    str(e),
                    exc_info=True,
                    extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                )
                err_data = json.dumps(
                    {"error": f"Execution interrupted: {str(e)}", "error_code": "SSE_STREAM_INTERRUPTED"}
                )
                yield f"event: error\ndata: {err_data}\n\n"
                break
            except (AppException, OSError, RuntimeError, ValueError) as e:
                if isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                logger.error(
                    "[ExecutionStreamService] %s: SSE Error for execution %s: %s",
                    ErrorCodes.INTERNAL_SERVER_ERROR.name,
                    execution_id,
                    str(e),
                    exc_info=True,
                    extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                )
                err_data = json.dumps(
                    {"error": f"Execution interrupted: {str(e)}", "error_code": "SSE_STREAM_INTERRUPTED"}
                )
                yield f"event: error\ndata: {err_data}\n\n"
                break
