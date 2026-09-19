"""Execution Lifecycle Service for listing, fetching, and cascade deleting executions."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable

from backend_v2.database.interfaces import IExecutionRepository, IReportArtifactRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.services import storage
from backend_v2.services.execution.resumption_service import ExecutionResumptionService
from backend_v2.services.file_driver import FileDriver

logger = logging.getLogger(__name__)

__all__ = ["ExecutionLifecycleService"]


class ExecutionLifecycleService:
    """Service managing tenant-isolated execution lifecycle operations."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        resumption_service: ExecutionResumptionService | None = None,
        storage_driver: FileDriver | None = None,
        report_repo: IReportArtifactRepository | None = None,
        check_resumability_fn: Callable[..., Awaitable[bool]] | None = None,
    ) -> None:
        self.exec_repo = exec_repo
        self.resumption_service = resumption_service
        self.storage: FileDriver = storage_driver if storage_driver is not None else storage.get_storage_driver()
        self.report_repo = report_repo
        self._check_resumability = check_resumability_fn or (
            resumption_service.check_resumability if resumption_service else None
        )

    async def list_executions(self, initiator: TokenData) -> list[ExecutionRecord]:
        """Fetch executions securely based on Tenant/Role."""
        try:
            executions = await self.exec_repo.get_all_executions()

            if initiator.role != "ROOT":
                org_id = initiator.organization_id
                executions = [e for e in executions if e.organization_id == org_id or e.created_by == initiator.id]

            if self._check_resumability:
                check_fn = self._check_resumability

                async def _eval(rec: ExecutionRecord) -> bool:
                    return await check_fn(rec)

                async with asyncio.TaskGroup() as tg:
                    tasks: list[asyncio.Task[bool]] = [tg.create_task(_eval(e)) for e in executions]
                return [
                    e.model_copy(update={"is_resumable": t.result()}) for e, t in zip(executions, tasks, strict=True)
                ]

            return executions
        except Exception as e:
            msg = f"Failed to list executions: {str(e)}"
            logger.error(
                "[ExecutionLifecycleService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True
            )
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
            ) from e

    async def get_execution(
        self,
        initiator: TokenData,
        execution_id: str,
        hydrate: bool = True,
        skip_resumability: bool = False,
    ) -> ExecutionRecord:
        """Fetch single execution securely with tenant validation."""
        data = await self.exec_repo.get_execution(execution_id, hydrate=hydrate)
        if not data:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        org_id = initiator.organization_id
        if initiator.role != "ROOT" and data.organization_id != org_id and data.created_by != initiator.id:
            raise PermissionDeniedError("You do not have permission to view this execution.")

        if skip_resumability or not self._check_resumability:
            return data

        is_resumable = await self._check_resumability(data)
        return data.model_copy(update={"is_resumable": is_resumable})

    async def delete_execution(self, initiator: TokenData, execution_id: str) -> bool:
        """Securely delete an execution and cascade clean its report artifacts and storage."""
        record = await self.exec_repo.get_execution(execution_id, hydrate=False)
        if not record:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        org_id = initiator.organization_id
        if initiator.role != "ROOT" and record.organization_id != org_id and record.created_by != initiator.id:
            raise PermissionDeniedError("You do not have permission to delete this execution.")

        try:
            # REQ-19 Cascade deletion: delete all associated ReportArtifact records and files
            if self.report_repo is not None:
                try:
                    reports = await self.report_repo.list_report_artifacts_by_execution(execution_id)
                    for report in reports:
                        if report.storage_paths:
                            for p in (
                                report.storage_paths.pdf_path,
                                report.storage_paths.sdui_json_path,
                                report.storage_paths.excel_path,
                                report.storage_paths.csv_path,
                            ):
                                if p:
                                    with contextlib.suppress(Exception):
                                        await self.storage.delete(p)
                        await self.report_repo.delete_report_artifact(report.id)
                except Exception as cascade_err:
                    logger.warning(
                        "[ExecutionLifecycleService] Report cascade cleanup non-fatal error: %s", cascade_err
                    )

            # Clean up all offloaded blobs and directory files using just-in-time storage resolution
            storage_drv = storage.get_storage_driver()
            try:
                await storage_drv.delete_directory(f"executions/{execution_id}")
            except AppException as e:
                if e.status_code != 404:
                    msg = f"Failed to clean up directory executions/{execution_id} during deletion."
                    logger.error(
                        "[ExecutionLifecycleService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True
                    )
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                    ) from e
            except Exception as e:
                msg = f"Failed to clean up directory executions/{execution_id} during deletion."
                logger.error(
                    "[ExecutionLifecycleService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True
                )
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                ) from e

            return await self.exec_repo.delete_execution(execution_id)
        except Exception as e:
            msg = f"Failed to delete execution {execution_id}: {str(e)}"
            logger.error(
                "[ExecutionLifecycleService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True
            )
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
            ) from e
