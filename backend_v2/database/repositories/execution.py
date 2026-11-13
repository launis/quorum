"""Database repository implementation module for Workflow Executions."""

from __future__ import annotations

from datetime import UTC, datetime

from backend_v2.database.repositories.base import BaseRepository
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus
from backend_v2.models.state import TraceEvent

__all__ = ["ExecutionRepositoryImpl"]


def _completed_at_sort_key(record: ExecutionRecord) -> datetime:
    """Resolve a timezone-aware UTC sort timestamp for completed executions.

    Args:
        record: ExecutionRecord candidate to sort.

    Returns:
        UTC-aware completion timestamp, or datetime.min (UTC) when completed_at is None.
    """
    if record.completed_at is None:
        return datetime.min.replace(tzinfo=UTC)
    if record.completed_at.tzinfo is None:
        return record.completed_at.replace(tzinfo=UTC)
    return record.completed_at


class ExecutionRepositoryImpl(BaseRepository):
    """Repository implementation for ExecutionRecord persistence via EntityPersistencePort."""

    async def get_execution(self, execution_id: str, hydrate: bool = True) -> ExecutionRecord | None:
        """Retrieve a fully hydrated ExecutionRecord by primary key ID.

        Args:
            execution_id: Canonical exe_<hex32> execution identifier.
            hydrate: Retained for interface parity; primary-key lookups always join execution_payloads.

        Returns:
            Validated ExecutionRecord if found, otherwise None.
        """
        _ = hydrate
        async with self._acquire_entities() as entities:
            return await entities.get_execution(execution_id)

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
        async with self._acquire_entities() as entities:
            return await entities.save_execution(record)

    async def update_execution(self, execution_id: str, updates: ExecutionUpdateDTO) -> bool:
        """Apply partial updates to an ExecutionRecord with atomic SQL state_version OCC enforcement.

        Args:
            execution_id: Canonical exe_<hex32> execution identifier.
            updates: Validated ExecutionUpdateDTO carrying partial state changes.

        Returns:
            True when the execution record and its sidecar payload are atomically updated.

        Raises:
            ResourceNotFoundError: With RESOURCE_NOT_FOUND (HTTP 404) when execution_id does not exist.
            AppException: With CONFLICT (HTTP 409) when expected_state_version mismatches.
        """
        async with self._acquire_entities() as entities:
            return await entities.update_execution_occ(execution_id, updates)

    async def append_trace_event(self, execution_id: str, event_data: TraceEvent) -> bool:
        """Append a single TraceEvent onto an ExecutionRecord sidecar payload.

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
            next_trace = [*existing.execution_trace, event_data]
            updated = existing.model_copy(
                update={
                    "execution_trace": next_trace,
                    "updated_at": datetime.now(UTC),
                }
            )
            await entities.save_execution(updated)
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
        """List summary execution records filtered by organization_id and creator user_id via indexed SQL.

        Args:
            organization_id: Optional organization filter.
            user_id: Optional creator user filter matched against ExecutionRecord.created_by.

        Returns:
            List of matching summary ExecutionRecord domain models ordered by id DESC.
        """
        async with self._acquire_entities() as entities:
            return await entities.list_executions_filtered(
                organization_id=organization_id,
                created_by=user_id,
                limit=1000,
            )

    async def get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]:
        """Retrieve the most recently completed execution runs hydrated with sidecar payloads.

        Args:
            limit: Maximum number of completed executions to return.

        Returns:
            List of fully hydrated completed ExecutionRecord domain models ordered by completed_at DESC.
        """
        if limit <= 0:
            return []
        async with self._acquire_entities() as entities:
            completed = await entities.list_executions_filtered(
                status=ExecutionStatus.PASSED,
                limit=max(limit * 5, 100),
            )
            completed.sort(key=_completed_at_sort_key, reverse=True)
            hydrated: list[ExecutionRecord] = []
            for candidate in completed[:limit]:
                full_record = await entities.get_execution(candidate.id)
                if full_record is not None:
                    hydrated.append(full_record)
            return hydrated
