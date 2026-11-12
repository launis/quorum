"""Database repository implementation module for Workflow Executions."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from pydantic import TypeAdapter

from backend_v2.database.postgres.entity_adapter import apply_execution_updates
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent
from backend_v2.services.storage import get_storage_driver

logger = logging.getLogger(__name__)

_BLOB_OFFLOAD_THRESHOLD_BYTES = 100_000
_TRACE_LIST_ADAPTER: TypeAdapter[list[ErrorTraceEvent | TombstoneEvent | TraceEvent]] = TypeAdapter(
    list[ErrorTraceEvent | TombstoneEvent | TraceEvent]
)

__all__ = ["ExecutionRepositoryImpl"]


def _completed_at_sort_key(record: ExecutionRecord) -> datetime:
    """Resolve a timezone-aware UTC sort timestamp for completed executions."""
    if record.completed_at is None:
        return datetime.min.replace(tzinfo=UTC)
    if record.completed_at.tzinfo is None:
        return record.completed_at.replace(tzinfo=UTC)
    return record.completed_at


class ExecutionRepositoryImpl(BaseRepository):
    """Repository implementation for ExecutionRecord persistence via EntityPersistencePort."""

    async def _save_blob_payload(self, blob_path: str, payload_bytes: bytes, execution_id: str) -> None:
        """Persist an oversized execution JSON blob via the configured object storage driver.

        Args:
            blob_path: Relative blob storage path.
            payload_bytes: UTF-8 JSON bytes to persist.
            execution_id: Associated execution ID for structured error context.

        Raises:
            AppException: With INTERNAL_SERVER_ERROR (HTTP 500) if blob write fails.
        """
        driver = get_storage_driver()
        try:
            await driver.save(blob_path, payload_bytes)
        except Exception as exc:
            logger.error(
                "[ExecutionRepository] %s: Failed to offload blob %s for execution %s: %s",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                blob_path,
                execution_id,
                exc,
                extra={
                    "error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value,
                    "execution_id": execution_id,
                    "path": blob_path,
                },
                exc_info=True,
            )
            raise AppException(
                message=f"Failed to offload execution blob '{blob_path}'.",
                status_code=500,
                details={
                    "error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value,
                    "execution_id": execution_id,
                    "path": blob_path,
                },
            ) from exc

    async def _offload_record_blobs(self, record: ExecutionRecord) -> ExecutionRecord:
        """Offload oversized execution_trace, frozen_context, and context_variables payloads to blob storage.

        Args:
            record: ExecutionRecord candidate prior to database persistence.

        Returns:
            ExecutionRecord with >100KB fields replaced by blob storage references.
        """
        current = record
        if current.execution_trace:
            trace_bytes = _TRACE_LIST_ADAPTER.dump_json(current.execution_trace, exclude_none=True)
            if len(trace_bytes) > _BLOB_OFFLOAD_THRESHOLD_BYTES:
                blob_path = f"executions/{current.id}/execution_trace.json"
                await self._save_blob_payload(blob_path, trace_bytes, current.id)
                current = current.model_copy(update={"execution_trace": [], "execution_trace_storage_path": blob_path})

        if current.frozen_context is not None:
            fc_bytes = current.frozen_context.model_dump_json().encode("utf-8")
            if len(fc_bytes) > _BLOB_OFFLOAD_THRESHOLD_BYTES:
                blob_path = f"executions/{current.id}/frozen_context.json"
                await self._save_blob_payload(blob_path, fc_bytes, current.id)
                current = current.model_copy(update={"frozen_context": None, "frozen_context_storage_path": blob_path})

        if current.context_variables.variables:
            cv_bytes = current.context_variables.model_dump_json().encode("utf-8")
            if len(cv_bytes) > _BLOB_OFFLOAD_THRESHOLD_BYTES:
                blob_path = f"executions/{current.id}/context_variables.json"
                await self._save_blob_payload(blob_path, cv_bytes, current.id)
                current = current.model_copy(
                    update={
                        "context_variables": ContextVariablesDTO(variables={}),
                        "context_variables_storage_path": blob_path,
                    }
                )

        return current

    async def _hydrate_record_blobs(self, record: ExecutionRecord) -> ExecutionRecord:
        """Hydrate offloaded blob payloads back onto an ExecutionRecord.

        Args:
            record: ExecutionRecord loaded from PostgreSQL 19.

        Returns:
            Hydrated ExecutionRecord with offloaded JSON blobs restored.

        Raises:
            AppException: With DATA_CORRUPTION (HTTP 500) if a referenced blob is missing or corrupt.
        """
        driver = get_storage_driver()
        current = record

        if current.execution_trace_storage_path:
            path_val = current.execution_trace_storage_path
            try:
                blob_bytes = await driver.read(path_val)
                if not blob_bytes:
                    if str(current.status).upper() in ("PENDING", "RUNNING"):
                        current = current.model_copy(update={"execution_trace": []})
                    else:
                        raise ValueError(f"Empty execution_trace blob at {path_val}")
                else:
                    hydrated_trace = _TRACE_LIST_ADAPTER.validate_json(blob_bytes)
                    current = current.model_copy(update={"execution_trace": hydrated_trace})
            except Exception as exc:
                logger.error(
                    "[ExecutionRepository] %s: Failed to hydrate execution_trace blob %s for %s: %s",
                    ErrorCodes.DATA_CORRUPTION.name,
                    path_val,
                    current.id,
                    exc,
                    extra={"error_code": ErrorCodes.DATA_CORRUPTION.value, "path": path_val},
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to hydrate execution_trace blob '{path_val}'.",
                    status_code=500,
                    details={"error_code": ErrorCodes.DATA_CORRUPTION.value, "path": path_val},
                ) from exc

        if current.frozen_context_storage_path:
            path_val = current.frozen_context_storage_path
            try:
                blob_bytes = await driver.read(path_val)
                if not blob_bytes:
                    raise ValueError(f"Empty frozen_context blob at {path_val}")
                hydrated_fc = FrozenContext.model_validate_json(blob_bytes)
                current = current.model_copy(update={"frozen_context": hydrated_fc})
            except Exception as exc:
                logger.error(
                    "[ExecutionRepository] %s: Failed to hydrate frozen_context blob %s for %s: %s",
                    ErrorCodes.DATA_CORRUPTION.name,
                    path_val,
                    current.id,
                    exc,
                    extra={"error_code": ErrorCodes.DATA_CORRUPTION.value, "path": path_val},
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to hydrate frozen_context blob '{path_val}'.",
                    status_code=500,
                    details={"error_code": ErrorCodes.DATA_CORRUPTION.value, "path": path_val},
                ) from exc

        if current.context_variables_storage_path:
            path_val = current.context_variables_storage_path
            try:
                blob_bytes = await driver.read(path_val)
                if not blob_bytes:
                    raise ValueError(f"Empty context_variables blob at {path_val}")
                hydrated_cv = ContextVariablesDTO.model_validate_json(blob_bytes)
                current = current.model_copy(update={"context_variables": hydrated_cv})
            except Exception as exc:
                logger.error(
                    "[ExecutionRepository] %s: Failed to hydrate context_variables blob %s for %s: %s",
                    ErrorCodes.DATA_CORRUPTION.name,
                    path_val,
                    current.id,
                    exc,
                    extra={"error_code": ErrorCodes.DATA_CORRUPTION.value, "path": path_val},
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to hydrate context_variables blob '{path_val}'.",
                    status_code=500,
                    details={"error_code": ErrorCodes.DATA_CORRUPTION.value, "path": path_val},
                ) from exc

        return current

    @staticmethod
    def _updates_exceed_blob_threshold(updates: ExecutionUpdateDTO) -> bool:
        """Check whether an ExecutionUpdateDTO contains any payload exceeding 100KB."""
        if updates.execution_trace is not None:
            trace_bytes = _TRACE_LIST_ADAPTER.dump_json(updates.execution_trace, exclude_none=True)
            if len(trace_bytes) > _BLOB_OFFLOAD_THRESHOLD_BYTES:
                return True
        if updates.frozen_context is not None:
            fc_bytes = updates.frozen_context.model_dump_json().encode("utf-8")
            if len(fc_bytes) > _BLOB_OFFLOAD_THRESHOLD_BYTES:
                return True
        if updates.context_variables is not None and updates.context_variables.variables:
            cv_bytes = updates.context_variables.model_dump_json().encode("utf-8")
            if len(cv_bytes) > _BLOB_OFFLOAD_THRESHOLD_BYTES:
                return True
        return False

    async def get_execution(self, execution_id: str, hydrate: bool = True) -> ExecutionRecord | None:
        """Retrieve an ExecutionRecord by primary key ID.

        Args:
            execution_id: Canonical exe_<hex32> execution identifier.
            hydrate: When True, restores offloaded blob payloads from object storage.

        Returns:
            Validated ExecutionRecord if found, otherwise None.
        """
        async with self._acquire_entities() as entities:
            record = await entities.get_execution(execution_id)
        if record is None:
            return None
        if hydrate:
            return await self._hydrate_record_blobs(record)
        return record

    async def get_execution_status(self, execution_id: str) -> str | None:
        """Retrieve the lifecycle status string for an execution run.

        Args:
            execution_id: Canonical exe_<hex32> execution identifier.

        Returns:
            String execution status if found, otherwise None.
        """
        async with self._acquire_entities() as entities:
            record = await entities.get_execution(execution_id)
        if record is None:
            return None
        return str(record.status)

    async def create_execution(self, execution_data: ExecutionCreateDTO) -> str:
        """Create and persist a new ExecutionRecord from an ExecutionCreateDTO.

        Args:
            execution_data: Validated ingress ExecutionCreateDTO payload.

        Returns:
            Persisted canonical exe_<hex32> execution identifier.
        """
        resolved_inputs: WorkflowInputs
        if isinstance(execution_data.raw_inputs, WorkflowInputs):
            resolved_inputs = execution_data.raw_inputs
        elif isinstance(execution_data.raw_inputs, WorkflowInputsIngress):
            resolved_inputs = WorkflowInputs.model_validate(
                execution_data.raw_inputs.model_dump(mode="json"),
                strict=False,
            )
        else:
            resolved_inputs = WorkflowInputs(dynamic_inputs={})

        resolved_status = ExecutionStatus(execution_data.status.upper())
        now = datetime.now(UTC)
        record = ExecutionRecord(
            id=generate_opaque_id(EntityPrefix.EXECUTION),
            workflow_id=execution_data.workflow_id,
            target_locale=execution_data.target_locale,
            status=resolved_status,
            active_profile_id=execution_data.active_profile_id,
            output_profile_id=execution_data.output_profile_id,
            raw_inputs=resolved_inputs,
            execution_trace=[],
            context_variables=ContextVariablesDTO(variables={}),
            frozen_context=None,
            steps=[],
            step_states={},
            profile_syntheses={},
            source_identity_manifest={},
            models_used={},
            organization_id=execution_data.organization_id,
            created_by=execution_data.created_by,
            metadata=execution_data.metadata,
            created_at=now,
            updated_at=now,
        )
        offloaded = await self._offload_record_blobs(record)
        async with self._acquire_entities() as entities:
            return await entities.save_execution(offloaded)

    async def update_execution(self, execution_id: str, updates: ExecutionUpdateDTO) -> bool:
        """Apply partial updates to an ExecutionRecord with OCC enforcement and >100KB blob offloading.

        Args:
            execution_id: Canonical exe_<hex32> execution identifier.
            updates: Validated ExecutionUpdateDTO carrying partial state changes.

        Returns:
            True if updated, False if the execution record does not exist.

        Raises:
            AppException: With CONFLICT (HTTP 409) when expected_state_version mismatches.
        """
        if not self._updates_exceed_blob_threshold(updates):
            async with self._acquire_entities() as entities:
                return await entities.update_execution_occ(execution_id, updates)

        async with self._acquire_entities() as entities:
            existing = await entities.get_execution(execution_id)
            if existing is None:
                return False
            merged = apply_execution_updates(existing, updates)
            if "execution_trace" in updates.model_fields_set and updates.execution_trace is not None:
                merged = merged.model_copy(update={"execution_trace_storage_path": None})
            if "frozen_context" in updates.model_fields_set and updates.frozen_context is not None:
                merged = merged.model_copy(update={"frozen_context_storage_path": None})
            if "context_variables" in updates.model_fields_set and updates.context_variables is not None:
                merged = merged.model_copy(update={"context_variables_storage_path": None})
            offloaded = await self._offload_record_blobs(merged)
            await entities.save_execution(offloaded, expected_state_version=updates.expected_state_version)
            return True

    async def append_trace_event(self, execution_id: str, event_data: TraceEvent) -> bool:
        """Append a single TraceEvent onto an ExecutionRecord.

        Args:
            execution_id: Canonical exe_<hex32> execution identifier.
            event_data: Validated TraceEvent instance to append.

        Returns:
            True if appended, False if the execution record does not exist.
        """
        async with self._acquire_entities() as entities:
            existing = await entities.get_execution(execution_id)
            if existing is None:
                return False
            hydrated = await self._hydrate_record_blobs(existing)
            next_trace = [*hydrated.execution_trace, event_data]
            updated = hydrated.model_copy(
                update={
                    "execution_trace": next_trace,
                    "execution_trace_storage_path": None,
                    "updated_at": datetime.now(UTC),
                }
            )
            offloaded = await self._offload_record_blobs(updated)
            await entities.save_execution(offloaded)
            return True

    async def delete_execution(self, execution_id: str) -> bool:
        """Delete an ExecutionRecord by primary key ID.

        Args:
            execution_id: Canonical exe_<hex32> execution identifier.

        Returns:
            True if deleted, False otherwise.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_execution(execution_id)

    async def get_all_executions(
        self,
        organization_id: str | None = None,
        user_id: str | None = None,
    ) -> list[ExecutionRecord]:
        """List execution records filtered by organization_id and creator user_id.

        Args:
            organization_id: Optional organization filter.
            user_id: Optional creator user filter matched against ExecutionRecord.created_by.

        Returns:
            List of matching ExecutionRecord domain models.
        """
        async with self._acquire_entities() as entities:
            records = await entities.list_executions()
        filtered: list[ExecutionRecord] = []
        for rec in records:
            if organization_id is not None and rec.organization_id != organization_id:
                continue
            if user_id is not None and rec.created_by != user_id:
                continue
            filtered.append(rec)
        return filtered

    async def get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]:
        """Retrieve the most recently completed execution runs ordered by completed_at DESC.

        Args:
            limit: Maximum number of completed executions to return.

        Returns:
            List of completed ExecutionRecord domain models.
        """
        if limit <= 0:
            return []
        async with self._acquire_entities() as entities:
            records = await entities.list_executions()
        completed = [rec for rec in records if rec.status == ExecutionStatus.PASSED]
        completed.sort(key=_completed_at_sort_key, reverse=True)
        return completed[:limit]

    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        """Count persisted executions referencing a target matrix identifier in context_variables.

        Args:
            matrix_id: Canonical blk_<hex32> matrix identifier.

        Returns:
            Count of matching execution records.
        """
        async with self._acquire_entities() as entities:
            records = await entities.list_executions()
        return sum(
            1
            for rec in records
            if "matrix_id" in rec.context_variables.variables
            and rec.context_variables.variables["matrix_id"] == matrix_id
        )
