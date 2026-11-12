"""Repository implementation for Report Artifacts.

Governs materialized report outputs, metadata, storage references, and CRUD persistence
targeting the 'report_artifacts' table via EntityPersistencePort.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from backend_v2.database.interfaces import IReportArtifactRepository, UnitOfWorkFactory
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import ReportArtifactUpdateDTO

logger = logging.getLogger(__name__)

__all__ = ["ReportArtifactRepositoryImpl"]


class ReportArtifactRepositoryImpl(BaseRepository, IReportArtifactRepository):
    """Repository implementation for ReportArtifact domain entities."""

    def __init__(self, uow_factory: UnitOfWorkFactory | None = None) -> None:
        """Initialize the repository with an optional UnitOfWorkFactory."""
        super().__init__(uow_factory)

    async def create_report_artifact(self, report: ReportArtifact) -> ReportArtifact:
        """Persist a new report artifact domain record.

        Args:
            report: Validated ReportArtifact domain entity to persist.

        Returns:
            Persisted ReportArtifact model.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if persistence fails.
        """
        async with self._acquire_entities() as entities:
            await entities.upsert_report_artifact(report)
        return report

    async def get_report_artifact(self, report_id: str) -> ReportArtifact | None:
        """Retrieve a report artifact by its canonical identifier.

        Args:
            report_id: Canonical rep_<hex32> identifier.

        Returns:
            Validated ReportArtifact if found, otherwise None.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on hydration/query failure.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_report_artifact(report_id)

    async def list_report_artifacts_by_execution(self, execution_id: str) -> list[ReportArtifact]:
        """List all report artifacts associated with an analytical execution run.

        Args:
            execution_id: Parent canonical exe_<hex32> execution identifier.

        Returns:
            List of validated ReportArtifact instances ordered newest first.

        Raises:
            AppException: With VALIDATION_FAILED or STORAGE_ACCESS_FAILED on hydration/query failure.
        """
        async with self._acquire_entities() as entities:
            return await entities.list_report_artifacts_by_execution(execution_id)

    async def update_report_artifact(self, report_id: str, update_dto: ReportArtifactUpdateDTO) -> ReportArtifact:
        """Apply in-place field updates to an existing report artifact.

        Args:
            report_id: Canonical rep_<hex32> identifier.
            update_dto: Validated ReportArtifactUpdateDTO carrying updated fields.

        Returns:
            Updated ReportArtifact model.

        Raises:
            AppException: With RESOURCE_NOT_FOUND (HTTP 404) if missing, or STORAGE_ACCESS_FAILED on write failure.
        """
        async with self._acquire_entities() as entities:
            current = await entities.get_report_artifact(report_id)
            if current is None:
                logger.error(
                    "[ReportArtifactRepository] %s: Report artifact %s not found for update",
                    ErrorCodes.RESOURCE_NOT_FOUND.name,
                    report_id,
                    extra={"report_id": report_id, "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                )
                raise AppException(
                    message=f"Report artifact {report_id} not found",
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                )

            next_status = current.status
            if update_dto.status is not None:
                next_status = update_dto.status
            next_paths = current.storage_paths
            if update_dto.storage_paths is not None:
                next_paths = update_dto.storage_paths
            next_metadata = current.metadata
            if update_dto.metadata is not None:
                next_metadata = update_dto.metadata
            next_error = current.error_message
            if update_dto.error_message is not None:
                next_error = update_dto.error_message

            updated = ReportArtifact(
                id=current.id,
                execution_id=current.execution_id,
                workflow_id=current.workflow_id,
                profile_id=current.profile_id,
                locale=current.locale,
                title=current.title,
                status=next_status,
                storage_paths=next_paths,
                metadata=next_metadata,
                custom_preface_md=current.custom_preface_md,
                error_message=next_error,
                created_at=current.created_at,
                updated_at=datetime.now(UTC),
            )
            await entities.upsert_report_artifact(updated)
            return updated

    async def delete_report_artifact(self, report_id: str) -> bool:
        """Delete a report artifact record by its identifier.

        Args:
            report_id: Canonical rep_<hex32> identifier.

        Returns:
            True if deletion succeeded, False otherwise.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if deletion fails.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_report_artifact(report_id)
