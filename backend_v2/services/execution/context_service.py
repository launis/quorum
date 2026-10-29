"""Execution Context Service for retrieving frozen forensic snapshots."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from backend_v2.database.interfaces import IExecutionRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.services import storage
from backend_v2.services.file_driver import FileDriver

logger = logging.getLogger(__name__)

__all__ = ["ExecutionContextService"]


class ExecutionContextService:
    """Service handling frozen forensic context extraction and formatting.

    Attributes:
        exec_repo: Execution repository for retrieving persisted execution records.
        storage: File storage driver for reading offloaded context blobs.
    """

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        storage_driver: FileDriver | None = None,
        get_execution_fn: Callable[..., Awaitable[ExecutionRecord]] | None = None,
    ) -> None:
        """Initialize the execution context service with repository and storage dependencies.

        Args:
            exec_repo: Execution repository for fetching execution records.
            storage_driver: Optional file storage driver for reading offloaded artifacts.
            get_execution_fn: Optional custom callable to fetch and validate execution records.
        """
        self.exec_repo = exec_repo
        self.storage: FileDriver = storage_driver if storage_driver is not None else storage.get_storage_driver()
        self._get_execution = get_execution_fn if get_execution_fn is not None else self._default_get_execution

    async def _default_get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        """Fetch and authorize an execution record using default tenant isolation rules.

        Args:
            initiator: Authenticated user token claims.
            execution_id: Canonical Opaque Stripe ID of the target execution.

        Returns:
            Hydrated and authorized ExecutionRecord domain model.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks permission to view the execution (ErrorCodes.PERMISSION_DENIED).
        """
        record = await self.exec_repo.get_execution(execution_id, hydrate=True)
        if not record:
            logger.error(
                "[ExecutionContextService] %s: Execution '%s' not found",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                execution_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": execution_id},
            )
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)
        org_id = initiator.organization_id
        if initiator.role != "ROOT" and record.organization_id != org_id and record.created_by != initiator.id:
            logger.error(
                "[ExecutionContextService] %s: User '%s' denied access to execution '%s'",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                execution_id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value, "execution_id": execution_id},
            )
            raise PermissionDeniedError("You do not have permission to view this execution.")
        return record

    async def get_frozen_context_bytes(self, initiator: TokenData, execution_id: str) -> tuple[bytes, str]:
        """Retrieve and format the frozen forensic context JSON bytes for an execution.

        Args:
            initiator: Authenticated user token claims.
            execution_id: Canonical Opaque Stripe ID of the target execution.

        Returns:
            Tuple containing the UTF-8 encoded JSON bytes and the suggested download filename.

        Raises:
            ResourceNotFoundError: If the execution record does not exist (ErrorCodes.RESOURCE_NOT_FOUND).
            PermissionDeniedError: If the initiator lacks permission to view the execution (ErrorCodes.PERMISSION_DENIED).
            AppException: If reading or validating the offloaded context file from storage fails (ErrorCodes.RESOURCE_NOT_FOUND).
        """
        record = await self._get_execution(initiator=initiator, execution_id=execution_id)

        if record.frozen_context_storage_path:
            storage_drv = storage.get_storage_driver()
            try:
                raw_bytes = await storage_drv.read(record.frozen_context_storage_path)
                parsed_context = FrozenContext.model_validate_json(raw_bytes)
                pretty_bytes = parsed_context.model_dump_json(indent=2).encode("utf-8")
                return pretty_bytes, f"frozen_context_{execution_id}.json"
            except Exception as strg_err:
                logger.error(
                    "[ExecutionContextService] Failed to fetch frozen context from storage",
                    exc_info=True,
                    extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": execution_id},
                )
                raise AppException(
                    message="Forensic context file not found in storage",
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                ) from strg_err

        fc = record.frozen_context if record.frozen_context is not None else FrozenContext()
        frozen_json = fc.model_dump_json(indent=2)
        return frozen_json.encode("utf-8"), f"frozen_context_{execution_id}.json"
