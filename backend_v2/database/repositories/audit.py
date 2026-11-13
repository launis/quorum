"""Database repository implementation module for append-only Audit Logs and FinOps Usage Data."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from backend_v2.database.interfaces import UnitOfWorkFactory
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.domain.base import (
    AuditLogCreateDTO,
    AuditLogRecord,
    DetailedUsageDTO,
    UsageRecord,
    UsageRollupSummaryDTO,
)
from backend_v2.models.domain.execution import ExecutionRecord

logger = logging.getLogger(__name__)

__all__ = ["AuditRepositoryImpl"]


class AuditRepositoryImpl(BaseRepository):
    """Repository implementation routing AuditLogRecord and UsageRecord operations through EntityPersistencePort."""

    def __init__(self, uow_factory: UnitOfWorkFactory | None = None) -> None:
        """Initialize the repository with an optional UnitOfWorkFactory.

        Args:
            uow_factory: Optional explicit UnitOfWorkFactory override.
        """
        super().__init__(uow_factory)

    @staticmethod
    def _parse_since_iso(since: str | None) -> datetime | None:
        """Parse an optional ISO 8601 timestamp string into a UTC-aware datetime.

        Args:
            since: Optional ISO 8601 timestamp string.

        Returns:
            Parsed UTC-aware datetime instance, or None when since is omitted.

        Raises:
            AppException: With VALIDATION_FAILED (HTTP 400) if since is malformed.
        """
        if not since:
            return None
        try:
            parsed = datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError as exc:
            msg = f"Invalid date format '{since}': {exc}"
            logger.error(
                "[AuditRepository] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "since": since},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "since": since},
            ) from exc
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed

    async def log_audit_event(self, event_data: AuditLogCreateDTO) -> None:
        """Insert a compliance audit event into the append-only audit_logs table.

        Args:
            event_data: Validated AuditLogCreateDTO describing the compliance event.

        Raises:
            AppException: With VALIDATION_FAILED, CONFIGURATION_ERROR, or STORAGE_ACCESS_FAILED.
        """
        record = AuditLogRecord(
            id=f"aud_{generate_uuid7().hex}",
            organization_id=event_data.organization_id,
            actor_id=event_data.actor_id,
            execution_id=event_data.execution_id,
            event_type=event_data.event_type,
            resource_type=event_data.resource_type,
            resource_id=event_data.resource_id,
            details=event_data.details,
            created_at=datetime.now(UTC),
        )
        async with self._acquire_entities() as entities:
            await entities.insert_audit_log(record)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        """List compliance audit logs filtered by organization, actor, or event_type.

        Args:
            organization_id: Optional organization filter.
            actor_id: Optional actor ID filter.
            event_type: Optional event type filter.
            limit: Maximum number of records to return.

        Returns:
            List of validated AuditLogRecord domain models ordered newest-first.

        Raises:
            AppException: With VALIDATION_FAILED, CONFIGURATION_ERROR, or STORAGE_ACCESS_FAILED.
        """
        async with self._acquire_entities() as entities:
            return await entities.list_audit_logs(
                organization_id=organization_id,
                actor_id=actor_id,
                event_type=event_type,
                limit=limit,
            )

    async def log_usage(self, record: UsageRecord) -> None:
        """Insert an immutable FinOps UsageRecord into the append-only usage_records table.

        Args:
            record: Validated UsageRecord model with canonical usg_<hex32> ID.

        Raises:
            AppException: With VALIDATION_FAILED, CONFIGURATION_ERROR, or STORAGE_ACCESS_FAILED.
        """
        async with self._acquire_entities() as entities:
            await entities.insert_usage_record(record)

    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[UsageRecord]:
        """Retrieve UsageRecord rows for a target scope and entity.

        Args:
            scope: Scope identifier ('org', 'organization', 'user', or 'system').
            entity_id: Optional target organization or user ID.
            since: Optional ISO 8601 lower-bound timestamp filter.

        Returns:
            List of validated UsageRecord domain models ordered chronologically.

        Raises:
            AppException: With VALIDATION_FAILED, CONFIGURATION_ERROR, or STORAGE_ACCESS_FAILED.
        """
        since_dt = self._parse_since_iso(since)
        org_filter: str | None = None
        user_filter: str | None = None
        if scope in ("org", "organization") and entity_id:
            org_filter = entity_id
        elif scope == "user" and entity_id:
            user_filter = entity_id

        async with self._acquire_entities() as entities:
            return await entities.list_usage_records(
                organization_id=org_filter,
                user_id=user_filter,
                since=since_dt,
            )

    async def aggregate_organization_usage(
        self,
        organization_id: str | None = None,
        since: datetime | None = None,
    ) -> UsageRollupSummaryDTO:
        """Aggregate FinOps token and USD metrics via SQL SUM/COUNT over usage_records.

        Args:
            organization_id: Optional organization filter ('org_<hex32>' or None for global rollup).
            since: Optional UTC timestamp lower bound.

        Returns:
            Validated UsageRollupSummaryDTO computed directly from usage_records.

        Raises:
            AppException: With VALIDATION_FAILED, CONFIGURATION_ERROR, or STORAGE_ACCESS_FAILED.
        """
        async with self._acquire_entities() as entities:
            return await entities.aggregate_organization_usage(
                organization_id=organization_id,
                since=since,
            )

    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> DetailedUsageDTO:
        """Calculate multi-dimensional usage metrics across executions and usage_records.

        Args:
            scope: Scope ('user', 'org', 'organization', or 'system').
            target_id: Optional target ID for the scope.
            since: Optional ISO 8601 lower-bound timestamp filter.

        Returns:
            DetailedUsageDTO containing cost, token, model, and workflow breakdowns.

        Raises:
            AppException: With VALIDATION_FAILED on malformed since timestamp, or STORAGE_ACCESS_FAILED.
        """
        since_dt = self._parse_since_iso(since)

        exec_org_filter: str | None = None
        if scope in ("org", "organization") and target_id:
            exec_org_filter = target_id
        exec_user_filter: str | None = None
        if scope == "user" and target_id:
            exec_user_filter = target_id

        async with self._acquire_entities() as entities:
            candidate_execs = await entities.list_executions_filtered(
                organization_id=exec_org_filter,
                created_by=exec_user_filter,
                limit=10000,
            )
            filtered_execs: list[ExecutionRecord] = []
            for item in candidate_execs:
                if since_dt is not None:
                    if item.completed_at is None:
                        continue
                    completed_utc = item.completed_at
                    if completed_utc.tzinfo is None:
                        completed_utc = completed_utc.replace(tzinfo=UTC)
                    if completed_utc < since_dt:
                        continue
                filtered_execs.append(item)

            total_cost = 0.0
            models_used: dict[str, int] = {}
            workflows_used: dict[str, int] = {}
            for item in filtered_execs:
                total_cost += float(item.cost_estimate)
                if item.workflow_id:
                    if item.workflow_id in workflows_used:
                        workflows_used[item.workflow_id] += 1
                    else:
                        workflows_used[item.workflow_id] = 1
                for model_key, token_count in item.models_used.items():
                    if model_key in models_used:
                        models_used[model_key] += int(token_count)
                    else:
                        models_used[model_key] = int(token_count)

            if scope == "user" and target_id:
                user_records = await entities.list_usage_records(user_id=target_id, since=since_dt)
                total_tokens = sum(r.input_tokens + r.output_tokens for r in user_records)
            else:
                org_filter: str | None = None
                if scope in ("org", "organization") and target_id:
                    org_filter = target_id
                rollup = await entities.aggregate_organization_usage(
                    organization_id=org_filter,
                    since=since_dt,
                )
                total_tokens = rollup.total_prompt_tokens + rollup.total_completion_tokens

        target_key = "system"
        if target_id:
            target_key = target_id
        return DetailedUsageDTO(
            organization_id=target_key,
            total_cost_usd=total_cost,
            total_tokens=total_tokens,
            by_model=models_used,
            by_workflow=workflows_used,
        )
