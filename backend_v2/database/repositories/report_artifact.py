"""Repository implementation for Report Artifacts.

Governs materialized report outputs, metadata, storage references, and CRUD persistence
targeting the 'report_artifacts' collection in strict compliance with Tripartite Pipeline Architecture.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from backend_v2.database.driver import Filter, StorageDriver
from backend_v2.database.interfaces import IReportArtifactRepository
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import ReportArtifactUpdateDTO

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "report_artifacts"


class ReportArtifactRepositoryImpl(BaseRepository, IReportArtifactRepository):
    """Repository implementation for ReportArtifact domain entities."""

    def __init__(self, driver: StorageDriver):
        """Initializes the repository with a storage driver.

        Args:
            driver: The underlying storage driver for database operations.
        """
        super().__init__(driver)

    async def create_report_artifact(self, report: ReportArtifact) -> ReportArtifact:
        """Persists a new report artifact domain record.

        Args:
            report: The ReportArtifact domain entity to persist.

        Returns:
            The persisted ReportArtifact model.

        Raises:
            AppException: If database persistence fails.
        """
        payload = report.model_dump(mode="json")
        await self.driver.upsert(_COLLECTION_NAME, payload, report.id)
        return report

    async def get_report_artifact(self, report_id: str) -> ReportArtifact | None:
        """Retrieves a report artifact by its unique identifier.

        Args:
            report_id: Unique identifier prefixed with 'rep_'.

        Returns:
            The validated ReportArtifact if found, otherwise None.

        Raises:
            AppException: If document validation or retrieval fails.
        """
        doc = await self.driver.get(_COLLECTION_NAME, report_id)
        if doc is None:
            return None
        try:
            return ReportArtifact.model_validate(doc, strict=False)
        except Exception as e:
            logger.error("Failed to parse ReportArtifact %s: %s", report_id, e, extra={"report_id": report_id})
            raise AppException(
                message=f"Failed to parse report artifact {report_id}",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def list_report_artifacts_by_execution(self, execution_id: str) -> list[ReportArtifact]:
        """Lists all report artifacts associated with an analytical execution run.

        Args:
            execution_id: Parent execution ID.

        Returns:
            List of validated ReportArtifact instances.

        Raises:
            AppException: If document validation or query fails.
        """
        docs = await self.driver.query(_COLLECTION_NAME, [Filter("execution_id", "==", execution_id)])
        results: list[ReportArtifact] = []
        for doc in docs:
            try:
                results.append(ReportArtifact.model_validate(doc, strict=False))
            except Exception as e:
                logger.error(
                    "Failed to parse ReportArtifact for execution %s: %s",
                    execution_id,
                    e,
                    extra={"execution_id": execution_id},
                )
                raise AppException(
                    message=f"Failed to parse report artifact for execution {execution_id}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return results

    async def update_report_artifact(self, report_id: str, update_dto: ReportArtifactUpdateDTO) -> ReportArtifact:
        """Applies in-place field updates to an existing report artifact.

        Args:
            report_id: Unique identifier prefixed with 'rep_'.
            update_dto: Strongly typed update DTO with optional fields.

        Returns:
            The updated ReportArtifact model.

        Raises:
            AppException: If the record does not exist or persistence fails.
        """
        doc = await self.driver.get(_COLLECTION_NAME, report_id)
        if doc is None:
            logger.error("Report artifact %s not found for update", report_id, extra={"report_id": report_id})
            raise AppException(
                message=f"Report artifact {report_id} not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        current = ReportArtifact.model_validate(doc, strict=False)
        update_dict: dict[str, Any] = {}
        if update_dto.status is not None:
            update_dict["status"] = update_dto.status
        if update_dto.storage_paths is not None:
            update_dict["storage_paths"] = update_dto.storage_paths
        if update_dto.metadata is not None:
            update_dict["metadata"] = update_dto.metadata
        if update_dto.error_message is not None:
            update_dict["error_message"] = update_dto.error_message

        update_dict["updated_at"] = datetime.now(UTC)
        updated = current.model_copy(update=update_dict)
        payload = updated.model_dump(mode="json")
        await self.driver.upsert(_COLLECTION_NAME, payload, report_id)
        return updated

    async def delete_report_artifact(self, report_id: str) -> bool:
        """Deletes a report artifact record by its identifier.

        Args:
            report_id: Unique identifier prefixed with 'rep_'.

        Returns:
            True if deletion succeeded, False otherwise.

        Raises:
            AppException: If deletion operation fails.
        """
        return await self.driver.delete(_COLLECTION_NAME, report_id)
