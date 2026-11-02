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
from datetime import datetime, timezone
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
from backend_v2.database.postgres.entity_adapter import hydrate_execution_row
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
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
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
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import (
    DependencyRelationType,
    EntityPrefix,
    PropositionNodeType,
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
    seed_counts: Annotated[dict[str, int], Field(default_factory=dict, description="Seeded table counts.")]
    migrations_applied: Annotated[int, Field(default=0, ge=0, description="DDL migrations applied count.")]


class _InMemoryPostgresStore:
    """Shared mutable in-memory storage backing InMemoryUnitOfWork and InMemoryAsyncPgPool.

    Attributes:
        nodes: Mapping of node_id to _StoredNodeEntry.
        edges: Mapping of edge_id to DependencyEdge.
        report_binaries: Mapping of report_id to ReportBinaryPayloadDTO.
        report_has_pdf: Mapping of report_id to boolean has_pdf flag.
        executions: Mapping of execution_id to ExecutionRecord.
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
        self.seed_tables: dict[str, dict[str, _SeedRowEntry]] = {
            "organizations": {},
            "users": {},
            "invitations": {},
            "tenant_secrets": {},
            "execution_assignments": {},
            "system_configs": {},
            "prompt_blocks": {},
            "steps": {},
            "workflows": {},
            "output_profiles": {},
            "report_artifacts": {},
            "trace_events": {},
        }
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
    return datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)


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
    "created_at",
    "updated_at",
    "completed_at",
    "created_by",
    "organization_id",
    "state_version",
)


def _hydrate_in_memory_execution_record(args: Sequence[object]) -> ExecutionRecord:
    """Hydrate an ExecutionRecord from parameterized INSERT INTO EXECUTIONS bind arguments.

    Delegates directly to the canonical PostgreSQL `hydrate_execution_row` adapter function.

    Args:
        args: Positional SQL bind parameters for executions insertion.

    Returns:
        Hydrated ExecutionRecord domain instance.
    """
    # Phase 1, Step 1.1: Delegate to canonical hydrate_execution_row SSOT without raw dict literals
    row_columns = dict(
        zip(
            _EXECUTION_INSERT_COLUMNS,
            (_to_column_value(arg) for arg in args),
            strict=True,
        )
    )
    return hydrate_execution_row(InMemoryAsyncPgRecord(row_columns))


def _hydrate_in_memory_proposition_node(row: Sequence[object]) -> _StoredNodeEntry:
    """Hydrate a _StoredNodeEntry from parameterized INSERT INTO QUORUM_NODES row values.

    Args:
        row: Positional SQL bind parameters for a quorum_nodes row.

    Returns:
        Hydrated _StoredNodeEntry instance.
    """
    # Phase 1, Step 1.1: Construct typed PropositionPayloadDTO and PropositionNode directly
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
            already_exists = any(
                existing.run_id == run_id
                and existing.source_id == src_node.node_id
                and existing.target_id == tgt_node.node_id
                and existing.relation_type == edge_draft.relation_type
                for existing in self._store.edges.values()
            )
            if not already_exists:
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
        _ = parse_prefixed_uuid7(org.id, EntityPrefix.ORG)
        self._store.seed_tables["organizations"][org.id] = org
        return org.id

    async def get_organization(self, org_id: str) -> Organization | None:
        """Retrieve an Organization by org_id.

        Args:
            org_id: Canonical org_<uuid7_hex> organization identifier.

        Returns:
            Stored Organization or None if not found.
        """
        _ = parse_prefixed_uuid7(org_id, EntityPrefix.ORG)
        if org_id in self._store.seed_tables["organizations"]:
            item = self._store.seed_tables["organizations"][org_id]
            if isinstance(item, Organization):
                return item
        return None

    async def list_organizations(self) -> Sequence[Organization]:
        """List all persisted Organization entities.

        Returns:
            Sequence of Organization domain models.
        """
        orgs = [item for item in self._store.seed_tables["organizations"].values() if isinstance(item, Organization)]
        orgs.sort(key=lambda o: o.id)
        return tuple(orgs)

    async def upsert_user(self, user: User) -> str:
        """Upsert a User entity in memory.

        Args:
            user: Validated User domain model.

        Returns:
            Canonical usr_<uuid7_hex> user identifier.
        """
        _ = parse_prefixed_uuid7(user.id, EntityPrefix.USER)
        _ = parse_prefixed_uuid7(user.organization_id, EntityPrefix.ORG)
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

    async def list_users(self, organization_id: str | None = None) -> Sequence[User]:
        """List persisted User entities, optionally filtered by organization_id.

        Args:
            organization_id: Optional org_<uuid7_hex> organization filter.

        Returns:
            Sequence of User domain models.
        """
        if organization_id is not None:
            _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORG)
        users = [
            item
            for item in self._store.seed_tables["users"].values()
            if isinstance(item, User) and (organization_id is None or item.organization_id == organization_id)
        ]
        users.sort(key=lambda u: u.id)
        return tuple(users)

    async def upsert_invitation(self, invitation: Invitation) -> str:
        """Upsert an Invitation entity in memory.

        Args:
            invitation: Validated Invitation domain model.

        Returns:
            Canonical inv_<uuid7_hex> invitation identifier.
        """
        _ = parse_prefixed_uuid7(invitation.id, EntityPrefix.INVITATION)
        _ = parse_prefixed_uuid7(invitation.organization_id, EntityPrefix.ORG)
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

    async def list_invitations(self, organization_id: str | None = None) -> Sequence[Invitation]:
        """List persisted Invitation entities, optionally filtered by organization_id.

        Args:
            organization_id: Optional org_<uuid7_hex> organization filter.

        Returns:
            Sequence of Invitation domain models.
        """
        if organization_id is not None:
            _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORG)
        invs = [
            item
            for item in self._store.seed_tables["invitations"].values()
            if isinstance(item, Invitation) and (organization_id is None or item.organization_id == organization_id)
        ]
        invs.sort(key=lambda i: i.id)
        return tuple(invs)

    async def upsert_tenant_secret(self, secret: TenantSecretDTO) -> str:
        """Upsert a TenantSecretDTO entity in memory.

        Args:
            secret: Validated TenantSecretDTO domain model.

        Returns:
            Canonical sec_<uuid7_hex> tenant secret identifier.
        """
        _ = parse_prefixed_uuid7(secret.id, EntityPrefix.TENANT_SECRET)
        _ = parse_prefixed_uuid7(secret.organization_id, EntityPrefix.ORG)
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

    async def list_tenant_secrets(self, organization_id: str | None = None) -> Sequence[TenantSecretDTO]:
        """List persisted TenantSecretDTO entities, optionally filtered by organization_id.

        Args:
            organization_id: Optional org_<uuid7_hex> organization filter.

        Returns:
            Sequence of TenantSecretDTO domain models.
        """
        if organization_id is not None:
            _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORG)
        secrets = [
            item
            for item in self._store.seed_tables["tenant_secrets"].values()
            if isinstance(item, TenantSecretDTO)
            and (organization_id is None or item.organization_id == organization_id)
        ]
        secrets.sort(key=lambda s: s.id)
        return tuple(secrets)

    async def upsert_execution_assignment(self, assignment: ExecutionAssignment) -> str:
        """Upsert an ExecutionAssignment entity in memory.

        Args:
            assignment: Validated ExecutionAssignment domain model.

        Returns:
            Canonical tsk_<uuid7_hex> execution assignment identifier.
        """
        _ = parse_prefixed_uuid7(assignment.id, EntityPrefix.ASSIGNMENT)
        _ = parse_prefixed_uuid7(assignment.organization_id, EntityPrefix.ORG)
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
    ) -> Sequence[ExecutionAssignment]:
        """List persisted ExecutionAssignment entities, optionally filtered by organization_id.

        Args:
            organization_id: Optional org_<uuid7_hex> organization filter.

        Returns:
            Sequence of ExecutionAssignment domain models.
        """
        if organization_id is not None:
            _ = parse_prefixed_uuid7(organization_id, EntityPrefix.ORG)
        assignments = [
            item
            for item in self._store.seed_tables["execution_assignments"].values()
            if isinstance(item, ExecutionAssignment)
            and (organization_id is None or item.organization_id == organization_id)
        ]
        assignments.sort(key=lambda a: a.id)
        return tuple(assignments)

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
        self._store.report_binaries[payload.report_id] = payload
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
        # Phase 4, Step 4.2: Enforce conditional expected_state_version OCC check and atomic increment
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
        reconstituted = ExecutionRecord.model_validate(
            target_record.model_dump(mode="json", exclude_none=True),
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

    async def seed_collection_batch(
        self,
        collection_name: str,
        items: Sequence[BaseModel],
    ) -> int:
        """Batch-upsert a validated seed collection in memory.

        Args:
            collection_name: Canonical collection or table name ('system_config' or 'system_configs', etc.).
            items: Sequence of validated Pydantic domain models to persist.

        Returns:
            Number of rows persisted into the target table.

        Raises:
            AppException: With VALIDATION_FAILED if collection_name is not an allowlisted seed table.
        """
        canonical = "system_configs" if collection_name == "system_config" else collection_name
        allowed = {
            "organizations",
            "users",
            "invitations",
            "tenant_secrets",
            "execution_assignments",
            "system_configs",
            "prompt_blocks",
            "steps",
            "workflows",
            "output_profiles",
            "executions",
            "report_artifacts",
            "report_binaries",
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
            "system_configs": (SystemConfigModelRegistry, SystemConfigMCPGateways),
            "prompt_blocks": (
                MatrixPromptBlock,
                SystemRulePromptBlock,
                PersonaPromptBlock,
                ProtocolPromptBlock,
            ),
            "steps": (Step,),
            "workflows": (Workflow,),
            "output_profiles": (OutputProfile,),
            "executions": (ExecutionRecord,),
            "report_artifacts": (ReportArtifact,),
            "report_binaries": (ReportBinaryPayloadDTO,),
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

        table_bucket = self._store.seed_tables[canonical]
        for idx, item in enumerate(items):
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
            "system_configs": len(self._store.seed_tables["system_configs"]),
            "prompt_blocks": len(self._store.seed_tables["prompt_blocks"]),
            "steps": len(self._store.seed_tables["steps"]),
            "workflows": len(self._store.seed_tables["workflows"]),
            "output_profiles": len(self._store.seed_tables["output_profiles"]),
            "executions": len(self._store.executions),
            "report_artifacts": len(self._store.seed_tables["report_artifacts"]),
            "report_binaries": len(self._store.report_binaries),
        }
        for key, min_expected in expected_counts.items():
            target_table = "system_configs" if key == "system_config" else key
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

        if "SET DEFAULT_TOAST_COMPRESSION" in normalized or "CREATE TABLE" in normalized:
            self._store.migrations_applied += 1
            return "CREATE TABLE"

        if normalized.startswith("TRUNCATE TABLE "):
            for tbl in self._store.seed_tables:
                if f"TRUNCATE TABLE {tbl.upper()}" in normalized:
                    self._store.seed_tables[tbl].clear()
                    return "TRUNCATE TABLE"
            if "TRUNCATE TABLE EXECUTIONS" in normalized:
                self._store.executions.clear()
                self._store.nodes.clear()
                self._store.edges.clear()
                return "TRUNCATE TABLE"
            if "TRUNCATE TABLE REPORT_BINARIES" in normalized:
                self._store.report_binaries.clear()
                return "TRUNCATE TABLE"
            return "TRUNCATE TABLE"

        if "INSERT INTO REPORT_BINARIES" in normalized:
            report_uuid = args[0] if isinstance(args[0], (uuid.UUID, str)) else str(args[0])
            report_id = format_prefixed_uuid7(report_uuid, EntityPrefix.REPORT)
            mime_type = str(args[1])
            pdf_bytes = bytes(args[2]) if isinstance(args[2], (bytes, bytearray, memoryview)) else b""
            size_bytes = int(str(args[3]))
            created_at = args[4] if isinstance(args[4], datetime) else datetime.now(timezone.utc)
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
            "system_configs",
            "prompt_blocks",
            "steps",
            "workflows",
            "output_profiles",
            "report_artifacts",
        ):
            if f"INSERT INTO {tbl.upper()}" in normalized:
                row_id = str(args[0])
                self._store.seed_tables[tbl][row_id] = tuple(_to_column_value(a) for a in args)
                return "INSERT 0 1"
            if f"DELETE FROM {tbl.upper()}" in normalized:
                if not args:
                    self._store.seed_tables[tbl].clear()
                    return "DELETE"
                row_id = str(args[0])
                if row_id in self._store.seed_tables[tbl]:
                    del self._store.seed_tables[tbl][row_id]
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
                "system_configs",
                "prompt_blocks",
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

        if "FROM EXECUTIONS" in normalized:
            return tuple(self._build_execution_record_row(rec) for rec in self._store.executions.values())

        for tbl in (
            "organizations",
            "users",
            "invitations",
            "tenant_secrets",
            "execution_assignments",
            "system_configs",
            "prompt_blocks",
            "steps",
            "workflows",
            "output_profiles",
            "report_artifacts",
        ):
            if f"FROM {tbl.upper()}" in normalized:
                cols = self._extract_select_columns(query)
                rows: list[AsyncPgRecordProtocol] = []
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
                        rows.append(InMemoryAsyncPgRecord(mapped))
                return tuple(rows)

        return ()

    @staticmethod
    def _zip_select_row(
        cols: list[str],
        entry: Sequence[_ColumnValue],
    ) -> dict[str, _ColumnValue]:
        """Map SELECT column names to stored positional values, synthesizing VIRTUAL created_at if omitted on INSERT."""
        if "created_at" in cols and len(entry) == len(cols) - 1:
            non_virtual_cols = [c for c in cols if c != "created_at"]
            mapped = {col: val for col, val in zip(non_virtual_cols, entry, strict=False)}
            pk_val = entry[0] if entry else None
            if isinstance(pk_val, uuid.UUID):
                ts_ms = (pk_val.int >> 80) & ((1 << 48) - 1)
                mapped["created_at"] = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
            else:
                mapped["created_at"] = datetime.now(timezone.utc)
            return mapped
        return {col: val for col, val in zip(cols, entry, strict=False)}

    @staticmethod
    def _extract_select_columns(query: str) -> list[str]:
        """Extract column names from a SELECT col1, col2, ... FROM statement."""
        norm_q = " ".join(query.strip().split())
        upper = norm_q.upper()
        select_idx = upper.find("SELECT ")
        from_idx = upper.find(" FROM ")
        if select_idx == -1 or from_idx == -1:
            return []
        cols_part = norm_q[select_idx + 7 : from_idx]
        return [c.strip().lower() for c in cols_part.split(",") if c.strip()]

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
                "created_by": rec.created_by,
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
                "system_configs",
                "prompt_blocks",
                "steps",
                "workflows",
                "output_profiles",
                "report_artifacts",
            ):
                if f"FROM {tbl.upper()}" in normalized:
                    return InMemoryAsyncPgRecord({"row_count": len(self._store.seed_tables[tbl])})
            if "FROM EXECUTIONS" in normalized:
                return InMemoryAsyncPgRecord({"row_count": len(self._store.executions)})
            if "FROM REPORT_BINARIES" in normalized:
                return InMemoryAsyncPgRecord({"row_count": len(self._store.report_binaries)})

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

        for tbl in (
            "organizations",
            "users",
            "invitations",
            "tenant_secrets",
            "execution_assignments",
            "system_configs",
            "prompt_blocks",
            "steps",
            "workflows",
            "output_profiles",
            "report_artifacts",
        ):
            if f"FROM {tbl.upper()}" in normalized and args:
                row_id = str(args[0])
                if row_id not in self._store.seed_tables[tbl]:
                    return None
                entry = self._store.seed_tables[tbl][row_id]
                if isinstance(entry, Sequence):
                    cols = self._extract_select_columns(query)
                    return InMemoryAsyncPgRecord(self._zip_select_row(cols, entry))

        return None


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
