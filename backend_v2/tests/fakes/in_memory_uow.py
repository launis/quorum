"""Stateful In-Memory Unit of Work & AsyncPg Pool Fakes for Zero-ORM PostgreSQL 19 Testing.

Provides 0 ms hermetic test doubles conforming to QuorumUnitOfWork, GraphMutationPort,
TopologyResolutionPort, CausalReasoningPort, EntityPersistencePort, AsyncPgPoolProtocol,
AsyncPgConnectionProtocol, AsyncPgTransactionProtocol, and AsyncPgRecordProtocol
with real Multi-CTE wave materialization, cycle detection, Toulmin falsification queries,
and repeatable_read snapshot rollback semantics.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from types import TracebackType
from typing import Annotated, Self

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import from_json, to_json

from backend_v2.database.interfaces import (
    CausalReasoningPort,
    EntityPersistencePort,
    GraphMutationPort,
    TopologyResolutionPort,
)
from backend_v2.database.postgres.entity_adapter import (
    _TABLE_TO_ENTITY_PREFIX,
    apply_execution_updates,
    hydrate_execution_row,
)
from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    hydrate_audit_log_row,
    hydrate_usage_record_row,
)
from backend_v2.database.postgres.pool import (
    AsyncPgConnectionProtocol,
    AsyncPgRecordProtocol,
    AsyncPgTransactionProtocol,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import (
    ExecutionAssignment,
    Invitation,
    Organization,
    TenantSecretDTO,
    User,
)
from backend_v2.models.core_base import (
    V2CoreBase,
    format_prefixed_uuid7,
    generate_uuid7_opaque_id,
    parse_prefixed_uuid7,
)
from backend_v2.models.domain.base import (
    AuditLogRecord,
    UsageRecord,
    UsageRollupSummaryDTO,
)
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.proposition_graph import (
    CycleDetectedError,
    DependencyEdge,
    EdgeDraft,
    FalsifiedClaimMatch,
    NodeDraft,
    PropositionNode,
    PropositionPayloadDTO,
)
from backend_v2.models.domain.proposition_graph import (
    ReportBinaryPayloadDTO as ReportBinaryPayloadDTO,
)
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import (
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import (
    DependencyRelationType,
    EntityPrefix,
    ExecutionStatus,
    PropositionNodeType,
    SecretScope,
)

logger = logging.getLogger(__name__)

__all__ = [
    "InMemoryAsyncPgConnection",
    "InMemoryAsyncPgPool",
    "InMemoryAsyncPgRecord",
    "InMemoryAsyncPgTransaction",
    "InMemoryEntityAdapter",
    "InMemoryGraphAdapter",
    "InMemoryUnitOfWork",
]

type _ColumnValue = (
    str | int | float | bool | bytes | datetime | uuid.UUID | tuple[uuid.UUID, ...] | tuple[str, ...] | None
)
type _SeedRowEntry = BaseModel | Sequence[_ColumnValue]


def _to_column_value(val: object) -> _ColumnValue:
    """Narrow an arbitrary SQL argument to _ColumnValue."""
    if val is None or isinstance(val, (str, int, float, bool, bytes, datetime, uuid.UUID)):
        return val
    return str(val)


class _StoredNodeEntry(V2CoreBase):
    """Immutable in-memory storage entry for a persisted quorum_nodes row.

    Attributes:
        node: Hydrated PropositionNode domain model.
        local_key: Optional wave-local symbolic key for ON CONFLICT (run_id, local_key) DO SELECT.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    node: Annotated[PropositionNode, Field(description="Persisted PropositionNode instance.")]
    local_key: Annotated[str | None, Field(default=None, description="Optional wave-local symbolic key.")] = None


class _StoreSnapshot(V2CoreBase):
    """Immutable point-in-time snapshot of the in-memory PostgreSQL store for rollback.

    Attributes:
        nodes: Map of node_id to _StoredNodeEntry.
        edges: Map of edge_id to DependencyEdge.
        report_binaries: Map of report_id to ReportBinaryPayloadDTO.
        report_has_pdf: Map of report_id to boolean PDF availability flag.
        executions: Map of execution_id to ExecutionRecord.
        migrations_applied: Count of DDL migration executions.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    nodes: Annotated[dict[str, _StoredNodeEntry], Field(default_factory=dict, description="Stored nodes.")]
    edges: Annotated[dict[str, DependencyEdge], Field(default_factory=dict, description="Stored edges.")]
    report_binaries: Annotated[
        dict[str, ReportBinaryPayloadDTO],
        Field(default_factory=dict, description="Stored report binaries."),
    ]
    report_has_pdf: Annotated[dict[str, bool], Field(default_factory=dict, description="Report PDF flags.")]
    executions: Annotated[dict[str, ExecutionRecord], Field(default_factory=dict, description="Stored executions.")]
    audit_logs: Annotated[dict[str, AuditLogRecord], Field(default_factory=dict, description="Stored audit logs.")]
    usage_records: Annotated[dict[str, UsageRecord], Field(default_factory=dict, description="Stored usage records.")]
    step_criteria_blocks: Annotated[
        dict[str, tuple[str, ...]],
        Field(default_factory=dict, description="Ordered step_criteria_blocks junction rows keyed by step_id."),
    ]
    workflow_step_refs: Annotated[
        dict[str, tuple[str, ...]],
        Field(default_factory=dict, description="Workflow step reference junction rows keyed by workflow_id."),
    ]
    seed_counts: Annotated[dict[str, int], Field(default_factory=dict, description="Seeded table counts.")]
    migrations_applied: Annotated[int, Field(default=0, ge=0, description="DDL migrations applied count.")]


class _InMemorySqlStateError(Exception):
    """Simulated PostgreSQL exception carrying an SQLSTATE code for translation tests."""

    def __init__(self, message: str, *, sqlstate: str) -> None:
        """Initialize the simulated SQLSTATE error.

        Args:
            message: Human-readable constraint error description.
            sqlstate: Five-character PostgreSQL SQLSTATE code.
        """
        super().__init__(message)
        self.sqlstate: str = sqlstate


class _InMemoryPostgresStore:
    """Shared mutable in-memory storage backing InMemoryUnitOfWork and InMemoryAsyncPgPool.

    Attributes:
        nodes: Mapping of node_id to _StoredNodeEntry.
        edges: Mapping of edge_id to DependencyEdge.
        report_binaries: Mapping of report_id to ReportBinaryPayloadDTO.
        report_has_pdf: Mapping of report_id to boolean has_pdf flag.
        executions: Mapping of execution_id to ExecutionRecord.
        audit_logs: Mapping of audit_log_id to AuditLogRecord.
        usage_records: Mapping of usage_record_id to UsageRecord.
        seed_tables: Mapping of canonical PostgreSQL table name to stored records keyed by id.
        migrations_applied: Number of times DDL migrations were executed.
        current_org_reset_count: Number of times RESET quorum.current_org was executed.
    """

    def __init__(self) -> None:
        """Initialize empty in-memory tables."""
        self.nodes: dict[str, _StoredNodeEntry] = {}
        self.edges: dict[str, DependencyEdge] = {}
        self.report_binaries: dict[str, ReportBinaryPayloadDTO] = {}
        self.report_has_pdf: dict[str, bool] = {}
        self.executions: dict[str, ExecutionRecord] = {}
        self.audit_logs: dict[str, AuditLogRecord] = {}
        self.usage_records: dict[str, UsageRecord] = {}
        self.seed_tables: dict[str, dict[str, _SeedRowEntry]] = {
            "organizations": {},
            "users": {},
            "invitations": {},
            "tenant_secrets": {},
            "execution_assignments": {},
            "model_registries": {},
            "mcp_gateways": {},
            "prompt_blocks": {},
            "task_briefs": {},
            "steps": {},
            "workflows": {},
            "output_profiles": {},
            "report_artifacts": {},
            "trace_events": {},
        }
        self.step_criteria_blocks: dict[str, tuple[str, ...]] = {}
        self.workflow_step_refs: dict[str, tuple[str, ...]] = {}
        self.migrations_applied: int = 0
        self.current_org_reset_count: int = 0

    def take_snapshot(self) -> _StoreSnapshot:
        """Capture an immutable copy of all current table dictionaries.

        Returns:
            Frozen _StoreSnapshot for repeatable_read rollback.
        """
        return _StoreSnapshot(
            nodes=dict(self.nodes),
            edges=dict(self.edges),
            report_binaries=dict(self.report_binaries),
            report_has_pdf=dict(self.report_has_pdf),
            executions=dict(self.executions),
            audit_logs=dict(self.audit_logs),
            usage_records=dict(self.usage_records),
            step_criteria_blocks=dict(self.step_criteria_blocks),
            workflow_step_refs=dict(self.workflow_step_refs),
            seed_counts={tbl: len(rows) for tbl, rows in self.seed_tables.items()},
            migrations_applied=self.migrations_applied,
        )

    def restore_snapshot(self, snapshot: _StoreSnapshot) -> None:
        """Restore all in-memory tables to the provided _StoreSnapshot.

        Args:
            snapshot: Previously captured _StoreSnapshot instance.
        """
        self.nodes = dict(snapshot.nodes)
        self.edges = dict(snapshot.edges)
        self.report_binaries = dict(snapshot.report_binaries)
        self.report_has_pdf = dict(snapshot.report_has_pdf)
        self.executions = dict(snapshot.executions)
        self.audit_logs = dict(snapshot.audit_logs)
        self.usage_records = dict(snapshot.usage_records)
        self.step_criteria_blocks = dict(snapshot.step_criteria_blocks)
        self.workflow_step_refs = dict(snapshot.workflow_step_refs)
        self.migrations_applied = snapshot.migrations_applied


def _extract_uuid7_timestamp(prefixed_id: str, prefix: EntityPrefix) -> datetime:
    """Extract the UTC datetime embedded in the top 48 bits of a UUIDv7 Opaque Stripe ID.

    Args:
        prefixed_id: Canonical Opaque Stripe ID containing a version 7 UUID.
        prefix: Expected EntityPrefix enum member.

    Returns:
        UTC-aware datetime corresponding to the 48-bit Unix millisecond timestamp.
    """
    raw_uuid = parse_prefixed_uuid7(prefixed_id, prefix)
    timestamp_ms = (raw_uuid.int >> 80) & ((1 << 48) - 1)
    return datetime.fromtimestamp(timestamp_ms / 1000.0, tz=UTC)


_EXECUTION_INSERT_COLUMNS: tuple[str, ...] = (
    "id",
    "workflow_id",
    "workflow_version",
    "active_profile_id",
    "output_profile_id",
    "status",
    "target_locale",
    "progress",
    "status_message",
    "raw_inputs",
    "frozen_context",
    "frozen_context_storage_path",
    "pdf_report_path",
    "steps",
    "step_states",
    "profile_syntheses",
    "source_identity_manifest",
    "execution_trace",
    "execution_trace_storage_path",
    "context_variables",
    "context_variables_storage_path",
    "is_resumable",
    "prompt_tokens",
    "completion_tokens",
    "cached_tokens",
    "reasoning_tokens",
    "cumulative_synthesis_tokens",
    "dag_cost_usd",
    "cumulative_synthesis_cost",
    "cost_estimate",
    "models_used",
    "execution_summary",
    "metadata",
    "duration_ms",
    "error",
    "updated_at",
    "completed_at",
    "created_by",
    "organization_id",
    "state_version",
)


def _hydrate_in_memory_execution_record(args: Sequence[object]) -> ExecutionRecord:
    """Hydrate an ExecutionRecord from parameterized INSERT INTO EXECUTIONS bind arguments.

    Delegates directly to the canonical PostgreSQL `hydrate_execution_row` adapter function,
    synthesizing the PostgreSQL 19 VIRTUAL `created_at` column from the UUIDv7 primary key.

    Args:
        args: Positional SQL bind parameters for executions insertion.

    Returns:
        Hydrated ExecutionRecord domain instance.
    """
    row_columns = dict(
        zip(
            _EXECUTION_INSERT_COLUMNS,
            (_to_column_value(arg) for arg in args),
            strict=True,
        )
    )
    exec_uuid_val = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
    exec_id = format_prefixed_uuid7(exec_uuid_val, EntityPrefix.EXECUTION)
    row_columns["created_at"] = _extract_uuid7_timestamp(exec_id, EntityPrefix.EXECUTION)
    return hydrate_execution_row(InMemoryAsyncPgRecord(row_columns))


def _hydrate_in_memory_proposition_node(row: Sequence[object]) -> _StoredNodeEntry:
    """Hydrate a _StoredNodeEntry from parameterized INSERT INTO QUORUM_NODES row values.

    Args:
        row: Positional SQL bind parameters for a quorum_nodes row.

    Returns:
        Hydrated _StoredNodeEntry instance.
    """
    node_uuid = row[0] if isinstance(row[0], (uuid.UUID, str)) else str(row[0])
    run_uuid = row[1] if isinstance(row[1], (uuid.UUID, str)) else str(row[1])
    node_id = format_prefixed_uuid7(node_uuid, EntityPrefix.NODE)
    run_id = format_prefixed_uuid7(run_uuid, EntityPrefix.EXECUTION)
    local_key = str(row[2]) if row[2] is not None else None
    node_type = PropositionNodeType(str(row[3]))
    confidence = float(str(row[4]))
    payload = PropositionPayloadDTO.model_validate_json(str(row[5]))
    node = PropositionNode(
        node_id=node_id,
        run_id=run_id,
        node_type=node_type,
        confidence=confidence,
        payload=payload,
        created_at=_extract_uuid7_timestamp(node_id, EntityPrefix.NODE),
    )
    return _StoredNodeEntry(node=node, local_key=local_key)


def _find_cycle_in_edges(run_id: str, edges: Sequence[DependencyEdge]) -> tuple[str, ...] | None:
    """Perform deterministic DFS cycle detection over directed edges for run_id.

    Args:
        run_id: Canonical exe_<uuid7_hex> execution identifier.
        edges: Persisted DependencyEdge collection.

    Returns:
        Tuple of nod_<uuid7_hex> IDs forming the cycle if a cycle exists, otherwise None.
    """
    adjacency: dict[str, list[str]] = {}
    nodes_in_run: set[str] = set()
    for edge in edges:
        if edge.run_id != run_id:
            continue
        nodes_in_run.add(edge.source_id)
        nodes_in_run.add(edge.target_id)
        if edge.source_id not in adjacency:
            adjacency[edge.source_id] = []
        adjacency[edge.source_id].append(edge.target_id)

    visited: set[str] = set()
    active_stack: list[str] = []
    active_set: set[str] = set()

    def _dfs(current: str) -> tuple[str, ...] | None:
        visited.add(current)
        active_stack.append(current)
        active_set.add(current)

        if current in adjacency:
            for neighbor in sorted(adjacency[current]):
                if neighbor not in visited:
                    found = _dfs(neighbor)
                    if found is not None:
                        return found
                elif neighbor in active_set:
                    cycle_start = active_stack.index(neighbor)
                    return tuple([*active_stack[cycle_start:], neighbor])

        active_stack.pop()
        active_set.remove(current)
        return None

    for start_node in sorted(nodes_in_run):
        if start_node not in visited:
            cycle = _dfs(start_node)
            if cycle is not None:
                return cycle
    return None


class InMemoryAsyncPgRecord:
    """In-memory implementation of AsyncPgRecordProtocol without Mapping inheritance.

    Attributes:
        columns: Typed mapping of column names to scalar or sequence values.
    """

    def __init__(self, columns: dict[str, _ColumnValue]) -> None:
        """Initialize the record with a column dictionary.

        Args:
            columns: Mapping of column names to cell values.
        """
        self.columns: dict[str, _ColumnValue] = dict(columns)

    def __getitem__(self, key: str) -> object:
        """Retrieve column value by column name.

        Args:
            key: Column name string.

        Returns:
            Stored column value.

        Raises:
            KeyError: If key is not present in the record.
        """
        return self.columns[key]

    def __contains__(self, key: object) -> bool:
        """Return True if column name exists in this record.

        Args:
            key: Candidate column key.

        Returns:
            Boolean membership result.
        """
        return isinstance(key, str) and key in self.columns


class InMemoryGraphAdapter:
    """Stateful in-memory implementation of GraphMutationPort, TopologyResolutionPort, and CausalReasoningPort."""

    def __init__(self, store: _InMemoryPostgresStore) -> None:
        """Initialize the in-memory graph adapter against a shared store.

        Args:
            store: Shared _InMemoryPostgresStore instance.
        """
        self._store: _InMemoryPostgresStore = store

    async def materialize_wave(
        self,
        run_id: str,
        node_drafts: Sequence[NodeDraft],
        edge_drafts: Sequence[EdgeDraft],
    ) -> Sequence[PropositionNode]:
        """Materialize NodeDraft and EdgeDraft items atomically with ON CONFLICT DO SELECT semantics.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.
            node_drafts: Symbolic NodeDraft items.
            edge_drafts: Symbolic EdgeDraft items.

        Returns:
            Sequence of persisted PropositionNode models ordered by node_id ascending.

        Raises:
            AppException: With VALIDATION_FAILED on invalid run_id, duplicate local_key,
                or dangling edge endpoint keys.
        """
        _ = parse_prefixed_uuid7(run_id, EntityPrefix.EXECUTION)

        seen_keys: set[str] = set()
        for draft in node_drafts:
            if draft.local_key in seen_keys:
                msg = f"Duplicate NodeDraft local_key '{draft.local_key}' in wave for run '{run_id}'."
                logger.error(
                    "[InMemoryGraphAdapter] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "run_id": run_id},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            seen_keys.add(draft.local_key)

        for edge_draft in edge_drafts:
            if edge_draft.source_key not in seen_keys or edge_draft.target_key not in seen_keys:
                msg = (
                    f"Dangling EdgeDraft reference ({edge_draft.source_key!r} -> {edge_draft.target_key!r}) "
                    f"in wave for run '{run_id}'."
                )
                logger.error(
                    "[InMemoryGraphAdapter] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "run_id": run_id},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        if not node_drafts:
            return ()

        existing_by_local_key: dict[str, PropositionNode] = {}
        for entry in self._store.nodes.values():
            if entry.node.run_id == run_id and entry.local_key is not None:
                existing_by_local_key[entry.local_key] = entry.node

        resolved_by_key: dict[str, PropositionNode] = {}
        materialized_nodes: list[PropositionNode] = []

        for draft in node_drafts:
            if draft.local_key in existing_by_local_key:
                persisted_node = existing_by_local_key[draft.local_key]
            else:
                new_node_id = generate_uuid7_opaque_id(EntityPrefix.NODE)
                created_at = _extract_uuid7_timestamp(new_node_id, EntityPrefix.NODE)
                persisted_node = PropositionNode(
                    node_id=new_node_id,
                    run_id=run_id,
                    node_type=draft.node_type,
                    confidence=draft.confidence,
                    payload=draft.payload,
                    created_at=created_at,
                )
                self._store.nodes[new_node_id] = _StoredNodeEntry(
                    node=persisted_node,
                    local_key=draft.local_key,
                )
            resolved_by_key[draft.local_key] = persisted_node
            materialized_nodes.append(persisted_node)

        for edge_draft in edge_drafts:
            src_node = resolved_by_key[edge_draft.source_key]
            tgt_node = resolved_by_key[edge_draft.target_key]
            matched_edge: DependencyEdge | None = None
            for existing in self._store.edges.values():
                if (
                    existing.run_id == run_id
                    and existing.source_id == src_node.node_id
                    and existing.target_id == tgt_node.node_id
                    and existing.relation_type == edge_draft.relation_type
                ):
                    matched_edge = existing
                    break
            if matched_edge is not None:
                self._store.edges[matched_edge.edge_id] = matched_edge.model_copy(
                    update={"causal_weight": edge_draft.causal_weight}
                )
            else:
                new_edge_id = generate_uuid7_opaque_id(EntityPrefix.EDGE)
                edge_created_at = _extract_uuid7_timestamp(new_edge_id, EntityPrefix.EDGE)
                persisted_edge = DependencyEdge(
                    edge_id=new_edge_id,
                    run_id=run_id,
                    source_id=src_node.node_id,
                    target_id=tgt_node.node_id,
                    relation_type=edge_draft.relation_type,
                    causal_weight=edge_draft.causal_weight,
                    created_at=edge_created_at,
                )
                self._store.edges[new_edge_id] = persisted_edge

        materialized_nodes.sort(key=lambda n: n.node_id)
        return tuple(materialized_nodes)

    async def upsert_wave_batch(
        self,
        nodes: Sequence[PropositionNode],
        edges: Sequence[DependencyEdge],
    ) -> None:
        """Upsert a batch of persisted PropositionNode and DependencyEdge entities.

        Args:
            nodes: PropositionNode instances to upsert.
            edges: DependencyEdge instances to upsert.
        """
        for node in nodes:
            _ = parse_prefixed_uuid7(node.node_id, EntityPrefix.NODE)
            _ = parse_prefixed_uuid7(node.run_id, EntityPrefix.EXECUTION)
            existing_key: str | None = None
            if node.node_id in self._store.nodes:
                existing_key = self._store.nodes[node.node_id].local_key
            self._store.nodes[node.node_id] = _StoredNodeEntry(node=node, local_key=existing_key)

        for edge in edges:
            _ = parse_prefixed_uuid7(edge.edge_id, EntityPrefix.EDGE)
            _ = parse_prefixed_uuid7(edge.run_id, EntityPrefix.EXECUTION)
            _ = parse_prefixed_uuid7(edge.source_id, EntityPrefix.NODE)
            _ = parse_prefixed_uuid7(edge.target_id, EntityPrefix.NODE)
            self._store.edges[edge.edge_id] = edge

    async def assert_acyclic(self, run_id: str) -> None:
        """Verify that the proposition graph for run_id is a valid DAG with zero cycles.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.

        Raises:
            CycleDetectedError: If a directed cycle is discovered.
        """
        _ = parse_prefixed_uuid7(run_id, EntityPrefix.EXECUTION)
        cycle_path = _find_cycle_in_edges(run_id, list(self._store.edges.values()))
        if cycle_path is not None:
            logger.error(
                "[InMemoryGraphAdapter] %s: Cycle detected in run '%s': %s",
                ErrorCodes.VALIDATION_FAILED.name,
                run_id,
                cycle_path,
                extra={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "run_id": run_id,
                    "cycle_path": list(cycle_path),
                },
            )
            raise CycleDetectedError(run_id=run_id, cycle_path=cycle_path)

    async def fetch_next_kahn_wave(self, run_id: str) -> Sequence[PropositionNode]:
        """Return all PropositionNode instances in run_id with in-degree 0.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.

        Returns:
            Sequence of root PropositionNode models ordered by node_id ascending.
        """
        _ = parse_prefixed_uuid7(run_id, EntityPrefix.EXECUTION)
        targets_with_incoming: set[str] = {
            edge.target_id for edge in self._store.edges.values() if edge.run_id == run_id
        }
        roots = [
            entry.node
            for entry in self._store.nodes.values()
            if entry.node.run_id == run_id and entry.node.node_id not in targets_with_incoming
        ]
        roots.sort(key=lambda n: n.node_id)
        return tuple(roots)

    async def find_falsified_claims(
        self,
        run_id: str,
        min_confidence: float = 0.70,
    ) -> Sequence[FalsifiedClaimMatch]:
        """Execute the 3-way Toulmin falsification join in memory for run_id.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.
            min_confidence: Minimum rebuttal confidence threshold in [0.0, 1.0].

        Returns:
            Sequence of FalsifiedClaimMatch DTOs ordered by rebuttal confidence descending.
        """
        if not 0.0 <= min_confidence <= 1.0:
            msg = f"min_confidence must be between 0.0 and 1.0, got {min_confidence}."
            logger.error(
                "[InMemoryGraphAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "run_id": run_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        _ = parse_prefixed_uuid7(run_id, EntityPrefix.EXECUTION)
        run_nodes: dict[str, PropositionNode] = {
            entry.node.node_id: entry.node for entry in self._store.nodes.values() if entry.node.run_id == run_id
        }
        run_edges: list[DependencyEdge] = [edge for edge in self._store.edges.values() if edge.run_id == run_id]

        matches: list[FalsifiedClaimMatch] = []
        for rebuttal in run_nodes.values():
            if rebuttal.node_type != PropositionNodeType.REBUTTAL:
                continue
            if rebuttal.confidence < min_confidence:
                continue
            for edge_rebuts in run_edges:
                if (
                    edge_rebuts.source_id != rebuttal.node_id
                    or edge_rebuts.relation_type != DependencyRelationType.REBUTS
                ):
                    continue
                if edge_rebuts.target_id not in run_nodes:
                    continue
                warrant = run_nodes[edge_rebuts.target_id]
                if warrant.node_type != PropositionNodeType.WARRANT:
                    continue
                for edge_warrants in run_edges:
                    if (
                        edge_warrants.source_id != warrant.node_id
                        or edge_warrants.relation_type != DependencyRelationType.WARRANTS
                    ):
                        continue
                    if edge_warrants.target_id not in run_nodes:
                        continue
                    claim = run_nodes[edge_warrants.target_id]
                    if claim.node_type != PropositionNodeType.CLAIM:
                        continue
                    matches.append(
                        FalsifiedClaimMatch(
                            rebuttal_id=rebuttal.node_id,
                            invalidated_warrant_id=warrant.node_id,
                            falsified_claim_id=claim.node_id,
                            rebuttal_confidence=rebuttal.confidence,
                            claim_statement=claim.payload.statement,
                        )
                    )

        matches.sort(key=lambda m: (-m.rebuttal_confidence, m.falsified_claim_id))
        return tuple(matches)


class InMemoryEntityAdapter:
    """Stateful in-memory implementation of EntityPersistencePort."""

    def __init__(self, store: _InMemoryPostgresStore) -> None:
        """Initialize the in-memory entity adapter against a shared store.

        Args:
            store: Shared _InMemoryPostgresStore instance.
        """
        self._store: _InMemoryPostgresStore = store

    async def upsert_organization(self, org: Organization) -> str:
        """Upsert an Organization entity in memory.

        Args:
            org: Validated Organization domain model.

        Returns:
            Canonical org_<uuid7_hex> organization identifier.
        """
        _ = parse_prefixed_uuid7(org.id, EntityPrefix.ORGANIZATION)
        self._store.seed_tables["organizations"][org.id] = org
        return org.id

    async def get_organization(self, org_id: str) -> Organization | None:
        """Retrieve an Organization by org_id.

        Args:
            org_id: Canonical org_<uuid7_hex> organization identifier.

        Returns:
            Stored Organization or None if not found.
        """
        _ = parse_prefixed_uuid7(org_id, EntityPrefix.ORGANIZATION)
        if org_id in self._store.seed_tables["organizations"]:
            item = self._store.seed_tables["organizations"][org_id]
            if isinstance(item, Organization):
                return item
        return None

    async def list_organizations(self) -> list[Organization]:
        """List all persisted Organization entities.

        Returns:
            List of Organization domain models.
        """
        orgs = [item for item in self._store.seed_tables["organizations"].values() if isinstance(item, Organization)]
        orgs.sort(key=lambda o: o.id)
        return orgs

    async def upsert_user(self, user: User) -> str:
        """Upsert a User entity in memory.

        Args:
            user: Validated User domain model.

        Returns:
            Canonical usr_<uuid7_hex> user identifier.
        """
        _ = parse_prefixed_uuid7(user.id, EntityPrefix.USER)
        if user.organization_id is not None:
            _ = parse_prefixed_uuid7(user.organization_id, EntityPrefix.ORGANIZATION)
        if user.created_by is not None:
            _ = parse_prefixed_uuid7(user.created_by, EntityPrefix.USER)
        self._store.seed_tables["users"][user.id] = user
        return user.id

    async def get_user(self, user_id: str) -> User | None:
        """Retrieve a User by user_id.

        Args:
            user_id: Canonical usr_<uuid7_hex> user identifier.

        Returns:
            Stored User or None if not found.
        """
        _ = parse_prefixed_uuid7(user_id, EntityPrefix.USER)
        if user_id in self._store.seed_tables["users"]:
            item = self._store.seed_tables["users"][user_id]
            if isinstance(item, User):
                return item
        return None

    async def list_users(self, organization_id: str | None = None) -> list[User]:
        """List persisted User entities, optionally filtered by organization_id.

        Args:
            organization_id: Optional org_<uuid7_hex> organization filter.

        Returns:
            List of User domain models.
        """
        if organization_id is not None:
            _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        users = [
            item
            for item in self._store.seed_tables["users"].values()
            if isinstance(item, User) and (organization_id is None or item.organization_id == organization_id)
        ]
        users.sort(key=lambda u: u.id)
        return users

    async def upsert_invitation(self, invitation: Invitation) -> str:
        """Upsert an Invitation entity in memory.

        Args:
            invitation: Validated Invitation domain model.

        Returns:
            Canonical inv_<uuid7_hex> invitation identifier.
        """
        _ = parse_prefixed_uuid7(invitation.id, EntityPrefix.INVITATION)
        _ = parse_prefixed_uuid7(invitation.organization_id, EntityPrefix.ORGANIZATION)
        self._store.seed_tables["invitations"][invitation.id] = invitation
        return invitation.id

    async def get_invitation(self, invitation_id: str) -> Invitation | None:
        """Retrieve an Invitation by invitation_id.

        Args:
            invitation_id: Canonical inv_<uuid7_hex> invitation identifier.

        Returns:
            Stored Invitation or None if not found.
        """
        _ = parse_prefixed_uuid7(invitation_id, EntityPrefix.INVITATION)
        if invitation_id in self._store.seed_tables["invitations"]:
            item = self._store.seed_tables["invitations"][invitation_id]
            if isinstance(item, Invitation):
                return item
        return None

    async def list_invitations(self, organization_id: str | None = None) -> list[Invitation]:
        """List persisted Invitation entities, optionally filtered by organization_id.

        Args:
            organization_id: Optional org_<uuid7_hex> organization filter.

        Returns:
            List of Invitation domain models.
        """
        if organization_id is not None:
            _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        invs = [
            item
            for item in self._store.seed_tables["invitations"].values()
            if isinstance(item, Invitation) and (organization_id is None or item.organization_id == organization_id)
        ]
        invs.sort(key=lambda i: i.id)
        return invs

    async def upsert_tenant_secret(self, secret: TenantSecretDTO) -> str:
        """Upsert a TenantSecretDTO entity in memory.

        Args:
            secret: Validated TenantSecretDTO domain model.

        Returns:
            Canonical sec_<uuid7_hex> tenant secret identifier.
        """
        _ = parse_prefixed_uuid7(secret.id, EntityPrefix.TENANT_SECRET)
        _ = parse_prefixed_uuid7(secret.organization_id, EntityPrefix.ORGANIZATION)
        if secret.scope == SecretScope.MCP_GATEWAY:
            _ = parse_prefixed_uuid7(secret.target_identifier, EntityPrefix.MCP_GATEWAY)
        self._store.seed_tables["tenant_secrets"][secret.id] = secret
        return secret.id

    async def get_tenant_secret(self, secret_id: str) -> TenantSecretDTO | None:
        """Retrieve a TenantSecretDTO by secret_id.

        Args:
            secret_id: Canonical sec_<uuid7_hex> tenant secret identifier.

        Returns:
            Stored TenantSecretDTO or None if not found.
        """
        _ = parse_prefixed_uuid7(secret_id, EntityPrefix.TENANT_SECRET)
        if secret_id in self._store.seed_tables["tenant_secrets"]:
            item = self._store.seed_tables["tenant_secrets"][secret_id]
            if isinstance(item, TenantSecretDTO):
                return item
        return None

    async def list_tenant_secrets(self, organization_id: str | None = None) -> list[TenantSecretDTO]:
        """List persisted TenantSecretDTO entities, optionally filtered by organization_id.

        Args:
            organization_id: Optional org_<uuid7_hex> organization filter.

        Returns:
            List of TenantSecretDTO domain models.
        """
        if organization_id is not None:
            _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        secrets = [
            item
            for item in self._store.seed_tables["tenant_secrets"].values()
            if isinstance(item, TenantSecretDTO)
            and (organization_id is None or item.organization_id == organization_id)
        ]
        secrets.sort(key=lambda s: s.id)
        return secrets

    async def delete_tenant_secret(self, secret_id: str) -> bool:
        """Delete a TenantSecretDTO by primary key in memory.

        Args:
            secret_id: Canonical sec_<uuid7_hex> tenant secret identifier.

        Returns:
            True if a matching secret was deleted, False otherwise.
        """
        sec_uuid = parse_prefixed_uuid7(secret_id, EntityPrefix.TENANT_SECRET)
        raw_uuid_key = str(sec_uuid)
        deleted = False
        if secret_id in self._store.seed_tables["tenant_secrets"]:
            del self._store.seed_tables["tenant_secrets"][secret_id]
            deleted = True
        if raw_uuid_key in self._store.seed_tables["tenant_secrets"]:
            del self._store.seed_tables["tenant_secrets"][raw_uuid_key]
            deleted = True
        return deleted

    async def upsert_execution_assignment(self, assignment: ExecutionAssignment) -> str:
        """Upsert an ExecutionAssignment entity in memory.

        Args:
            assignment: Validated ExecutionAssignment domain model.

        Returns:
            Canonical tsk_<uuid7_hex> execution assignment identifier.
        """
        _ = parse_prefixed_uuid7(assignment.id, EntityPrefix.ASSIGNMENT)
        _ = parse_prefixed_uuid7(assignment.organization_id, EntityPrefix.ORGANIZATION)
        self._store.seed_tables["execution_assignments"][assignment.id] = assignment
        return assignment.id

    async def get_execution_assignment(self, assignment_id: str) -> ExecutionAssignment | None:
        """Retrieve an ExecutionAssignment by assignment_id.

        Args:
            assignment_id: Canonical tsk_<uuid7_hex> execution assignment identifier.

        Returns:
            Stored ExecutionAssignment or None if not found.
        """
        _ = parse_prefixed_uuid7(assignment_id, EntityPrefix.ASSIGNMENT)
        if assignment_id in self._store.seed_tables["execution_assignments"]:
            item = self._store.seed_tables["execution_assignments"][assignment_id]
            if isinstance(item, ExecutionAssignment):
                return item
        return None

    async def list_execution_assignments(
        self,
        organization_id: str | None = None,
    ) -> list[ExecutionAssignment]:
        """List persisted ExecutionAssignment entities, optionally filtered by organization_id.

        Args:
            organization_id: Optional org_<uuid7_hex> organization filter.

        Returns:
            List of ExecutionAssignment domain models.
        """
        if organization_id is not None:
            _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        assignments = [
            item
            for item in self._store.seed_tables["execution_assignments"].values()
            if isinstance(item, ExecutionAssignment)
            and (organization_id is None or item.organization_id == organization_id)
        ]
        assignments.sort(key=lambda a: a.id)
        return assignments

    async def get_execution_assignment_by_token_hash(self, token_hash: str) -> ExecutionAssignment | None:
        """Retrieve an ExecutionAssignment by indexed SHA-256 token_hash lookup in memory.

        Args:
            token_hash: 64-character hex SHA-256 token digest.

        Returns:
            Matching ExecutionAssignment or None.
        """
        normalized_hash = token_hash.strip()
        if not normalized_hash:
            return None
        for item in self._store.seed_tables["execution_assignments"].values():
            if isinstance(item, ExecutionAssignment) and item.token_hash == normalized_hash:
                return item
        return None

    async def get_execution_assignment_by_execution_id(self, execution_id: str) -> ExecutionAssignment | None:
        """Retrieve the newest ExecutionAssignment referencing execution_id in memory.

        Args:
            execution_id: Canonical exe_<uuid7_hex> execution identifier.

        Returns:
            Matching ExecutionAssignment or None.
        """
        _ = parse_prefixed_uuid7(execution_id, EntityPrefix.EXECUTION)
        matched = [
            item
            for item in self._store.seed_tables["execution_assignments"].values()
            if isinstance(item, ExecutionAssignment) and item.execution_id == execution_id
        ]
        if not matched:
            return None
        matched.sort(key=lambda a: parse_prefixed_uuid7(a.id, EntityPrefix.ASSIGNMENT), reverse=True)
        return matched[0]

    async def list_execution_assignments_by_organization(
        self,
        organization_id: str,
        *,
        batch_id: str | None = None,
        workflow_id: str | None = None,
        limit: int = 100,
    ) -> list[ExecutionAssignment]:
        """List ExecutionAssignments for an organization ordered by id DESC with optional filters.

        Args:
            organization_id: Canonical org_<uuid7_hex> organization identifier.
            batch_id: Optional canonical tsk_<uuid7_hex> batch identifier filter.
            workflow_id: Optional canonical wor_<uuid7_hex> workflow identifier filter.
            limit: Maximum number of assignments to return.

        Returns:
            List of matching ExecutionAssignment models ordered by id DESC.
        """
        _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        if batch_id is not None:
            _ = parse_prefixed_uuid7(batch_id, EntityPrefix.ASSIGNMENT)
        if workflow_id is not None:
            _ = parse_prefixed_uuid7(workflow_id, EntityPrefix.WORKFLOW)
        if limit <= 0:
            return []
        matched = [
            item
            for item in self._store.seed_tables["execution_assignments"].values()
            if isinstance(item, ExecutionAssignment)
            and item.organization_id == organization_id
            and (batch_id is None or item.batch_id == batch_id)
            and (workflow_id is None or item.workflow_id == workflow_id)
        ]
        matched.sort(key=lambda a: parse_prefixed_uuid7(a.id, EntityPrefix.ASSIGNMENT), reverse=True)
        return matched[:limit]

    async def upsert_task_brief(self, brief: TaskBrief) -> str:
        """Upsert a TaskBrief entity in memory.

        Args:
            brief: Validated TaskBrief domain model.

        Returns:
            Canonical tbr_<uuid7_hex> task brief identifier.
        """
        _ = parse_prefixed_uuid7(brief.id, EntityPrefix.TASK_BRIEF)
        _ = parse_prefixed_uuid7(brief.organization_id, EntityPrefix.ORGANIZATION)
        self._store.seed_tables["task_briefs"][brief.id] = brief
        return brief.id

    async def get_task_brief(self, brief_id: str) -> TaskBrief | None:
        """Retrieve a TaskBrief by brief_id.

        Args:
            brief_id: Canonical tbr_<uuid7_hex> task brief identifier.

        Returns:
            Stored TaskBrief or None if not found.
        """
        _ = parse_prefixed_uuid7(brief_id, EntityPrefix.TASK_BRIEF)
        if brief_id in self._store.seed_tables["task_briefs"]:
            item = self._store.seed_tables["task_briefs"][brief_id]
            if isinstance(item, TaskBrief):
                return item
        return None

    async def list_task_briefs(self) -> list[TaskBrief]:
        """List all persisted TaskBrief entities.

        Returns:
            List of TaskBrief domain models.
        """
        briefs = [item for item in self._store.seed_tables["task_briefs"].values() if isinstance(item, TaskBrief)]
        briefs.sort(key=lambda b: b.id)
        return briefs

    async def save_report_binary(self, payload: ReportBinaryPayloadDTO) -> None:
        """Persist a ReportBinaryPayloadDTO in memory and mark report_has_pdf.

        Args:
            payload: Validated ReportBinaryPayloadDTO instance.

        Raises:
            AppException: With VALIDATION_FAILED if report_id is invalid or size_bytes mismatches.
        """
        if len(payload.pdf_bytes) != payload.size_bytes:
            msg = (
                f"ReportBinaryPayloadDTO size_bytes ({payload.size_bytes}) does not match "
                f"actual pdf_bytes length ({len(payload.pdf_bytes)})."
            )
            logger.error(
                "[InMemoryEntityAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "report_id": payload.report_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        _ = parse_prefixed_uuid7(payload.report_id, EntityPrefix.REPORT)
        virtual_created_at = _extract_uuid7_timestamp(payload.report_id, EntityPrefix.REPORT)
        self._store.report_binaries[payload.report_id] = payload.model_copy(update={"created_at": virtual_created_at})
        self._store.report_has_pdf[payload.report_id] = True

    async def get_report_binary(self, report_id: str) -> ReportBinaryPayloadDTO | None:
        """Retrieve a ReportBinaryPayloadDTO by report_id.

        Args:
            report_id: Canonical rep_<uuid7_hex> report identifier.

        Returns:
            Stored ReportBinaryPayloadDTO or None if not found.
        """
        _ = parse_prefixed_uuid7(report_id, EntityPrefix.REPORT)
        if report_id in self._store.report_binaries:
            return self._store.report_binaries[report_id]
        return None

    async def save_execution(
        self,
        record: ExecutionRecord,
        *,
        expected_state_version: int | None = None,
    ) -> str:
        """Persist an ExecutionRecord in memory with full roundtrip validation and OCC enforcement.

        Args:
            record: Validated ExecutionRecord domain model.
            expected_state_version: Optional expected state_version for optimistic concurrency control.

        Returns:
            Canonical exe_<uuid7_hex> execution identifier.

        Raises:
            AppException: With VALIDATION_FAILED on invalid ID or CONFLICT on state_version mismatch.
        """
        _ = parse_prefixed_uuid7(record.id, EntityPrefix.EXECUTION)
        target_record = record
        if expected_state_version is not None:
            actual_version = 1
            if record.id in self._store.executions:
                actual_version = self._store.executions[record.id].state_version
            if actual_version != expected_state_version:
                msg = (
                    f"Optimistic concurrency conflict for execution '{record.id}': "
                    f"expected state_version={expected_state_version}, actual state_version={actual_version}."
                )
                logger.error(
                    "[InMemoryEntityAdapter] %s: %s",
                    ErrorCodes.CONFLICT.name,
                    msg,
                    extra={
                        "error_code": ErrorCodes.CONFLICT.value,
                        "execution_id": record.id,
                        "expected_state_version": expected_state_version,
                        "actual_state_version": actual_version,
                    },
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_409_CONFLICT,
                    details={
                        "error_code": ErrorCodes.CONFLICT.value,
                        "expected_state_version": expected_state_version,
                        "actual_state_version": actual_version,
                    },
                )
            target_record = record.model_copy(update={"state_version": actual_version + 1})
        if record.created_by is not None:
            _ = parse_prefixed_uuid7(record.created_by, EntityPrefix.USER)
        virtual_created_at = _extract_uuid7_timestamp(record.id, EntityPrefix.EXECUTION)
        reconstituted = ExecutionRecord.model_validate(
            target_record.model_copy(update={"created_at": virtual_created_at}).model_dump(
                mode="json",
                exclude_none=True,
            ),
            strict=False,
        )
        self._store.executions[record.id] = reconstituted
        return record.id

    async def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        """Retrieve an ExecutionRecord by execution_id.

        Args:
            execution_id: Canonical exe_<uuid7_hex> execution identifier.

        Returns:
            Stored ExecutionRecord or None if not found.
        """
        _ = parse_prefixed_uuid7(execution_id, EntityPrefix.EXECUTION)
        if execution_id in self._store.executions:
            return self._store.executions[execution_id]
        return None

    async def list_executions(self) -> list[ExecutionRecord]:
        """List all persisted ExecutionRecord entities ordered by created_at descending.

        Returns:
            List of ExecutionRecord domain models.
        """
        records = list(self._store.executions.values())
        records.sort(key=lambda r: r.created_at, reverse=True)
        return records

    async def list_executions_filtered(
        self,
        *,
        organization_id: str | None = None,
        created_by: str | None = None,
        workflow_id: str | None = None,
        status: ExecutionStatus | None = None,
        limit: int = 100,
    ) -> list[ExecutionRecord]:
        """List ExecutionRecord entities filtered by indexed attributes and ordered by id DESC.

        Args:
            organization_id: Optional canonical org_<uuid7_hex> organization filter.
            created_by: Optional canonical usr_<uuid7_hex> creator filter.
            workflow_id: Optional canonical wor_<uuid7_hex> workflow filter.
            status: Optional ExecutionStatus filter.
            limit: Maximum number of records to return.

        Returns:
            List of matching ExecutionRecord models ordered by id DESC.
        """
        if organization_id is not None:
            _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORGANIZATION)
        if created_by is not None:
            _ = parse_prefixed_uuid7(created_by, EntityPrefix.USER)
        if workflow_id is not None:
            _ = parse_prefixed_uuid7(workflow_id, EntityPrefix.WORKFLOW)
        if limit <= 0:
            return []
        matched = list(self._store.executions.values())
        if organization_id is not None:
            matched = [r for r in matched if r.organization_id == organization_id]
        if created_by is not None:
            matched = [r for r in matched if r.created_by == created_by]
        if workflow_id is not None:
            matched = [r for r in matched if r.workflow_id == workflow_id]
        if status is not None:
            matched = [r for r in matched if r.status == status]
        matched.sort(key=lambda r: parse_prefixed_uuid7(r.id, EntityPrefix.EXECUTION), reverse=True)
        return matched[:limit]

    @staticmethod
    def _normalize_optional_org_filter(organization_id: str | None) -> str | None:
        """Normalize an optional organization identifier, coercing 'SYSTEM'/'system' sentinels to None."""
        if organization_id is None:
            return None
        trimmed = organization_id.strip()
        if not trimmed or trimmed.upper() == "SYSTEM":
            return None
        _ = parse_prefixed_uuid7(trimmed, EntityPrefix.ORGANIZATION)
        return trimmed

    @staticmethod
    def _normalize_optional_user_filter(user_id: str | None) -> str | None:
        """Normalize an optional user identifier, coercing 'system' sentinels to None."""
        if user_id is None:
            return None
        trimmed = user_id.strip()
        if not trimmed or trimmed.lower() == "system":
            return None
        _ = parse_prefixed_uuid7(trimmed, EntityPrefix.USER)
        return trimmed

    async def insert_audit_log(self, record: AuditLogRecord) -> str:
        """Insert an immutable AuditLogRecord into the append-only in-memory audit_logs table.

        Args:
            record: Validated AuditLogRecord domain model.

        Returns:
            Canonical aud_<uuid7_hex> identifier inserted.
        """
        _ = parse_prefixed_uuid7(record.id, EntityPrefix.AUDIT_LOG)
        norm_org = self._normalize_optional_org_filter(record.organization_id)
        norm_actor = self._normalize_optional_user_filter(record.actor_id)
        if record.execution_id is not None:
            _ = parse_prefixed_uuid7(record.execution_id, EntityPrefix.EXECUTION)
        if record.id in self._store.audit_logs:
            msg = f"AuditLogRecord '{record.id}' already exists in append-only audit_logs."
            logger.error(
                "[InMemoryEntityAdapter] %s: %s",
                ErrorCodes.CONFLICT.name,
                msg,
                extra={"error_code": ErrorCodes.CONFLICT.value, "entity_id": record.id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_409_CONFLICT,
                details={"error_code": ErrorCodes.CONFLICT.value, "entity_id": record.id},
            )
        normalized_record = record.model_copy(
            update={
                "organization_id": norm_org,
                "actor_id": norm_actor,
                "created_at": _extract_uuid7_timestamp(record.id, EntityPrefix.AUDIT_LOG),
            }
        )
        self._store.audit_logs[record.id] = normalized_record
        return record.id

    async def list_audit_logs(
        self,
        *,
        organization_id: str | None = None,
        actor_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        """List AuditLogRecord entries ordered newest-first with optional filters.

        Args:
            organization_id: Optional organization filter.
            actor_id: Optional actor user filter.
            event_type: Optional event_type string filter.
            limit: Maximum number of rows to return.

        Returns:
            List of matching AuditLogRecord instances ordered by id DESC.
        """
        if limit <= 0:
            return []
        matched = list(self._store.audit_logs.values())
        if organization_id is not None:
            norm_org = self._normalize_optional_org_filter(organization_id)
            matched = [r for r in matched if r.organization_id == norm_org]
        if actor_id is not None:
            norm_actor = self._normalize_optional_user_filter(actor_id)
            matched = [r for r in matched if r.actor_id == norm_actor]
        if event_type is not None:
            matched = [r for r in matched if r.event_type == event_type]
        matched.sort(key=lambda r: parse_prefixed_uuid7(r.id, EntityPrefix.AUDIT_LOG), reverse=True)
        return matched[:limit]

    async def insert_usage_record(self, record: UsageRecord) -> str:
        """Insert an immutable UsageRecord into the append-only in-memory usage_records table.

        Args:
            record: Validated UsageRecord domain model.

        Returns:
            Canonical usg_<uuid7_hex> identifier inserted.
        """
        _ = parse_prefixed_uuid7(record.id, EntityPrefix.USAGE_RECORD)
        norm_org = self._normalize_optional_org_filter(record.org_id)
        norm_usr = self._normalize_optional_user_filter(record.user_id)
        if record.execution_id is not None:
            _ = parse_prefixed_uuid7(record.execution_id, EntityPrefix.EXECUTION)
        if record.id in self._store.usage_records:
            msg = f"UsageRecord '{record.id}' already exists in append-only usage_records."
            logger.error(
                "[InMemoryEntityAdapter] %s: %s",
                ErrorCodes.CONFLICT.name,
                msg,
                extra={"error_code": ErrorCodes.CONFLICT.value, "entity_id": record.id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_409_CONFLICT,
                details={"error_code": ErrorCodes.CONFLICT.value, "entity_id": record.id},
            )
        resolved_org = norm_org if norm_org is not None else "system"
        resolved_usr = norm_usr if norm_usr is not None else "system"
        normalized_record = record.model_copy(
            update={
                "org_id": resolved_org,
                "user_id": resolved_usr,
                "timestamp": _extract_uuid7_timestamp(record.id, EntityPrefix.USAGE_RECORD),
            }
        )
        self._store.usage_records[record.id] = normalized_record
        return record.id

    async def list_usage_records(
        self,
        *,
        organization_id: str | None = None,
        user_id: str | None = None,
        since: datetime | None = None,
    ) -> list[UsageRecord]:
        """List UsageRecord entries ordered chronologically with optional filters.

        Args:
            organization_id: Optional organization filter.
            user_id: Optional user filter.
            since: Optional UTC timestamp lower bound.

        Returns:
            List of matching UsageRecord instances ordered by id ASC.
        """
        matched = list(self._store.usage_records.values())
        if organization_id is not None:
            norm_org = self._normalize_optional_org_filter(organization_id)
            expected_org = norm_org if norm_org is not None else "system"
            matched = [r for r in matched if r.org_id == expected_org]
        if user_id is not None:
            norm_usr = self._normalize_optional_user_filter(user_id)
            expected_usr = norm_usr if norm_usr is not None else "system"
            matched = [r for r in matched if r.user_id == expected_usr]
        if since is not None:
            matched = [r for r in matched if r.timestamp >= since]
        matched.sort(key=lambda r: parse_prefixed_uuid7(r.id, EntityPrefix.USAGE_RECORD))
        return matched

    async def aggregate_organization_usage(
        self,
        organization_id: str | None = None,
        since: datetime | None = None,
    ) -> UsageRollupSummaryDTO:
        """Compute FinOps token and USD rollups over in-memory usage_records.

        Args:
            organization_id: Optional organization filter or None for global system rollup.
            since: Optional UTC timestamp lower bound.

        Returns:
            Aggregated UsageRollupSummaryDTO instance.
        """
        matched = await self.list_usage_records(organization_id=organization_id, since=since)
        return UsageRollupSummaryDTO(
            organization_id=organization_id,
            total_prompt_tokens=sum(r.input_tokens for r in matched),
            total_completion_tokens=sum(r.output_tokens for r in matched),
            total_cached_tokens=sum(r.cached_tokens for r in matched),
            total_reasoning_tokens=sum(r.reasoning_tokens for r in matched),
            total_cache_creation_input_tokens=sum(r.cache_creation_input_tokens for r in matched),
            total_cost_usd=sum(r.cost_usd for r in matched),
            total_estimated_savings_usd=sum(r.estimated_savings_usd for r in matched),
            record_count=len(matched),
        )

    async def seed_collection_batch(
        self,
        collection_name: str,
        items: Sequence[BaseModel],
    ) -> int:
        """Batch-upsert a validated seed collection in memory.

        Args:
            collection_name: Canonical collection or table name ('model_registries', 'mcp_gateways', etc.).
            items: Sequence of validated Pydantic domain models to persist.

        Returns:
            Number of rows persisted into the target table.

        Raises:
            AppException: With VALIDATION_FAILED if collection_name is not an allowlisted seed table.
        """
        canonical = collection_name
        allowed = {
            "organizations",
            "users",
            "invitations",
            "tenant_secrets",
            "execution_assignments",
            "model_registries",
            "mcp_gateways",
            "prompt_blocks",
            "task_briefs",
            "steps",
            "workflows",
            "output_profiles",
            "executions",
            "report_artifacts",
            "report_binaries",
            "audit_logs",
            "usage_records",
        }
        if canonical not in allowed:
            msg = f"Unsupported seed collection '{collection_name}'."
            logger.error(
                "[InMemoryEntityAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "collection_name": collection_name},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        expected_types: dict[str, tuple[type[BaseModel], ...]] = {
            "organizations": (Organization,),
            "users": (User,),
            "invitations": (Invitation,),
            "tenant_secrets": (TenantSecretDTO,),
            "execution_assignments": (ExecutionAssignment,),
            "model_registries": (SystemConfigModelRegistry,),
            "mcp_gateways": (SystemConfigMCPGateways,),
            "prompt_blocks": (
                MatrixPromptBlock,
                SystemRulePromptBlock,
                PersonaPromptBlock,
                ProtocolPromptBlock,
            ),
            "task_briefs": (TaskBrief,),
            "steps": (Step,),
            "workflows": (Workflow,),
            "output_profiles": (OutputProfile,),
            "executions": (ExecutionRecord,),
            "report_artifacts": (ReportArtifact,),
            "report_binaries": (ReportBinaryPayloadDTO,),
            "audit_logs": (AuditLogRecord,),
            "usage_records": (UsageRecord,),
        }
        for item in items:
            if not isinstance(item, expected_types[canonical]):
                msg = f"Item type '{type(item).__name__}' does not match target table '{canonical}'."
                logger.error(
                    "[InMemoryEntityAdapter] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        if canonical == "executions":
            for item in items:
                if isinstance(item, ExecutionRecord):
                    await self.save_execution(item)
            return len(items)

        if canonical == "report_binaries":
            for item in items:
                if isinstance(item, ReportBinaryPayloadDTO):
                    await self.save_report_binary(item)
            return len(items)

        if canonical == "audit_logs":
            for item in items:
                if isinstance(item, AuditLogRecord):
                    await self.insert_audit_log(item)
            return len(items)

        if canonical == "usage_records":
            for item in items:
                if isinstance(item, UsageRecord):
                    await self.insert_usage_record(item)
            return len(items)

        table_bucket = self._store.seed_tables[canonical]
        for idx, item in enumerate(items):
            if isinstance(item, Step):
                self._store.step_criteria_blocks[item.id] = tuple(item.criteria_block_ids)
                table_bucket[item.id] = item
            elif isinstance(item, Workflow):
                dedup_steps: list[str] = []
                seen_steps: set[str] = set()
                for rule in item.steps:
                    if rule.task_blueprint not in seen_steps:
                        seen_steps.add(rule.task_blueprint)
                        dedup_steps.append(rule.task_blueprint)
                self._store.workflow_step_refs[item.id] = tuple(dedup_steps)
                table_bucket[item.id] = item
            elif isinstance(item, ReportArtifact):
                normalized_art = item.model_copy(
                    update={"created_at": _extract_uuid7_timestamp(item.id, EntityPrefix.REPORT)}
                )
                table_bucket[item.id] = normalized_art
            else:
                dumped = item.model_dump(mode="json")
                raw_id = dumped["id"] if "id" in dumped else f"{canonical}_{idx}"
                table_bucket[str(raw_id)] = item
        return len(items)

    async def verify_seed_table_counts(
        self,
        expected_counts: Mapping[str, int],
    ) -> dict[str, int]:
        """Query row counts across all core tables and assert seed materialization.

        Args:
            expected_counts: Mapping of collection/table name to minimum expected row count.

        Returns:
            Dictionary mapping each of the table names to its row count.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED or VALIDATION_FAILED if any table fails verification.
        """
        counts: dict[str, int] = {
            "organizations": len(self._store.seed_tables["organizations"]),
            "users": len(self._store.seed_tables["users"]),
            "tenant_secrets": len(self._store.seed_tables["tenant_secrets"]),
            "model_registries": len(self._store.seed_tables["model_registries"]),
            "mcp_gateways": len(self._store.seed_tables["mcp_gateways"]),
            "prompt_blocks": len(self._store.seed_tables["prompt_blocks"]),
            "task_briefs": len(self._store.seed_tables["task_briefs"]),
            "steps": len(self._store.seed_tables["steps"]),
            "workflows": len(self._store.seed_tables["workflows"]),
            "output_profiles": len(self._store.seed_tables["output_profiles"]),
            "executions": len(self._store.executions),
            "report_artifacts": len(self._store.seed_tables["report_artifacts"]),
            "report_binaries": len(self._store.report_binaries),
        }
        for key, min_expected in expected_counts.items():
            target_table = key
            if target_table not in counts:
                msg = f"Unknown table '{target_table}' in verify_seed_table_counts."
                logger.error(
                    "[InMemoryEntityAdapter] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            if counts[target_table] < min_expected:
                msg = (
                    f"Seed count verification failed for table '{target_table}': "
                    f"expected >= {min_expected}, got {counts[target_table]}."
                )
                logger.error(
                    "[InMemoryEntityAdapter] %s: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "table": target_table},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "table": target_table},
                )
        return counts

    def _delete_seed_row(self, table: str, entity_id: str, prefix: EntityPrefix) -> bool:
        """Delete an entity row from a seed_tables bucket by canonical or raw UUID key."""
        ent_uuid = parse_prefixed_uuid7(entity_id, prefix)
        raw_uuid_key = str(ent_uuid)
        deleted = False
        if entity_id in self._store.seed_tables[table]:
            del self._store.seed_tables[table][entity_id]
            deleted = True
        if raw_uuid_key in self._store.seed_tables[table]:
            del self._store.seed_tables[table][raw_uuid_key]
            deleted = True
        return deleted

    def _cascade_delete_organization_children(self, org_id: str) -> None:
        """Cascade-delete tenant-scoped child entities matching org_id in memory."""
        for table in (
            "users",
            "invitations",
            "tenant_secrets",
            "mcp_gateways",
            "execution_assignments",
            "prompt_blocks",
            "task_briefs",
            "steps",
            "workflows",
            "output_profiles",
        ):
            bucket = self._store.seed_tables[table]
            keys_to_drop = [
                k
                for k, v in bucket.items()
                if isinstance(
                    v,
                    (
                        User,
                        Invitation,
                        TenantSecretDTO,
                        SystemConfigMCPGateways,
                        ExecutionAssignment,
                        MatrixPromptBlock,
                        PersonaPromptBlock,
                        ProtocolPromptBlock,
                        SystemRulePromptBlock,
                        TaskBrief,
                        Step,
                        Workflow,
                        OutputProfile,
                    ),
                )
                and v.organization_id == org_id
            ]
            for k in keys_to_drop:
                del bucket[k]

        deleted_exec_ids = [eid for eid, rec in self._store.executions.items() if rec.organization_id == org_id]
        for eid in deleted_exec_ids:
            del self._store.executions[eid]
            self._cascade_delete_execution_children(eid)

        audit_keys = [aid for aid, rec in self._store.audit_logs.items() if rec.organization_id == org_id]
        for aid in audit_keys:
            del self._store.audit_logs[aid]

        usage_keys = [uid for uid, rec in self._store.usage_records.items() if rec.org_id == org_id]
        for uid in usage_keys:
            del self._store.usage_records[uid]

    def _cascade_delete_execution_children(self, execution_id: str) -> None:
        """Cascade-delete report_artifacts, report_binaries, and graph elements for an execution."""
        rep_bucket = self._store.seed_tables["report_artifacts"]
        rep_keys = [
            rk for rk, rv in rep_bucket.items() if isinstance(rv, ReportArtifact) and rv.execution_id == execution_id
        ]
        for rk in rep_keys:
            item = rep_bucket[rk]
            rep_id = item.id if isinstance(item, ReportArtifact) else rk
            del rep_bucket[rk]
            if rep_id in self._store.report_binaries:
                del self._store.report_binaries[rep_id]
            if rep_id in self._store.report_has_pdf:
                del self._store.report_has_pdf[rep_id]

        node_keys = [nid for nid, entry in self._store.nodes.items() if entry.node.run_id == execution_id]
        for nid in node_keys:
            del self._store.nodes[nid]

        edge_keys = [eid for eid, edge in self._store.edges.items() if edge.run_id == execution_id]
        for eid in edge_keys:
            del self._store.edges[eid]

    async def delete_organization(self, org_id: str) -> bool:
        """Delete an Organization by primary key and cascade-delete child tenant records."""
        deleted = self._delete_seed_row("organizations", org_id, EntityPrefix.ORGANIZATION)
        self._cascade_delete_organization_children(org_id)
        return deleted

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a User by case-insensitive email match in memory."""
        normalized_email = email.strip().lower()
        if not normalized_email:
            return None
        for item in self._store.seed_tables["users"].values():
            if isinstance(item, User) and str(item.email).lower() == normalized_email:
                return item
        return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a User by primary key in memory."""
        return self._delete_seed_row("users", user_id, EntityPrefix.USER)

    async def delete_invitation(self, invitation_id: str) -> bool:
        """Delete an Invitation by primary key in memory."""
        return self._delete_seed_row("invitations", invitation_id, EntityPrefix.INVITATION)

    def _cascade_delete_mcp_gateway_secrets(self, gateway_id: str, gateway_uuid: uuid.UUID) -> None:
        """Cascade-delete tenant_secrets bound to a deleted MCP gateway (ON DELETE CASCADE)."""
        secret_bucket = self._store.seed_tables["tenant_secrets"]
        keys_to_drop: list[str] = []
        for k, entry in secret_bucket.items():
            if isinstance(entry, TenantSecretDTO):
                if entry.scope == SecretScope.MCP_GATEWAY and entry.target_identifier == gateway_id:
                    keys_to_drop.append(k)
            elif isinstance(entry, Sequence) and len(entry) >= 5:
                if entry[2] == gateway_uuid or str(entry[2]) == str(gateway_uuid) or str(entry[4]) == gateway_id:
                    keys_to_drop.append(k)
        for k in keys_to_drop:
            del secret_bucket[k]

    def _assert_model_registry_not_referenced(self, registry_id: str, registry_uuid: uuid.UUID) -> None:
        """Enforce ON DELETE RESTRICT for workflows.model_registry_id."""
        for entry in self._store.seed_tables["workflows"].values():
            if isinstance(entry, Workflow) and entry.model_registry_id == registry_id:
                msg = f"Model registry '{registry_id}' is referenced by workflow '{entry.id}'."
                logger.error(
                    "[InMemoryEntityAdapter] %s: %s",
                    ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                    msg,
                    extra={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, "entity_id": registry_id},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                )
            if (
                isinstance(entry, Sequence)
                and len(entry) > 10
                and (entry[10] == registry_uuid or str(entry[10]) == str(registry_uuid))
            ):
                msg = f"Model registry '{registry_id}' is referenced by a persisted workflow row."
                logger.error(
                    "[InMemoryEntityAdapter] %s: %s",
                    ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                    msg,
                    extra={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, "entity_id": registry_id},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                )

    def _assert_mcp_gateway_not_referenced(self, gateway_id: str, gateway_uuid: uuid.UUID) -> None:
        """Enforce ON DELETE RESTRICT for workflows.mcp_gateway_id."""
        for entry in self._store.seed_tables["workflows"].values():
            if isinstance(entry, Workflow) and entry.mcp_gateway_id == gateway_id:
                msg = f"MCP gateway '{gateway_id}' is referenced by workflow '{entry.id}'."
                logger.error(
                    "[InMemoryEntityAdapter] %s: %s",
                    ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                    msg,
                    extra={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, "entity_id": gateway_id},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                )
            if (
                isinstance(entry, Sequence)
                and len(entry) > 9
                and entry[9] is not None
                and (entry[9] == gateway_uuid or str(entry[9]) == str(gateway_uuid))
            ):
                msg = f"MCP gateway '{gateway_id}' is referenced by a persisted workflow row."
                logger.error(
                    "[InMemoryEntityAdapter] %s: %s",
                    ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                    msg,
                    extra={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, "entity_id": gateway_id},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                )

    async def upsert_model_registry(self, registry: SystemConfigModelRegistry) -> str:
        """Upsert a SystemConfigModelRegistry in memory."""
        _ = parse_prefixed_uuid7(registry.id, EntityPrefix.MODEL_REGISTRY)
        self._store.seed_tables["model_registries"][registry.id] = registry
        return registry.id

    async def get_model_registry(self, registry_id: str) -> SystemConfigModelRegistry | None:
        """Retrieve a SystemConfigModelRegistry by registry_id in memory."""
        _ = parse_prefixed_uuid7(registry_id, EntityPrefix.MODEL_REGISTRY)
        if registry_id in self._store.seed_tables["model_registries"]:
            item = self._store.seed_tables["model_registries"][registry_id]
            if isinstance(item, SystemConfigModelRegistry):
                return item
        return None

    async def list_model_registries(self) -> list[SystemConfigModelRegistry]:
        """List all persisted SystemConfigModelRegistry entities in memory."""
        registries = [
            item
            for item in self._store.seed_tables["model_registries"].values()
            if isinstance(item, SystemConfigModelRegistry)
        ]
        registries.sort(key=lambda r: r.id)
        return registries

    async def delete_model_registry(self, registry_id: str) -> bool:
        """Delete a SystemConfigModelRegistry by primary key in memory (ON DELETE RESTRICT)."""
        reg_uuid = parse_prefixed_uuid7(registry_id, EntityPrefix.MODEL_REGISTRY)
        self._assert_model_registry_not_referenced(registry_id, reg_uuid)
        return self._delete_seed_row("model_registries", registry_id, EntityPrefix.MODEL_REGISTRY)

    async def upsert_mcp_gateway(self, gateway: SystemConfigMCPGateways) -> str:
        """Upsert a SystemConfigMCPGateways in memory."""
        _ = parse_prefixed_uuid7(gateway.id, EntityPrefix.MCP_GATEWAY)
        _ = parse_prefixed_uuid7(gateway.organization_id, EntityPrefix.ORGANIZATION)
        self._store.seed_tables["mcp_gateways"][gateway.id] = gateway
        return gateway.id

    async def get_mcp_gateway(self, gateway_id: str) -> SystemConfigMCPGateways | None:
        """Retrieve a SystemConfigMCPGateways by gateway_id in memory."""
        _ = parse_prefixed_uuid7(gateway_id, EntityPrefix.MCP_GATEWAY)
        if gateway_id in self._store.seed_tables["mcp_gateways"]:
            item = self._store.seed_tables["mcp_gateways"][gateway_id]
            if isinstance(item, SystemConfigMCPGateways):
                return item
        return None

    async def list_mcp_gateways(self) -> list[SystemConfigMCPGateways]:
        """List all persisted SystemConfigMCPGateways entities in memory."""
        gateways = [
            item
            for item in self._store.seed_tables["mcp_gateways"].values()
            if isinstance(item, SystemConfigMCPGateways)
        ]
        gateways.sort(key=lambda g: g.id)
        return gateways

    async def delete_mcp_gateway(self, gateway_id: str) -> bool:
        """Delete a SystemConfigMCPGateways by primary key in memory (RESTRICT on workflows, CASCADE on secrets)."""
        gw_uuid = parse_prefixed_uuid7(gateway_id, EntityPrefix.MCP_GATEWAY)
        self._assert_mcp_gateway_not_referenced(gateway_id, gw_uuid)
        deleted = self._delete_seed_row("mcp_gateways", gateway_id, EntityPrefix.MCP_GATEWAY)
        if deleted:
            self._cascade_delete_mcp_gateway_secrets(gateway_id, gw_uuid)
        return deleted

    async def upsert_prompt_block(self, block: PromptBlock) -> str:
        """Upsert a polymorphic PromptBlock in memory."""
        _ = parse_prefixed_uuid7(block.id, EntityPrefix.PROMPT_BLOCK)
        _ = parse_prefixed_uuid7(block.organization_id, EntityPrefix.ORGANIZATION)
        self._store.seed_tables["prompt_blocks"][block.id] = block
        return block.id

    async def get_prompt_block(self, block_id: str) -> PromptBlock | None:
        """Retrieve a PromptBlock by block_id in memory."""
        _ = parse_prefixed_uuid7(block_id, EntityPrefix.PROMPT_BLOCK)
        if block_id in self._store.seed_tables["prompt_blocks"]:
            item = self._store.seed_tables["prompt_blocks"][block_id]
            if isinstance(
                item,
                (MatrixPromptBlock, PersonaPromptBlock, ProtocolPromptBlock, SystemRulePromptBlock),
            ):
                return item
        return None

    async def list_prompt_blocks(self) -> list[PromptBlock]:
        """List all persisted PromptBlock entities in memory."""
        blocks: list[PromptBlock] = [
            item
            for item in self._store.seed_tables["prompt_blocks"].values()
            if isinstance(
                item,
                (MatrixPromptBlock, PersonaPromptBlock, ProtocolPromptBlock, SystemRulePromptBlock),
            )
        ]
        blocks.sort(key=lambda b: b.id)
        return blocks

    def _is_prompt_block_referenced(self, block_id: str, block_uuid: uuid.UUID) -> bool:
        """Return True if any persisted step, junction row, or output profile references block_id."""
        for blk_ids in self._store.step_criteria_blocks.values():
            if block_id in blk_ids:
                return True
        raw_uuid_str = str(block_uuid)
        for step_entry in self._store.seed_tables["steps"].values():
            if isinstance(step_entry, Step):
                if (
                    block_id
                    in (
                        step_entry.role_block_id,
                        step_entry.extraction_protocol_block_id,
                        step_entry.execution_persona_block_id,
                    )
                    or block_id in step_entry.criteria_block_ids
                ):
                    return True
            elif isinstance(step_entry, Sequence) and len(step_entry) >= 10:
                for col_idx in (7, 8, 9):
                    col_val = step_entry[col_idx]
                    if col_val is not None and (col_val == block_uuid or str(col_val) == raw_uuid_str):
                        return True
        for prf_entry in self._store.seed_tables["output_profiles"].values():
            if isinstance(prf_entry, OutputProfile):
                if block_id in (prf_entry.variance_target_block, prf_entry.user_role_target_block):
                    return True
            elif isinstance(prf_entry, Sequence) and len(prf_entry) >= 40:
                for col_idx in (38, 39):
                    col_val = prf_entry[col_idx]
                    if col_val is not None and (col_val == block_uuid or str(col_val) == raw_uuid_str):
                        return True
        return False

    def _is_step_referenced(self, step_id: str) -> bool:
        """Return True if any workflow or workflow_step_refs junction row references step_id."""
        for stp_ids in self._store.workflow_step_refs.values():
            if step_id in stp_ids:
                return True
        for wf_entry in self._store.seed_tables["workflows"].values():
            if isinstance(wf_entry, Workflow) and any(r.task_blueprint == step_id for r in wf_entry.steps):
                return True
        return False

    def _is_output_profile_referenced(self, profile_id: str, profile_uuid: uuid.UUID) -> bool:
        """Return True if any workflow, report_artifact, or execution_assignment references profile_id."""
        raw_uuid_str = str(profile_uuid)
        for wf_entry in self._store.seed_tables["workflows"].values():
            if isinstance(wf_entry, Workflow) and wf_entry.default_profile_id == profile_id:
                return True
            if (
                isinstance(wf_entry, Sequence)
                and len(wf_entry) > 8
                and wf_entry[8] is not None
                and (wf_entry[8] == profile_uuid or str(wf_entry[8]) == raw_uuid_str)
            ):
                return True
        for rep_entry in self._store.seed_tables["report_artifacts"].values():
            if isinstance(rep_entry, ReportArtifact) and rep_entry.profile_id == profile_id:
                return True
            if (
                isinstance(rep_entry, Sequence)
                and len(rep_entry) > 3
                and rep_entry[3] is not None
                and (rep_entry[3] == profile_uuid or str(rep_entry[3]) == raw_uuid_str)
            ):
                return True
        for asg_entry in self._store.seed_tables["execution_assignments"].values():
            if isinstance(asg_entry, ExecutionAssignment) and asg_entry.output_profile_id == profile_id:
                return True
            if (
                isinstance(asg_entry, Sequence)
                and len(asg_entry) > 7
                and asg_entry[7] is not None
                and (asg_entry[7] == profile_uuid or str(asg_entry[7]) == raw_uuid_str)
            ):
                return True
        return False

    def _is_task_brief_referenced(self, brief_id: str, brief_uuid: uuid.UUID) -> bool:
        """Return True if any execution_assignment references brief_id (ON DELETE RESTRICT)."""
        raw_uuid_str = str(brief_uuid)
        for asg_entry in self._store.seed_tables["execution_assignments"].values():
            if isinstance(asg_entry, ExecutionAssignment) and asg_entry.task_brief_id == brief_id:
                return True
            if (
                isinstance(asg_entry, Sequence)
                and len(asg_entry) > 8
                and asg_entry[8] is not None
                and (asg_entry[8] == brief_uuid or str(asg_entry[8]) == raw_uuid_str)
            ):
                return True
        return False

    def _is_workflow_referenced(self, workflow_id: str, workflow_uuid: uuid.UUID) -> bool:
        """Return True if any execution, report_artifact, or execution_assignment references workflow_id."""
        raw_uuid_str = str(workflow_uuid)
        for exec_record in self._store.executions.values():
            if exec_record.workflow_id == workflow_id:
                return True
        for rep_entry in self._store.seed_tables["report_artifacts"].values():
            if isinstance(rep_entry, ReportArtifact) and rep_entry.workflow_id == workflow_id:
                return True
            if (
                isinstance(rep_entry, Sequence)
                and len(rep_entry) > 2
                and rep_entry[2] is not None
                and (rep_entry[2] == workflow_uuid or str(rep_entry[2]) == raw_uuid_str)
            ):
                return True
        for asg_entry in self._store.seed_tables["execution_assignments"].values():
            if isinstance(asg_entry, ExecutionAssignment) and asg_entry.workflow_id == workflow_id:
                return True
            if (
                isinstance(asg_entry, Sequence)
                and len(asg_entry) > 6
                and asg_entry[6] is not None
                and (asg_entry[6] == workflow_uuid or str(asg_entry[6]) == raw_uuid_str)
            ):
                return True
        return False

    async def delete_prompt_block(self, block_id: str) -> bool:
        """Delete a PromptBlock by primary key in memory (ON DELETE RESTRICT)."""
        blk_uuid = parse_prefixed_uuid7(block_id, EntityPrefix.PROMPT_BLOCK)
        if self._is_prompt_block_referenced(block_id, blk_uuid):
            msg = f"Prompt block '{block_id}' is referenced by a persisted step or output profile."
            logger.error(
                "[InMemoryEntityAdapter] %s: %s",
                ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                msg,
                extra={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, "entity_id": block_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
            )
        return self._delete_seed_row("prompt_blocks", block_id, EntityPrefix.PROMPT_BLOCK)

    async def delete_task_brief(self, brief_id: str) -> bool:
        """Delete a TaskBrief by primary key in memory (ON DELETE RESTRICT)."""
        tbr_uuid = parse_prefixed_uuid7(brief_id, EntityPrefix.TASK_BRIEF)
        if self._is_task_brief_referenced(brief_id, tbr_uuid):
            msg = f"Task brief '{brief_id}' is referenced by a persisted execution assignment."
            logger.error(
                "[InMemoryEntityAdapter] %s: %s",
                ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                msg,
                extra={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, "entity_id": brief_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
            )
        return self._delete_seed_row("task_briefs", brief_id, EntityPrefix.TASK_BRIEF)

    async def upsert_output_profile(self, profile: OutputProfile) -> str:
        """Upsert an OutputProfile in memory."""
        _ = parse_prefixed_uuid7(profile.id, EntityPrefix.OUTPUT_PROFILE)
        _ = parse_prefixed_uuid7(profile.workflow_id, EntityPrefix.WORKFLOW)
        _ = parse_prefixed_uuid7(profile.organization_id, EntityPrefix.ORGANIZATION)
        if profile.variance_target_block is not None:
            _ = parse_prefixed_uuid7(profile.variance_target_block, EntityPrefix.PROMPT_BLOCK)
        if profile.user_role_target_block is not None:
            _ = parse_prefixed_uuid7(profile.user_role_target_block, EntityPrefix.PROMPT_BLOCK)
        self._store.seed_tables["output_profiles"][profile.id] = profile
        return profile.id

    async def get_output_profile(self, profile_id: str) -> OutputProfile | None:
        """Retrieve an OutputProfile by profile_id in memory."""
        _ = parse_prefixed_uuid7(profile_id, EntityPrefix.OUTPUT_PROFILE)
        if profile_id in self._store.seed_tables["output_profiles"]:
            item = self._store.seed_tables["output_profiles"][profile_id]
            if isinstance(item, OutputProfile):
                return item
        return None

    async def list_output_profiles(self) -> list[OutputProfile]:
        """List all persisted OutputProfile entities in memory."""
        profiles = [
            item for item in self._store.seed_tables["output_profiles"].values() if isinstance(item, OutputProfile)
        ]
        profiles.sort(key=lambda p: p.id)
        return profiles

    async def delete_output_profile(self, profile_id: str) -> bool:
        """Delete an OutputProfile by primary key in memory (ON DELETE RESTRICT / IMMEDIATE FK)."""
        prf_uuid = parse_prefixed_uuid7(profile_id, EntityPrefix.OUTPUT_PROFILE)
        if self._is_output_profile_referenced(profile_id, prf_uuid):
            msg = f"Output profile '{profile_id}' is referenced by a persisted workflow or report artifact."
            logger.error(
                "[InMemoryEntityAdapter] %s: %s",
                ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                msg,
                extra={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, "entity_id": profile_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
            )
        return self._delete_seed_row("output_profiles", profile_id, EntityPrefix.OUTPUT_PROFILE)

    async def upsert_workflow(self, wf: Workflow) -> str:
        """Upsert a Workflow in memory with SQL OCC version checking and workflow_step_refs sync."""
        wf_uuid = parse_prefixed_uuid7(wf.id, EntityPrefix.WORKFLOW)
        _ = parse_prefixed_uuid7(wf.model_registry_id, EntityPrefix.MODEL_REGISTRY)
        if wf.default_profile_id is not None:
            _ = parse_prefixed_uuid7(wf.default_profile_id, EntityPrefix.OUTPUT_PROFILE)
        if wf.mcp_gateway_id is not None:
            _ = parse_prefixed_uuid7(wf.mcp_gateway_id, EntityPrefix.MCP_GATEWAY)
        _ = parse_prefixed_uuid7(wf.organization_id, EntityPrefix.ORGANIZATION)

        dedup_steps: list[str] = []
        seen_steps: set[str] = set()
        for rule in wf.steps:
            _ = parse_prefixed_uuid7(rule.task_blueprint, EntityPrefix.STEP)
            if rule.task_blueprint not in seen_steps:
                seen_steps.add(rule.task_blueprint)
                dedup_steps.append(rule.task_blueprint)

        wf_bucket = self._store.seed_tables["workflows"]
        raw_uuid_key = str(wf_uuid)
        existing_entry: _SeedRowEntry | None = None
        if wf.id in wf_bucket:
            existing_entry = wf_bucket[wf.id]
        elif raw_uuid_key in wf_bucket:
            existing_entry = wf_bucket[raw_uuid_key]

        persisted_wf = wf
        if existing_entry is not None:
            if isinstance(existing_entry, Workflow):
                actual_version = existing_entry.version
            elif isinstance(existing_entry, BaseModel):
                raise TypeError(f"Unexpected BaseModel in workflows bucket: {type(existing_entry).__name__}")
            else:
                actual_version = int(str(existing_entry[5]))
            if actual_version != wf.version:
                msg = f"Optimistic concurrency conflict for workflow '{wf.id}' at expected version={wf.version}."
                logger.error(
                    "[InMemoryEntityAdapter] %s: %s",
                    ErrorCodes.CONFLICT.name,
                    msg,
                    extra={
                        "error_code": ErrorCodes.CONFLICT.value,
                        "workflow_id": wf.id,
                        "expected_version": wf.version,
                        "actual_version": actual_version,
                    },
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_409_CONFLICT,
                    details={
                        "error_code": ErrorCodes.CONFLICT.value,
                        "workflow_id": wf.id,
                        "expected_version": wf.version,
                    },
                )
            persisted_wf = wf.model_copy(update={"version": actual_version + 1})
            if raw_uuid_key in wf_bucket:
                del wf_bucket[raw_uuid_key]

        wf_bucket[wf.id] = persisted_wf
        self._store.workflow_step_refs[wf.id] = tuple(dedup_steps)
        return wf.id

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Retrieve a Workflow by workflow_id in memory."""
        _ = parse_prefixed_uuid7(workflow_id, EntityPrefix.WORKFLOW)
        if workflow_id in self._store.seed_tables["workflows"]:
            item = self._store.seed_tables["workflows"][workflow_id]
            if isinstance(item, Workflow):
                return item
        return None

    async def list_workflows(self) -> list[Workflow]:
        """List all persisted Workflow entities in memory."""
        workflows = [item for item in self._store.seed_tables["workflows"].values() if isinstance(item, Workflow)]
        workflows.sort(key=lambda w: w.id)
        return workflows

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a Workflow by primary key in memory (ON DELETE RESTRICT on runs/assignments)."""
        wf_uuid = parse_prefixed_uuid7(workflow_id, EntityPrefix.WORKFLOW)
        if self._is_workflow_referenced(workflow_id, wf_uuid):
            msg = f"Workflow '{workflow_id}' is referenced by a persisted execution, report, or assignment."
            logger.error(
                "[InMemoryEntityAdapter] %s: %s",
                ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                msg,
                extra={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, "entity_id": workflow_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
            )
        deleted = self._delete_seed_row("workflows", workflow_id, EntityPrefix.WORKFLOW)
        if workflow_id in self._store.workflow_step_refs:
            del self._store.workflow_step_refs[workflow_id]
        if deleted:
            prf_bucket = self._store.seed_tables["output_profiles"]
            prf_keys = [
                pk for pk, pv in prf_bucket.items() if isinstance(pv, OutputProfile) and pv.workflow_id == workflow_id
            ]
            for pk in prf_keys:
                del prf_bucket[pk]
        return deleted

    async def upsert_step(self, step: Step) -> str:
        """Upsert a Step in memory and synchronize step_criteria_blocks."""
        _ = parse_prefixed_uuid7(step.id, EntityPrefix.STEP)
        _ = parse_prefixed_uuid7(step.organization_id, EntityPrefix.ORGANIZATION)
        for blk_id in step.criteria_block_ids:
            _ = parse_prefixed_uuid7(blk_id, EntityPrefix.PROMPT_BLOCK)
        self._store.seed_tables["steps"][step.id] = step
        self._store.step_criteria_blocks[step.id] = tuple(step.criteria_block_ids)
        return step.id

    async def get_step(self, step_id: str) -> Step | None:
        """Retrieve a Step by step_id in memory."""
        _ = parse_prefixed_uuid7(step_id, EntityPrefix.STEP)
        if step_id in self._store.seed_tables["steps"]:
            item = self._store.seed_tables["steps"][step_id]
            if isinstance(item, Step):
                return item
        return None

    async def list_steps(self) -> list[Step]:
        """List all persisted Step entities in memory."""
        steps = [item for item in self._store.seed_tables["steps"].values() if isinstance(item, Step)]
        steps.sort(key=lambda s: s.id)
        return steps

    async def delete_step(self, step_id: str) -> bool:
        """Delete a Step by primary key in memory (ON DELETE RESTRICT)."""
        _ = parse_prefixed_uuid7(step_id, EntityPrefix.STEP)
        if self._is_step_referenced(step_id):
            msg = f"Step '{step_id}' is referenced by a persisted workflow."
            logger.error(
                "[InMemoryEntityAdapter] %s: %s",
                ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                msg,
                extra={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, "entity_id": step_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
            )
        deleted = self._delete_seed_row("steps", step_id, EntityPrefix.STEP)
        if step_id in self._store.step_criteria_blocks:
            del self._store.step_criteria_blocks[step_id]
        return deleted

    async def update_execution_occ(self, execution_id: str, updates: ExecutionUpdateDTO) -> bool:
        """Apply partial ExecutionUpdateDTO updates to a persisted ExecutionRecord with OCC checking."""
        existing = await self.get_execution(execution_id)
        if existing is None:
            return False
        merged = apply_execution_updates(existing, updates)
        await self.save_execution(merged, expected_state_version=updates.expected_state_version)
        return True

    async def delete_execution(self, execution_id: str) -> bool:
        """Delete an ExecutionRecord by primary key in memory."""
        _ = parse_prefixed_uuid7(execution_id, EntityPrefix.EXECUTION)
        if execution_id not in self._store.executions:
            return False
        del self._store.executions[execution_id]
        self._cascade_delete_execution_children(execution_id)
        return True

    async def upsert_report_artifact(self, artifact: ReportArtifact) -> str:
        """Upsert a ReportArtifact in memory with VIRTUAL created_at timestamp alignment."""
        _ = parse_prefixed_uuid7(artifact.id, EntityPrefix.REPORT)
        _ = parse_prefixed_uuid7(artifact.execution_id, EntityPrefix.EXECUTION)
        _ = parse_prefixed_uuid7(artifact.workflow_id, EntityPrefix.WORKFLOW)
        _ = parse_prefixed_uuid7(artifact.profile_id, EntityPrefix.OUTPUT_PROFILE)
        virtual_created_at = _extract_uuid7_timestamp(artifact.id, EntityPrefix.REPORT)
        self._store.seed_tables["report_artifacts"][artifact.id] = artifact.model_copy(
            update={"created_at": virtual_created_at}
        )
        return artifact.id

    async def get_report_artifact(self, report_id: str) -> ReportArtifact | None:
        """Retrieve a ReportArtifact by report_id in memory."""
        _ = parse_prefixed_uuid7(report_id, EntityPrefix.REPORT)
        if report_id in self._store.seed_tables["report_artifacts"]:
            item = self._store.seed_tables["report_artifacts"][report_id]
            if isinstance(item, ReportArtifact):
                return item
        return None

    async def list_report_artifacts_by_execution(self, execution_id: str) -> list[ReportArtifact]:
        """List all ReportArtifact entities belonging to execution_id ordered newest-first."""
        _ = parse_prefixed_uuid7(execution_id, EntityPrefix.EXECUTION)
        reports = [
            item
            for item in self._store.seed_tables["report_artifacts"].values()
            if isinstance(item, ReportArtifact) and item.execution_id == execution_id
        ]
        reports.sort(key=lambda r: r.created_at, reverse=True)
        return reports

    async def delete_report_artifact(self, report_id: str) -> bool:
        """Delete a ReportArtifact by primary key in memory."""
        deleted = self._delete_seed_row("report_artifacts", report_id, EntityPrefix.REPORT)
        if deleted:
            if report_id in self._store.report_binaries:
                del self._store.report_binaries[report_id]
            if report_id in self._store.report_has_pdf:
                del self._store.report_has_pdf[report_id]
        return deleted


class InMemoryAsyncPgTransaction:
    """In-memory implementation of AsyncPgTransactionProtocol with snapshot rollback."""

    def __init__(
        self,
        store: _InMemoryPostgresStore,
        faults: dict[str, Exception] | None = None,
    ) -> None:
        """Initialize the transaction wrapper around a shared store.

        Args:
            store: Shared _InMemoryPostgresStore instance.
            faults: Optional dictionary of injected faults keyed by operation name.
        """
        self._store: _InMemoryPostgresStore = store
        self._faults: dict[str, Exception] = faults if faults is not None else {}
        self._snapshot: _StoreSnapshot | None = None
        self.active: bool = False

    async def start(self) -> None:
        """Capture a point-in-time snapshot and mark transaction active."""
        self._snapshot = self._store.take_snapshot()
        self.active = True

    async def commit(self) -> None:
        """Commit the active transaction and discard the rollback snapshot."""
        if "tx_commit" in self._faults:
            raise self._faults["tx_commit"]
        self._snapshot = None
        self.active = False

    async def rollback(self) -> None:
        """Restore the store to the pre-transaction snapshot."""
        if "tx_rollback" in self._faults:
            raise self._faults["tx_rollback"]
        if self._snapshot is not None:
            self._store.restore_snapshot(self._snapshot)
        self._snapshot = None
        self.active = False

    async def __aenter__(self) -> Self:
        """Enter the transaction context manager."""
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Commit or roll back upon exiting the transaction context."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()


class InMemoryAsyncPgConnection:
    """Stateful SQL-emulating implementation of AsyncPgConnectionProtocol for PostgresUnitOfWork tests."""

    def __init__(
        self,
        store: _InMemoryPostgresStore,
        faults: dict[str, Exception],
    ) -> None:
        """Initialize the in-memory connection.

        Args:
            store: Shared _InMemoryPostgresStore instance.
            faults: Shared dictionary of injected faults keyed by operation name.
        """
        self._store: _InMemoryPostgresStore = store
        self._faults: dict[str, Exception] = faults
        self._graph: InMemoryGraphAdapter = InMemoryGraphAdapter(store)
        self._entities: InMemoryEntityAdapter = InMemoryEntityAdapter(store)
        self.codecs_registered: set[str] = set()

    def _check_fault(self, operation: str) -> None:
        """Raise an injected exception if a fault is registered for operation.

        Args:
            operation: Logical operation identifier.
        """
        if operation in self._faults:
            raise self._faults[operation]

    async def set_type_codec(
        self,
        typename: str,
        *,
        encoder: Callable[[object], bytes],
        decoder: Callable[[bytes | bytearray | memoryview], object],
        schema: str = "pg_catalog",
        format: str = "binary",
    ) -> None:
        """Register a custom binary wire codec and verify roundtrip sanity.

        Args:
            typename: PostgreSQL type name (specifically 'jsonb').
            encoder: Binary encoder function.
            decoder: Binary decoder function.
            schema: PostgreSQL catalog schema.
            format: Wire format ('binary').
        """
        self._check_fault("set_type_codec")
        _ = (schema, format)
        probe = decoder(encoder({"codec_ok": True}))
        if probe is not None:
            self.codecs_registered.add(typename)

    def transaction(self, *, isolation: str = "repeatable_read") -> AsyncPgTransactionProtocol:
        """Create an InMemoryAsyncPgTransaction for repeatable_read isolation.

        Args:
            isolation: Transaction isolation level string.

        Returns:
            InMemoryAsyncPgTransaction instance.
        """
        self._check_fault("transaction")
        _ = isolation
        return InMemoryAsyncPgTransaction(self._store, self._faults)

    async def execute(self, query: str, *args: object, timeout: float | None = None) -> str:
        """Execute a SQL statement against the in-memory PostgreSQL store.

        Args:
            query: SQL statement string.
            *args: Positional query bind parameters.
            timeout: Optional command timeout in seconds.

        Returns:
            PostgreSQL command status tag string.
        """
        self._check_fault("execute")
        _ = timeout
        normalized = " ".join(query.strip().split()).upper()

        if "RESET QUORUM.CURRENT_ORG" in normalized:
            self._store.current_org_reset_count += 1
            return "RESET"

        if normalized.startswith("SET CONSTRAINTS "):
            return "SET CONSTRAINTS"

        if "SET DEFAULT_TOAST_COMPRESSION" in normalized or "CREATE TABLE" in normalized:
            self._store.migrations_applied += 1
            return "CREATE TABLE"

        if normalized.startswith("TRUNCATE TABLE "):
            for tbl in self._store.seed_tables:
                if f"TRUNCATE TABLE {tbl.upper()}" in normalized:
                    self._store.seed_tables[tbl].clear()
                    if tbl == "steps":
                        self._store.step_criteria_blocks.clear()
                    if tbl == "workflows":
                        self._store.workflow_step_refs.clear()
                    return "TRUNCATE TABLE"
            if "TRUNCATE TABLE STEP_CRITERIA_BLOCKS" in normalized:
                self._store.step_criteria_blocks.clear()
                return "TRUNCATE TABLE"
            if "TRUNCATE TABLE WORKFLOW_STEP_REFS" in normalized:
                self._store.workflow_step_refs.clear()
                return "TRUNCATE TABLE"
            if "TRUNCATE TABLE EXECUTIONS" in normalized:
                self._store.executions.clear()
                self._store.nodes.clear()
                self._store.edges.clear()
                return "TRUNCATE TABLE"
            if "TRUNCATE TABLE REPORT_BINARIES" in normalized:
                self._store.report_binaries.clear()
                return "TRUNCATE TABLE"
            if "TRUNCATE TABLE AUDIT_LOGS" in normalized:
                self._store.audit_logs.clear()
                return "TRUNCATE TABLE"
            if "TRUNCATE TABLE USAGE_RECORDS" in normalized:
                self._store.usage_records.clear()
                return "TRUNCATE TABLE"
            return "TRUNCATE TABLE"

        if "INSERT INTO AUDIT_LOGS" in normalized:
            aud_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            aud_id = format_prefixed_uuid7(aud_uuid, EntityPrefix.AUDIT_LOG)
            if aud_id in self._store.audit_logs:
                raise _InMemorySqlStateError(
                    f"duplicate key value violates unique constraint 'audit_logs_pkey' ({aud_id})",
                    sqlstate="23505",
                )
            audit_row = InMemoryAsyncPgRecord(
                {
                    "id": _to_column_value(args[0]),
                    "organization_id": _to_column_value(args[1]),
                    "actor_id": _to_column_value(args[2]),
                    "execution_id": _to_column_value(args[3]),
                    "event_type": _to_column_value(args[4]),
                    "resource_type": _to_column_value(args[5]),
                    "resource_id": _to_column_value(args[6]),
                    "details": _to_column_value(args[7]),
                    "created_at": _extract_uuid7_timestamp(aud_id, EntityPrefix.AUDIT_LOG),
                }
            )
            hydrated_audit = hydrate_audit_log_row(audit_row)
            self._store.audit_logs[hydrated_audit.id] = hydrated_audit
            return "INSERT 0 1"

        if "INSERT INTO USAGE_RECORDS" in normalized:
            usg_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            usg_id = format_prefixed_uuid7(usg_uuid, EntityPrefix.USAGE_RECORD)
            if usg_id in self._store.usage_records:
                raise _InMemorySqlStateError(
                    f"duplicate key value violates unique constraint 'usage_records_pkey' ({usg_id})",
                    sqlstate="23505",
                )
            usage_row = InMemoryAsyncPgRecord(
                {
                    "id": _to_column_value(args[0]),
                    "organization_id": _to_column_value(args[1]),
                    "user_id": _to_column_value(args[2]),
                    "execution_id": _to_column_value(args[3]),
                    "model_name": _to_column_value(args[4]),
                    "prompt_tokens": _to_column_value(args[5]),
                    "completion_tokens": _to_column_value(args[6]),
                    "cached_tokens": _to_column_value(args[7]),
                    "reasoning_tokens": _to_column_value(args[8]),
                    "cache_creation_input_tokens": _to_column_value(args[9]),
                    "latency_ms": _to_column_value(args[10]),
                    "finish_reason": _to_column_value(args[11]),
                    "system_fingerprint": _to_column_value(args[12]),
                    "cost_usd": _to_column_value(args[13]),
                    "estimated_savings_usd": _to_column_value(args[14]),
                    "created_at": _extract_uuid7_timestamp(usg_id, EntityPrefix.USAGE_RECORD),
                }
            )
            hydrated_usage = hydrate_usage_record_row(usage_row)
            self._store.usage_records[hydrated_usage.id] = hydrated_usage
            return "INSERT 0 1"

        if "INSERT INTO REPORT_BINARIES" in normalized:
            report_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            report_id = format_prefixed_uuid7(report_uuid, EntityPrefix.REPORT)
            mime_type = str(args[1])
            pdf_bytes = bytes(args[2]) if isinstance(args[2], (bytes, bytearray, memoryview)) else b""
            size_bytes = int(str(args[3]))
            created_at = (
                args[4]
                if len(args) > 4 and isinstance(args[4], datetime)
                else _extract_uuid7_timestamp(report_id, EntityPrefix.REPORT)
            )
            await self._entities.save_report_binary(
                ReportBinaryPayloadDTO(
                    report_id=report_id,
                    mime_type=mime_type,
                    pdf_bytes=pdf_bytes,
                    size_bytes=size_bytes,
                    created_at=created_at,
                )
            )
            return "INSERT 0 1"

        if "DELETE FROM STEP_CRITERIA_BLOCKS" in normalized:
            if not args:
                self._store.step_criteria_blocks.clear()
                return "DELETE"
            stp_id = format_prefixed_uuid7(str(args[0]), EntityPrefix.STEP)
            if stp_id in self._store.step_criteria_blocks:
                del self._store.step_criteria_blocks[stp_id]
                return "DELETE 1"
            return "DELETE 0"

        if "INSERT INTO STEP_CRITERIA_BLOCKS" in normalized:
            stp_id = format_prefixed_uuid7(str(args[0]), EntityPrefix.STEP)
            raw_blks = args[1] if len(args) > 1 and isinstance(args[1], Sequence) else ()
            raw_pos = args[2] if len(args) > 2 and isinstance(args[2], Sequence) else ()
            indexed_pairs: list[tuple[int, str]] = []
            for pos_val, blk_val in zip(raw_pos, raw_blks, strict=True):
                blk_id = format_prefixed_uuid7(str(blk_val), EntityPrefix.PROMPT_BLOCK)
                blk_uuid = parse_prefixed_uuid7(blk_id, EntityPrefix.PROMPT_BLOCK)
                if (
                    self._store.seed_tables["prompt_blocks"]
                    and str(blk_uuid) not in self._store.seed_tables["prompt_blocks"]
                    and blk_id not in self._store.seed_tables["prompt_blocks"]
                ):
                    raise _InMemorySqlStateError(
                        f"insert or update on table 'step_criteria_blocks' violates foreign key constraint ({blk_id})",
                        sqlstate="23503",
                    )
                indexed_pairs.append((int(str(pos_val)), blk_id))
            indexed_pairs.sort(key=lambda pair: pair[0])
            self._store.step_criteria_blocks[stp_id] = tuple(pair[1] for pair in indexed_pairs)
            return f"INSERT 0 {len(indexed_pairs)}"

        if "DELETE FROM WORKFLOW_STEP_REFS" in normalized:
            if not args:
                self._store.workflow_step_refs.clear()
                return "DELETE"
            wf_id = format_prefixed_uuid7(str(args[0]), EntityPrefix.WORKFLOW)
            if wf_id in self._store.workflow_step_refs:
                del self._store.workflow_step_refs[wf_id]
                return "DELETE 1"
            return "DELETE 0"

        if "INSERT INTO WORKFLOW_STEP_REFS" in normalized:
            wf_id = format_prefixed_uuid7(str(args[0]), EntityPrefix.WORKFLOW)
            raw_stps = args[1] if len(args) > 1 and isinstance(args[1], Sequence) else ()
            formatted_stps: list[str] = []
            for stp_val in raw_stps:
                stp_id = format_prefixed_uuid7(str(stp_val), EntityPrefix.STEP)
                stp_uuid = parse_prefixed_uuid7(stp_id, EntityPrefix.STEP)
                if (
                    self._store.seed_tables["steps"]
                    and str(stp_uuid) not in self._store.seed_tables["steps"]
                    and stp_id not in self._store.seed_tables["steps"]
                ):
                    raise _InMemorySqlStateError(
                        f"insert or update on table 'workflow_step_refs' violates foreign key constraint ({stp_id})",
                        sqlstate="23503",
                    )
                if stp_id not in formatted_stps:
                    formatted_stps.append(stp_id)
            self._store.workflow_step_refs[wf_id] = tuple(formatted_stps)
            return f"INSERT 0 {len(formatted_stps)}"

        if "UPDATE REPORT_ARTIFACTS" in normalized:
            report_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            report_id = format_prefixed_uuid7(report_uuid, EntityPrefix.REPORT)
            self._store.report_has_pdf[report_id] = True
            return "UPDATE 1"

        if "INSERT INTO EXECUTIONS" in normalized:
            record = _hydrate_in_memory_execution_record(args)
            self._store.executions[record.id] = record
            return "INSERT 0 1"

        for tbl in (
            "organizations",
            "users",
            "invitations",
            "tenant_secrets",
            "execution_assignments",
            "model_registries",
            "mcp_gateways",
            "prompt_blocks",
            "task_briefs",
            "steps",
            "workflows",
            "output_profiles",
            "report_artifacts",
        ):
            if f"INSERT INTO {tbl.upper()}" in normalized:
                if tbl == "execution_assignments" and len(args) >= 10 and (args[8] is None) != (args[9] is None):
                    raise _InMemorySqlStateError(
                        "new row for relation 'execution_assignments' violates check constraint "
                        "'enforce_assignment_task_brief_snapshot_parity'",
                        sqlstate="23514",
                    )
                row_id = str(args[0])
                self._store.seed_tables[tbl][row_id] = tuple(_to_column_value(a) for a in args)
                return "INSERT 0 1"
            if f"DELETE FROM {tbl.upper()}" in normalized:
                if not args:
                    self._store.seed_tables[tbl].clear()
                    return "DELETE"
                row_id = str(args[0])
                if tbl == "model_registries" and isinstance(args[0], (uuid.UUID, str)):
                    mrg_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.MODEL_REGISTRY)
                    mrg_uuid = parse_prefixed_uuid7(mrg_prefixed, EntityPrefix.MODEL_REGISTRY)
                    self._entities._assert_model_registry_not_referenced(mrg_prefixed, mrg_uuid)
                if tbl == "mcp_gateways" and isinstance(args[0], (uuid.UUID, str)):
                    mcp_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.MCP_GATEWAY)
                    mcp_uuid = parse_prefixed_uuid7(mcp_prefixed, EntityPrefix.MCP_GATEWAY)
                    self._entities._assert_mcp_gateway_not_referenced(mcp_prefixed, mcp_uuid)
                if tbl == "prompt_blocks" and isinstance(args[0], (uuid.UUID, str)):
                    blk_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.PROMPT_BLOCK)
                    blk_uuid = parse_prefixed_uuid7(blk_prefixed, EntityPrefix.PROMPT_BLOCK)
                    if self._entities._is_prompt_block_referenced(blk_prefixed, blk_uuid):
                        raise _InMemorySqlStateError(
                            f"update or delete on table 'prompt_blocks' violates foreign key constraint ({blk_prefixed})",
                            sqlstate="23503",
                        )
                if tbl == "steps" and isinstance(args[0], (uuid.UUID, str)):
                    stp_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.STEP)
                    if self._entities._is_step_referenced(stp_prefixed):
                        raise _InMemorySqlStateError(
                            f"update or delete on table 'steps' violates foreign key constraint ({stp_prefixed})",
                            sqlstate="23503",
                        )
                if tbl == "output_profiles" and isinstance(args[0], (uuid.UUID, str)):
                    prf_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.OUTPUT_PROFILE)
                    prf_uuid = parse_prefixed_uuid7(prf_prefixed, EntityPrefix.OUTPUT_PROFILE)
                    if self._entities._is_output_profile_referenced(prf_prefixed, prf_uuid):
                        raise _InMemorySqlStateError(
                            f"update or delete on table 'output_profiles' violates foreign key constraint ({prf_prefixed})",
                            sqlstate="23503",
                        )
                if tbl == "task_briefs" and isinstance(args[0], (uuid.UUID, str)):
                    tbr_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.TASK_BRIEF)
                    tbr_uuid = parse_prefixed_uuid7(tbr_prefixed, EntityPrefix.TASK_BRIEF)
                    if self._entities._is_task_brief_referenced(tbr_prefixed, tbr_uuid):
                        raise _InMemorySqlStateError(
                            f"update or delete on table 'task_briefs' violates foreign key constraint ({tbr_prefixed})",
                            sqlstate="23503",
                        )
                if tbl == "workflows" and isinstance(args[0], (uuid.UUID, str)):
                    wf_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.WORKFLOW)
                    wf_uuid = parse_prefixed_uuid7(wf_prefixed, EntityPrefix.WORKFLOW)
                    if self._entities._is_workflow_referenced(wf_prefixed, wf_uuid):
                        raise _InMemorySqlStateError(
                            f"update or delete on table 'workflows' violates foreign key constraint ({wf_prefixed})",
                            sqlstate="23503",
                        )
                if row_id in self._store.seed_tables[tbl]:
                    del self._store.seed_tables[tbl][row_id]
                    if tbl == "organizations" and isinstance(args[0], (uuid.UUID, str)):
                        org_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.ORGANIZATION)
                        self._entities._cascade_delete_organization_children(org_prefixed)
                    if tbl == "mcp_gateways" and isinstance(args[0], (uuid.UUID, str)):
                        mcp_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.MCP_GATEWAY)
                        mcp_uuid = parse_prefixed_uuid7(mcp_prefixed, EntityPrefix.MCP_GATEWAY)
                        self._entities._cascade_delete_mcp_gateway_secrets(mcp_prefixed, mcp_uuid)
                    if tbl == "steps" and isinstance(args[0], (uuid.UUID, str)):
                        stp_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.STEP)
                        if stp_prefixed in self._store.step_criteria_blocks:
                            del self._store.step_criteria_blocks[stp_prefixed]
                    if tbl == "workflows" and isinstance(args[0], (uuid.UUID, str)):
                        wf_prefixed = format_prefixed_uuid7(args[0], EntityPrefix.WORKFLOW)
                        if wf_prefixed in self._store.workflow_step_refs:
                            del self._store.workflow_step_refs[wf_prefixed]
                    return "DELETE 1"
                if tbl in _TABLE_TO_ENTITY_PREFIX and isinstance(args[0], (uuid.UUID, str)):
                    prefixed_key = format_prefixed_uuid7(args[0], _TABLE_TO_ENTITY_PREFIX[tbl])
                    if prefixed_key in self._store.seed_tables[tbl]:
                        del self._store.seed_tables[tbl][prefixed_key]
                        if tbl == "organizations":
                            self._entities._cascade_delete_organization_children(prefixed_key)
                        if tbl == "mcp_gateways":
                            mcp_uuid = parse_prefixed_uuid7(prefixed_key, EntityPrefix.MCP_GATEWAY)
                            self._entities._cascade_delete_mcp_gateway_secrets(prefixed_key, mcp_uuid)
                        if tbl == "steps" and prefixed_key in self._store.step_criteria_blocks:
                            del self._store.step_criteria_blocks[prefixed_key]
                        if tbl == "workflows" and prefixed_key in self._store.workflow_step_refs:
                            del self._store.workflow_step_refs[prefixed_key]
                        return "DELETE 1"
                return "DELETE 0"

        if "DELETE FROM EXECUTIONS" in normalized:
            if not args:
                self._store.executions.clear()
                return "DELETE"
            exec_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            exec_id = format_prefixed_uuid7(exec_uuid, EntityPrefix.EXECUTION)
            if exec_id in self._store.executions:
                del self._store.executions[exec_id]
                return "DELETE 1"
            return "DELETE 0"

        return "OK"

    async def executemany(
        self,
        command: str,
        args: Sequence[Sequence[object]],
        *,
        timeout: float | None = None,
    ) -> None:
        """Execute a batch SQL statement across parameter sequences.

        Args:
            command: SQL statement template.
            args: Sequence of parameter rows.
            timeout: Optional command timeout in seconds.
        """
        self._check_fault("executemany")
        _ = timeout
        normalized = " ".join(command.strip().split()).upper()

        if "INSERT INTO QUORUM_NODES" in normalized:
            for row in args:
                entry = _hydrate_in_memory_proposition_node(row)
                self._store.nodes[entry.node.node_id] = entry
        elif "INSERT INTO QUORUM_EDGES" in normalized:
            for row in args:
                edge_uuid = row[0] if isinstance(row[0], (uuid.UUID, str)) else str(row[0])
                run_uuid = row[1] if isinstance(row[1], (uuid.UUID, str)) else str(row[1])
                src_uuid = row[2] if isinstance(row[2], (uuid.UUID, str)) else str(row[2])
                tgt_uuid = row[3] if isinstance(row[3], (uuid.UUID, str)) else str(row[3])
                edge_id = format_prefixed_uuid7(edge_uuid, EntityPrefix.EDGE)
                run_id = format_prefixed_uuid7(run_uuid, EntityPrefix.EXECUTION)
                src_id = format_prefixed_uuid7(src_uuid, EntityPrefix.NODE)
                tgt_id = format_prefixed_uuid7(tgt_uuid, EntityPrefix.NODE)
                edge = DependencyEdge(
                    edge_id=edge_id,
                    run_id=run_id,
                    source_id=src_id,
                    target_id=tgt_id,
                    relation_type=DependencyRelationType(str(row[4])),
                    causal_weight=float(str(row[5])),
                    created_at=_extract_uuid7_timestamp(edge_id, EntityPrefix.EDGE),
                )
                self._store.edges[edge_id] = edge
        else:
            for tbl in (
                "organizations",
                "users",
                "invitations",
                "tenant_secrets",
                "execution_assignments",
                "model_registries",
                "mcp_gateways",
                "prompt_blocks",
                "task_briefs",
                "steps",
                "workflows",
                "output_profiles",
            ):
                if f"INSERT INTO {tbl.upper()}" in normalized:
                    for row in args:
                        row_id = str(row[0])
                        self._store.seed_tables[tbl][row_id] = tuple(_to_column_value(a) for a in row)
                    break

    async def fetch(
        self,
        query: str,
        *args: object,
        timeout: float | None = None,
    ) -> Sequence[AsyncPgRecordProtocol]:
        """Execute a SQL query and return all matching records as InMemoryAsyncPgRecord rows.

        Args:
            query: SQL SELECT or Multi-CTE query string.
            *args: Positional query bind parameters.
            timeout: Optional command timeout in seconds.

        Returns:
            Sequence of InMemoryAsyncPgRecord instances.
        """
        self._check_fault("fetch")
        _ = timeout
        normalized = " ".join(query.strip().split()).upper()

        if "WITH INPUT_NODES AS" in normalized:
            run_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            run_id = format_prefixed_uuid7(run_uuid, EntityPrefix.EXECUTION)
            raw_nodes = from_json(str(args[1]))
            raw_edges = from_json(str(args[2]))
            node_drafts = [NodeDraft.model_validate(item, strict=False) for item in raw_nodes]
            edge_drafts = [EdgeDraft.model_validate(item, strict=False) for item in raw_edges]
            nodes = await self._graph.materialize_wave(run_id, node_drafts, edge_drafts)
            records: list[AsyncPgRecordProtocol] = []
            for node in nodes:
                records.append(
                    InMemoryAsyncPgRecord(
                        {
                            "node_id": parse_prefixed_uuid7(node.node_id, EntityPrefix.NODE),
                            "run_id": parse_prefixed_uuid7(node.run_id, EntityPrefix.EXECUTION),
                            "node_type": node.node_type.value,
                            "confidence": node.confidence,
                            "payload": node.payload.model_dump_json(),
                            "created_at": node.created_at,
                        }
                    )
                )
            return tuple(records)

        if "NOT EXISTS" in normalized and "FROM QUORUM_NODES" in normalized:
            run_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            run_id = format_prefixed_uuid7(run_uuid, EntityPrefix.EXECUTION)
            roots = await self._graph.fetch_next_kahn_wave(run_id)
            return tuple(
                InMemoryAsyncPgRecord(
                    {
                        "node_id": parse_prefixed_uuid7(node.node_id, EntityPrefix.NODE),
                        "run_id": parse_prefixed_uuid7(node.run_id, EntityPrefix.EXECUTION),
                        "node_type": node.node_type.value,
                        "confidence": node.confidence,
                        "payload": node.payload.model_dump_json(),
                        "created_at": node.created_at,
                    }
                )
                for node in roots
            )

        if "REBUTTAL_CONFIDENCE" in normalized:
            run_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            run_id = format_prefixed_uuid7(run_uuid, EntityPrefix.EXECUTION)
            min_conf = float(str(args[1]))
            matches = await self._graph.find_falsified_claims(run_id, min_confidence=min_conf)
            return tuple(
                InMemoryAsyncPgRecord(
                    {
                        "rebuttal_id": parse_prefixed_uuid7(m.rebuttal_id, EntityPrefix.NODE),
                        "invalidated_warrant_id": parse_prefixed_uuid7(m.invalidated_warrant_id, EntityPrefix.NODE),
                        "falsified_claim_id": parse_prefixed_uuid7(m.falsified_claim_id, EntityPrefix.NODE),
                        "rebuttal_confidence": m.rebuttal_confidence,
                        "claim_statement": m.claim_statement,
                    }
                )
                for m in matches
            )

        if "FROM AUDIT_LOGS" in normalized:
            return self._fetch_audit_log_rows(normalized, args)

        if "FROM USAGE_RECORDS" in normalized:
            return self._fetch_usage_record_rows(normalized, args)

        if "FROM EXECUTIONS" in normalized:
            return self._fetch_execution_rows(normalized, args)

        outer_tbl = self._extract_outer_from_table(query)
        if outer_tbl == "execution_assignments":
            return self._fetch_execution_assignment_rows(query, normalized, args)
        for tbl in (
            "organizations",
            "users",
            "invitations",
            "tenant_secrets",
            "execution_assignments",
            "model_registries",
            "mcp_gateways",
            "prompt_blocks",
            "task_briefs",
            "steps",
            "workflows",
            "output_profiles",
            "report_artifacts",
        ):
            if outer_tbl == tbl:
                cols = self._extract_select_columns(query)
                mapped_rows: list[dict[str, _ColumnValue]] = []
                for entry in self._store.seed_tables[tbl].values():
                    if isinstance(entry, Sequence):
                        mapped = self._zip_select_row(cols, entry)
                        if (
                            "WHERE ORGANIZATION_ID = $1" in normalized
                            and args
                            and "organization_id" in mapped
                            and mapped["organization_id"] != args[0]
                        ):
                            continue
                        if (
                            "WHERE EXECUTION_ID = $1" in normalized
                            and args
                            and "execution_id" in mapped
                            and mapped["execution_id"] != args[0]
                        ):
                            continue
                        mapped_rows.append(mapped)
                if "ORDER BY CREATED_AT DESC" in normalized:
                    mapped_rows.sort(
                        key=lambda m: (
                            m["created_at"]
                            if "created_at" in m and isinstance(m["created_at"], datetime)
                            else datetime.min.replace(tzinfo=UTC)
                        ),
                        reverse=True,
                    )
                return tuple(InMemoryAsyncPgRecord(m) for m in mapped_rows)

        return ()

    def _zip_select_row(
        self,
        cols: list[str],
        entry: Sequence[_ColumnValue],
    ) -> dict[str, _ColumnValue]:
        """Map SELECT column names to stored positional values, synthesizing VIRTUAL created_at and junction arrays."""
        if "criteria_block_ids" in cols and len(entry) == len(cols) - 1:
            non_projected_cols = [c for c in cols if c != "criteria_block_ids"]
            mapped_step = {col: val for col, val in zip(non_projected_cols, entry, strict=False)}
            step_pk: _ColumnValue = entry[0] if entry else None
            criteria_uuids: tuple[uuid.UUID, ...] = ()
            if isinstance(step_pk, (uuid.UUID, str)):
                stp_id = format_prefixed_uuid7(step_pk, EntityPrefix.STEP)
                if stp_id in self._store.step_criteria_blocks:
                    criteria_uuids = tuple(
                        parse_prefixed_uuid7(bid, EntityPrefix.PROMPT_BLOCK)
                        for bid in self._store.step_criteria_blocks[stp_id]
                    )
            mapped_step["criteria_block_ids"] = criteria_uuids
            return mapped_step
        if "created_at" in cols and len(entry) == len(cols) - 1:
            non_virtual_cols = [c for c in cols if c != "created_at"]
            mapped = {col: val for col, val in zip(non_virtual_cols, entry, strict=False)}
            pk_val: _ColumnValue = None
            if entry:
                pk_val = entry[0]
            if isinstance(pk_val, uuid.UUID):
                ts_ms = (pk_val.int >> 80) & ((1 << 48) - 1)
                mapped["created_at"] = datetime.fromtimestamp(ts_ms / 1000.0, tz=UTC)
            else:
                mapped["created_at"] = datetime.now(UTC)
            return mapped
        return {col: val for col, val in zip(cols, entry, strict=False)}

    @staticmethod
    def _find_outer_from_index(norm_q: str) -> int:
        """Find the character index of the top-level ' FROM ' keyword outside parentheses."""
        upper = norm_q.upper()
        depth = 0
        for idx, ch in enumerate(upper):
            if ch == "(":
                depth += 1
            elif ch == ")" and depth > 0:
                depth -= 1
            elif depth == 0 and upper.startswith(" FROM ", idx):
                return idx
        return -1

    @classmethod
    def _extract_outer_from_table(cls, query: str) -> str | None:
        """Extract the outer FROM table identifier ignoring scalar subqueries."""
        norm_q = " ".join(query.strip().split())
        from_idx = cls._find_outer_from_index(norm_q)
        if from_idx == -1:
            return None
        after_from = norm_q[from_idx + 6 :].strip()
        if not after_from:
            return None
        return after_from.split()[0].strip().lower()

    @classmethod
    def _extract_select_columns(cls, query: str) -> list[str]:
        """Extract column names or aliases from a SELECT col1, col2, ... FROM statement."""
        norm_q = " ".join(query.strip().split())
        upper = norm_q.upper()
        select_idx = upper.find("SELECT ")
        from_idx = cls._find_outer_from_index(norm_q)
        if select_idx == -1 or from_idx == -1 or from_idx <= select_idx + 7:
            return []
        cols_part = norm_q[select_idx + 7 : from_idx]
        items: list[str] = []
        depth = 0
        start = 0
        for idx, ch in enumerate(cols_part):
            if ch == "(":
                depth += 1
            elif ch == ")" and depth > 0:
                depth -= 1
            elif ch == "," and depth == 0:
                items.append(cols_part[start:idx].strip())
                start = idx + 1
        tail = cols_part[start:].strip()
        if tail:
            items.append(tail)

        resolved_cols: list[str] = []
        for expr in items:
            if not expr:
                continue
            expr_upper = expr.upper()
            as_pos = -1
            p_depth = 0
            for idx, ch in enumerate(expr_upper):
                if ch == "(":
                    p_depth += 1
                elif ch == ")" and p_depth > 0:
                    p_depth -= 1
                elif p_depth == 0 and expr_upper.startswith(" AS ", idx):
                    as_pos = idx
            if as_pos != -1:
                resolved_cols.append(expr[as_pos + 4 :].strip().lower())
            else:
                resolved_cols.append(expr.strip().lower())
        return resolved_cols

    @staticmethod
    def _build_execution_record_row(rec: ExecutionRecord) -> InMemoryAsyncPgRecord:
        """Convert a stored ExecutionRecord into an InMemoryAsyncPgRecord."""
        dumped = rec.model_dump(mode="json", exclude_none=True)
        frozen_ctx_str: str | None = None
        if rec.frozen_context is not None:
            frozen_ctx_str = to_json(dumped["frozen_context"]).decode("utf-8")
        exec_summary_str: str | None = None
        if rec.execution_summary is not None:
            exec_summary_str = to_json(dumped["execution_summary"]).decode("utf-8")
        metadata_str: str | None = None
        if rec.metadata is not None:
            metadata_str = to_json(dumped["metadata"]).decode("utf-8")
        return InMemoryAsyncPgRecord(
            {
                "id": parse_prefixed_uuid7(rec.id, EntityPrefix.EXECUTION),
                "workflow_id": rec.workflow_id,
                "workflow_version": rec.workflow_version,
                "active_profile_id": rec.active_profile_id,
                "output_profile_id": rec.output_profile_id,
                "status": rec.status.value,
                "target_locale": rec.target_locale,
                "progress": rec.progress,
                "status_message": rec.status_message,
                "raw_inputs": to_json(dumped["raw_inputs"]).decode("utf-8"),
                "frozen_context": frozen_ctx_str,
                "frozen_context_storage_path": rec.frozen_context_storage_path,
                "pdf_report_path": rec.pdf_report_path,
                "steps": to_json(dumped["steps"]).decode("utf-8"),
                "step_states": to_json(dumped["step_states"]).decode("utf-8"),
                "profile_syntheses": to_json(dumped["profile_syntheses"]).decode("utf-8"),
                "source_identity_manifest": to_json(dumped["source_identity_manifest"]).decode("utf-8"),
                "execution_trace": to_json(dumped["execution_trace"]).decode("utf-8"),
                "execution_trace_storage_path": rec.execution_trace_storage_path,
                "context_variables": to_json(dumped["context_variables"]).decode("utf-8"),
                "context_variables_storage_path": rec.context_variables_storage_path,
                "is_resumable": rec.is_resumable,
                "prompt_tokens": rec.prompt_tokens,
                "completion_tokens": rec.completion_tokens,
                "cached_tokens": rec.cached_tokens,
                "reasoning_tokens": rec.reasoning_tokens,
                "cumulative_synthesis_tokens": rec.cumulative_synthesis_tokens,
                "dag_cost_usd": rec.dag_cost_usd,
                "cumulative_synthesis_cost": rec.cumulative_synthesis_cost,
                "cost_estimate": rec.cost_estimate,
                "models_used": to_json(dumped["models_used"]).decode("utf-8"),
                "execution_summary": exec_summary_str,
                "metadata": metadata_str,
                "duration_ms": rec.duration_ms,
                "error": rec.error,
                "created_at": rec.created_at,
                "updated_at": rec.updated_at,
                "completed_at": rec.completed_at,
                "created_by": parse_prefixed_uuid7(rec.created_by, EntityPrefix.USER)
                if rec.created_by is not None
                else None,
                "organization_id": rec.organization_id,
                "state_version": rec.state_version,
            }
        )

    async def fetchrow(
        self,
        query: str,
        *args: object,
        timeout: float | None = None,
    ) -> AsyncPgRecordProtocol | None:
        """Execute a SQL query and return the first matching record or None.

        Args:
            query: SQL query string.
            *args: Positional query bind parameters.
            timeout: Optional command timeout in seconds.

        Returns:
            InMemoryAsyncPgRecord or None.
        """
        self._check_fault("fetchrow")
        _ = timeout
        normalized = " ".join(query.strip().split()).upper()

        if "INSERT INTO WORKFLOWS" in normalized and args:
            wf_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            row_id = str(wf_uuid)
            wf_prefixed = format_prefixed_uuid7(wf_uuid, EntityPrefix.WORKFLOW)
            wf_bucket = self._store.seed_tables["workflows"]
            expected_version = int(str(args[5]))
            existing_wf_entry: _SeedRowEntry | None = None
            if row_id in wf_bucket:
                existing_wf_entry = wf_bucket[row_id]
            elif wf_prefixed in wf_bucket:
                existing_wf_entry = wf_bucket[wf_prefixed]

            if existing_wf_entry is not None:
                if isinstance(existing_wf_entry, Workflow):
                    actual_wf_version = existing_wf_entry.version
                elif isinstance(existing_wf_entry, BaseModel):
                    raise TypeError(f"Unexpected BaseModel in workflows bucket: {type(existing_wf_entry).__name__}")
                else:
                    actual_wf_version = int(str(existing_wf_entry[5]))
                if actual_wf_version != expected_version:
                    return None
                next_version = actual_wf_version + 1
                updated_row = [_to_column_value(a) for a in args]
                updated_row[5] = next_version
                if wf_prefixed in wf_bucket:
                    del wf_bucket[wf_prefixed]
                wf_bucket[row_id] = tuple(updated_row)
                return InMemoryAsyncPgRecord({"version": next_version})

            wf_bucket[row_id] = tuple(_to_column_value(a) for a in args)
            return InMemoryAsyncPgRecord({"version": expected_version})

        if (
            "SELECT COUNT(*)::BIGINT AS ROW_COUNT FROM " in normalized
            or "SELECT COUNT(*) AS ROW_COUNT FROM " in normalized
        ):
            for tbl in (
                "organizations",
                "users",
                "invitations",
                "tenant_secrets",
                "execution_assignments",
                "model_registries",
                "mcp_gateways",
                "prompt_blocks",
                "task_briefs",
                "steps",
                "workflows",
                "output_profiles",
                "report_artifacts",
            ):
                if f"FROM {tbl.upper()}" in normalized:
                    return InMemoryAsyncPgRecord({"row_count": len(self._store.seed_tables[tbl])})
            if "FROM STEP_CRITERIA_BLOCKS" in normalized:
                return InMemoryAsyncPgRecord(
                    {"row_count": sum(len(v) for v in self._store.step_criteria_blocks.values())}
                )
            if "FROM WORKFLOW_STEP_REFS" in normalized:
                return InMemoryAsyncPgRecord(
                    {"row_count": sum(len(v) for v in self._store.workflow_step_refs.values())}
                )
            if "FROM EXECUTIONS" in normalized:
                return InMemoryAsyncPgRecord({"row_count": len(self._store.executions)})
            if "FROM REPORT_BINARIES" in normalized:
                return InMemoryAsyncPgRecord({"row_count": len(self._store.report_binaries)})
            if "FROM AUDIT_LOGS" in normalized:
                return InMemoryAsyncPgRecord({"row_count": len(self._store.audit_logs)})
            if "FROM USAGE_RECORDS" in normalized:
                return InMemoryAsyncPgRecord({"row_count": len(self._store.usage_records)})

        if "COALESCE(SUM(PROMPT_TOKENS)" in normalized and "FROM USAGE_RECORDS" in normalized:
            matched_usage = self._filter_usage_records(normalized, args)
            return InMemoryAsyncPgRecord(
                {
                    "total_prompt_tokens": sum(r.input_tokens for r in matched_usage),
                    "total_completion_tokens": sum(r.output_tokens for r in matched_usage),
                    "total_cached_tokens": sum(r.cached_tokens for r in matched_usage),
                    "total_reasoning_tokens": sum(r.reasoning_tokens for r in matched_usage),
                    "total_cache_creation_input_tokens": sum(r.cache_creation_input_tokens for r in matched_usage),
                    "total_cost_usd": sum(r.cost_usd for r in matched_usage),
                    "total_estimated_savings_usd": sum(r.estimated_savings_usd for r in matched_usage),
                    "record_count": len(matched_usage),
                }
            )

        if "CYCLE TARGET_ID SET IS_CYCLE" in normalized:
            run_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            run_id = format_prefixed_uuid7(run_uuid, EntityPrefix.EXECUTION)
            cycle = _find_cycle_in_edges(run_id, list(self._store.edges.values()))
            if cycle is None:
                return None
            uuid_path = tuple(parse_prefixed_uuid7(nid, EntityPrefix.NODE) for nid in cycle)
            return InMemoryAsyncPgRecord(
                {
                    "traversal_path": uuid_path,
                    "is_cycle": True,
                }
            )

        if "FROM REPORT_BINARIES" in normalized:
            report_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            report_id = format_prefixed_uuid7(report_uuid, EntityPrefix.REPORT)
            if report_id not in self._store.report_binaries:
                return None
            binary = self._store.report_binaries[report_id]
            return InMemoryAsyncPgRecord(
                {
                    "report_id": parse_prefixed_uuid7(binary.report_id, EntityPrefix.REPORT),
                    "mime_type": binary.mime_type,
                    "pdf_bytes": binary.pdf_bytes,
                    "size_bytes": binary.size_bytes,
                    "created_at": binary.created_at,
                }
            )

        if "FROM EXECUTIONS" in normalized:
            exec_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            exec_id = format_prefixed_uuid7(exec_uuid, EntityPrefix.EXECUTION)
            if exec_id not in self._store.executions:
                return None
            return self._build_execution_record_row(self._store.executions[exec_id])

        if "FROM USERS" in normalized and "LOWER(EMAIL) = LOWER($1)" in normalized and args:
            target_email = str(args[0]).strip().lower()
            cols = self._extract_select_columns(query)
            for entry in self._store.seed_tables["users"].values():
                if isinstance(entry, Sequence):
                    mapped = self._zip_select_row(cols, entry)
                    if "email" in mapped and str(mapped["email"]).lower() == target_email:
                        return InMemoryAsyncPgRecord(mapped)
            return None

        outer_tbl = self._extract_outer_from_table(query)
        if outer_tbl == "execution_assignments" and args:
            if "WHERE TOKEN_HASH = $1" in normalized:
                cols = self._extract_select_columns(query)
                for entry in self._store.seed_tables["execution_assignments"].values():
                    if isinstance(entry, Sequence):
                        mapped = self._zip_select_row(cols, entry)
                        if "token_hash" in mapped and mapped["token_hash"] == args[0]:
                            return InMemoryAsyncPgRecord(mapped)
                return None
            if "WHERE EXECUTION_ID = $1" in normalized:
                cols = self._extract_select_columns(query)
                matched_rows: list[dict[str, _ColumnValue]] = []
                for entry in self._store.seed_tables["execution_assignments"].values():
                    if isinstance(entry, Sequence):
                        mapped = self._zip_select_row(cols, entry)
                        if "execution_id" in mapped and mapped["execution_id"] == args[0]:
                            matched_rows.append(mapped)
                if not matched_rows:
                    return None
                matched_rows.sort(key=lambda m: uuid.UUID(str(m["id"])), reverse=True)
                return InMemoryAsyncPgRecord(matched_rows[0])

        for tbl in (
            "organizations",
            "users",
            "invitations",
            "tenant_secrets",
            "execution_assignments",
            "model_registries",
            "mcp_gateways",
            "prompt_blocks",
            "task_briefs",
            "steps",
            "workflows",
            "output_profiles",
            "report_artifacts",
        ):
            if outer_tbl == tbl and args:
                row_id = str(args[0])
                if row_id not in self._store.seed_tables[tbl]:
                    return None
                entry = self._store.seed_tables[tbl][row_id]
                if isinstance(entry, Sequence):
                    cols = self._extract_select_columns(query)
                    return InMemoryAsyncPgRecord(self._zip_select_row(cols, entry))

        return None

    def _fetch_execution_rows(
        self,
        normalized: str,
        args: Sequence[object],
    ) -> tuple[AsyncPgRecordProtocol, ...]:
        """Filter, order, and serialize stored ExecutionRecord models into InMemoryAsyncPgRecord rows."""
        matched = list(self._store.executions.values())
        where_part = normalized.split("WHERE", 1)[1] if "WHERE" in normalized else ""
        param_idx = 0
        if "ORGANIZATION_ID = $" in where_part and param_idx < len(args):
            target_org = args[param_idx]
            param_idx += 1
            matched = [
                r
                for r in matched
                if r.organization_id is not None
                and parse_prefixed_uuid7(r.organization_id, EntityPrefix.ORGANIZATION) == target_org
            ]
        if "CREATED_BY = $" in where_part and param_idx < len(args):
            target_usr = args[param_idx]
            param_idx += 1
            matched = [
                r
                for r in matched
                if r.created_by is not None and parse_prefixed_uuid7(r.created_by, EntityPrefix.USER) == target_usr
            ]
        if "WORKFLOW_ID = $" in where_part and param_idx < len(args):
            target_wf = args[param_idx]
            param_idx += 1
            matched = [r for r in matched if parse_prefixed_uuid7(r.workflow_id, EntityPrefix.WORKFLOW) == target_wf]
        if "STATUS = $" in where_part and param_idx < len(args):
            target_status = str(args[param_idx])
            param_idx += 1
            matched = [r for r in matched if r.status.value == target_status]

        if "ORDER BY ID DESC" in normalized:
            matched.sort(key=lambda r: parse_prefixed_uuid7(r.id, EntityPrefix.EXECUTION), reverse=True)
        else:
            matched.sort(key=lambda r: r.created_at, reverse=True)

        if "LIMIT $" in normalized and param_idx < len(args):
            limit_val = int(str(args[param_idx]))
            matched = matched[:limit_val]

        return tuple(self._build_execution_record_row(rec) for rec in matched)

    def _fetch_execution_assignment_rows(
        self,
        query: str,
        normalized: str,
        args: Sequence[object],
    ) -> tuple[AsyncPgRecordProtocol, ...]:
        """Filter, order, and serialize stored execution_assignments tuple rows into InMemoryAsyncPgRecord rows."""
        cols = self._extract_select_columns(query)
        mapped_rows: list[dict[str, _ColumnValue]] = [
            self._zip_select_row(cols, entry)
            for entry in self._store.seed_tables["execution_assignments"].values()
            if isinstance(entry, Sequence)
        ]
        where_part = normalized.split("WHERE", 1)[1] if "WHERE" in normalized else ""
        param_idx = 0
        if "ORGANIZATION_ID = $" in where_part and param_idx < len(args):
            target_org = args[param_idx]
            param_idx += 1
            mapped_rows = [m for m in mapped_rows if "organization_id" in m and m["organization_id"] == target_org]
        if "BATCH_ID = $" in where_part and param_idx < len(args):
            target_batch = args[param_idx]
            param_idx += 1
            mapped_rows = [m for m in mapped_rows if "batch_id" in m and m["batch_id"] == target_batch]
        if "WORKFLOW_ID = $" in where_part and param_idx < len(args):
            target_wf = args[param_idx]
            param_idx += 1
            mapped_rows = [m for m in mapped_rows if "workflow_id" in m and m["workflow_id"] == target_wf]
        if "EXECUTION_ID = $" in where_part and param_idx < len(args):
            target_exe = args[param_idx]
            param_idx += 1
            mapped_rows = [m for m in mapped_rows if "execution_id" in m and m["execution_id"] == target_exe]

        if "ORDER BY ID DESC" in normalized:
            mapped_rows.sort(key=lambda m: uuid.UUID(str(m["id"])), reverse=True)

        if "LIMIT $" in normalized and param_idx < len(args):
            limit_val = int(str(args[param_idx]))
            mapped_rows = mapped_rows[:limit_val]

        return tuple(InMemoryAsyncPgRecord(m) for m in mapped_rows)

    def _fetch_audit_log_rows(
        self,
        normalized: str,
        args: Sequence[object],
    ) -> tuple[AsyncPgRecordProtocol, ...]:
        """Filter and serialize stored AuditLogRecord models into InMemoryAsyncPgRecord rows."""
        param_idx = 0
        matched = list(self._store.audit_logs.values())
        if "ORGANIZATION_ID = $" in normalized:
            target_org = args[param_idx]
            param_idx += 1
            matched = [
                r
                for r in matched
                if r.organization_id is not None
                and parse_prefixed_uuid7(r.organization_id, EntityPrefix.ORGANIZATION) == target_org
            ]
        elif "ORGANIZATION_ID IS NULL" in normalized:
            matched = [r for r in matched if r.organization_id is None]

        if "ACTOR_ID = $" in normalized:
            target_actor = args[param_idx]
            param_idx += 1
            matched = [
                r
                for r in matched
                if r.actor_id is not None and parse_prefixed_uuid7(r.actor_id, EntityPrefix.USER) == target_actor
            ]
        elif "ACTOR_ID IS NULL" in normalized:
            matched = [r for r in matched if r.actor_id is None]

        if "EVENT_TYPE = $" in normalized:
            target_event = str(args[param_idx])
            param_idx += 1
            matched = [r for r in matched if r.event_type == target_event]

        matched.sort(key=lambda r: parse_prefixed_uuid7(r.id, EntityPrefix.AUDIT_LOG), reverse=True)
        if "LIMIT $" in normalized and param_idx < len(args):
            limit_val = int(str(args[param_idx]))
            matched = matched[:limit_val]

        rows: list[AsyncPgRecordProtocol] = []
        for rec in matched:
            org_uuid = (
                parse_prefixed_uuid7(rec.organization_id, EntityPrefix.ORGANIZATION)
                if rec.organization_id is not None
                else None
            )
            actor_uuid = parse_prefixed_uuid7(rec.actor_id, EntityPrefix.USER) if rec.actor_id is not None else None
            exec_uuid = (
                parse_prefixed_uuid7(rec.execution_id, EntityPrefix.EXECUTION) if rec.execution_id is not None else None
            )
            rows.append(
                InMemoryAsyncPgRecord(
                    {
                        "id": parse_prefixed_uuid7(rec.id, EntityPrefix.AUDIT_LOG),
                        "organization_id": org_uuid,
                        "actor_id": actor_uuid,
                        "execution_id": exec_uuid,
                        "event_type": rec.event_type,
                        "resource_type": rec.resource_type,
                        "resource_id": rec.resource_id,
                        "details": to_json(rec.details).decode("utf-8"),
                        "created_at": rec.created_at,
                    }
                )
            )
        return tuple(rows)

    def _filter_usage_records(
        self,
        normalized: str,
        args: Sequence[object],
    ) -> list[UsageRecord]:
        """Filter stored UsageRecord models according to parameterized SQL predicates."""
        param_idx = 0
        matched = list(self._store.usage_records.values())
        if "ORGANIZATION_ID = $" in normalized:
            target_org = args[param_idx]
            param_idx += 1
            matched = [
                r
                for r in matched
                if r.org_id != "system" and parse_prefixed_uuid7(r.org_id, EntityPrefix.ORGANIZATION) == target_org
            ]
        elif "ORGANIZATION_ID IS NULL" in normalized:
            matched = [r for r in matched if r.org_id == "system"]

        if "USER_ID = $" in normalized:
            target_usr = args[param_idx]
            param_idx += 1
            matched = [
                r
                for r in matched
                if r.user_id != "system" and parse_prefixed_uuid7(r.user_id, EntityPrefix.USER) == target_usr
            ]
        elif "USER_ID IS NULL" in normalized:
            matched = [r for r in matched if r.user_id == "system"]

        if "CREATED_AT >= $" in normalized:
            since_val = args[param_idx]
            if isinstance(since_val, datetime):
                matched = [r for r in matched if r.timestamp >= since_val]

        matched.sort(key=lambda r: parse_prefixed_uuid7(r.id, EntityPrefix.USAGE_RECORD))
        return matched

    def _fetch_usage_record_rows(
        self,
        normalized: str,
        args: Sequence[object],
    ) -> tuple[AsyncPgRecordProtocol, ...]:
        """Filter and serialize stored UsageRecord models into InMemoryAsyncPgRecord rows."""
        matched = self._filter_usage_records(normalized, args)
        rows: list[AsyncPgRecordProtocol] = []
        for rec in matched:
            org_uuid = None if rec.org_id == "system" else parse_prefixed_uuid7(rec.org_id, EntityPrefix.ORGANIZATION)
            usr_uuid = None if rec.user_id == "system" else parse_prefixed_uuid7(rec.user_id, EntityPrefix.USER)
            exec_uuid = (
                parse_prefixed_uuid7(rec.execution_id, EntityPrefix.EXECUTION) if rec.execution_id is not None else None
            )
            rows.append(
                InMemoryAsyncPgRecord(
                    {
                        "id": parse_prefixed_uuid7(rec.id, EntityPrefix.USAGE_RECORD),
                        "organization_id": org_uuid,
                        "user_id": usr_uuid,
                        "execution_id": exec_uuid,
                        "model_name": rec.model,
                        "prompt_tokens": rec.input_tokens,
                        "completion_tokens": rec.output_tokens,
                        "cached_tokens": rec.cached_tokens,
                        "reasoning_tokens": rec.reasoning_tokens,
                        "cache_creation_input_tokens": rec.cache_creation_input_tokens,
                        "latency_ms": rec.latency_ms,
                        "finish_reason": rec.finish_reason,
                        "system_fingerprint": rec.system_fingerprint,
                        "cost_usd": rec.cost_usd,
                        "estimated_savings_usd": rec.estimated_savings_usd,
                        "created_at": rec.timestamp,
                    }
                )
            )
        return tuple(rows)


class InMemoryAsyncPgPool:
    """Stateful in-memory implementation of AsyncPgPoolProtocol with deterministic fault injection."""

    def __init__(self) -> None:
        """Initialize the in-memory connection pool and backing store."""
        self.store: _InMemoryPostgresStore = _InMemoryPostgresStore()
        self._faults: dict[str, Exception] = {}
        self.closed: bool = False
        self.acquired_count: int = 0
        self.released_count: int = 0

    def inject_fault(self, operation: str, exc: Exception) -> None:
        """Inject a deterministic exception for a specific pool or connection operation.

        Args:
            operation: Operation name ('acquire', 'release', 'close', 'execute', 'fetch', 'fetchrow', 'transaction').
            exc: Exception instance to raise when operation is called.
        """
        self._faults[operation] = exc

    def clear_faults(self) -> None:
        """Clear all injected faults from the pool."""
        self._faults.clear()

    async def acquire(self, *, timeout: float | None = None) -> AsyncPgConnectionProtocol:
        """Acquire an InMemoryAsyncPgConnection from the pool.

        Args:
            timeout: Optional timeout in seconds.

        Returns:
            InMemoryAsyncPgConnection bound to the shared store.
        """
        _ = timeout
        if "acquire" in self._faults:
            raise self._faults["acquire"]
        self.acquired_count += 1
        return InMemoryAsyncPgConnection(store=self.store, faults=self._faults)

    async def release(
        self,
        connection: AsyncPgConnectionProtocol,
        *,
        timeout: float | None = None,
    ) -> None:
        """Release an acquired connection back to the pool.

        Args:
            connection: Previously acquired connection.
            timeout: Optional timeout in seconds.
        """
        _ = (connection, timeout)
        if "release" in self._faults:
            raise self._faults["release"]
        self.released_count += 1

    async def close(self) -> None:
        """Mark the in-memory pool closed."""
        if "close" in self._faults:
            raise self._faults["close"]
        self.closed = True


class InMemoryUnitOfWork:
    """Hermetic 0 ms in-memory implementation of QuorumUnitOfWork with snapshot rollback.

    Attributes:
        graph: InMemoryGraphAdapter bound to the shared store.
        topology: InMemoryGraphAdapter bound to the shared store.
        reasoning: InMemoryGraphAdapter bound to the shared store.
        entities: InMemoryEntityAdapter bound to the shared store.
    """

    graph: GraphMutationPort
    topology: TopologyResolutionPort
    reasoning: CausalReasoningPort
    entities: EntityPersistencePort

    def __init__(self, store: _InMemoryPostgresStore | None = None) -> None:
        """Initialize the in-memory Unit of Work.

        Args:
            store: Optional shared _InMemoryPostgresStore; creates a new store if None.
        """
        self.store: _InMemoryPostgresStore = store if store is not None else _InMemoryPostgresStore()
        self._snapshot: _StoreSnapshot | None = None
        self._finalized: bool = False
        graph_adapter = InMemoryGraphAdapter(self.store)
        entity_adapter = InMemoryEntityAdapter(self.store)
        self.graph = graph_adapter
        self.topology = graph_adapter
        self.reasoning = graph_adapter
        self.entities = entity_adapter

    async def __aenter__(self) -> Self:
        """Capture a repeatable_read snapshot and enter the Unit of Work context.

        Returns:
            Initialized InMemoryUnitOfWork instance.
        """
        self._snapshot = self.store.take_snapshot()
        self._finalized = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Commit on clean exit or restore the pre-transaction snapshot on exception.

        Args:
            exc_type: Exception class if raised inside context.
            exc_val: Exception value if raised inside context.
            exc_tb: Traceback if raised inside context.
        """
        try:
            if exc_type is not None:
                if not self._finalized:
                    await self.rollback()
            elif not self._finalized:
                await self.commit()
        finally:
            self.store.current_org_reset_count += 1
            self._snapshot = None

    async def commit(self) -> None:
        """Commit the active in-memory transaction."""
        self._snapshot = None
        self._finalized = True

    async def rollback(self) -> None:
        """Roll back the active in-memory transaction to its initial snapshot."""
        if self._snapshot is not None:
            self.store.restore_snapshot(self._snapshot)
        self._snapshot = None
        self._finalized = True
