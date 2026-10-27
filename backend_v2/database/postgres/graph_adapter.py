"""PostgreSQL 19 Zero-ORM Proposition Graph Adapter & CTE Reasoning Strategy.

Implements GraphMutationPort, TopologyResolutionPort, and CausalReasoningPort over
asyncpg connections using Single-Round Multi-CTE wave materialization with PostgreSQL 19
ON CONFLICT (run_id, local_key) DO SELECT RETURNING, recursive CYCLE detection,
Kahn wave resolution, and ANSI SQL Toulmin falsification queries.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import status
from pydantic import ConfigDict, Field
from pydantic_core import from_json, to_json

from backend_v2.database.postgres.pool import (
    AsyncPgConnectionProtocol,
    AsyncPgRecordProtocol,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX,
    V2CoreBase,
    format_prefixed_uuid7,
    parse_prefixed_uuid7,
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
from backend_v2.models.enums import (
    DependencyRelationType,
    EntityPrefix,
    PropositionNodeType,
)
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "CteReasoningStrategy",
    "PostgresGraphAdapter",
]

# Step 4: Single-Round Multi-CTE Wave Ingestion with PostgreSQL 19 ON CONFLICT DO SELECT RETURNING
_MATERIALIZE_WAVE_SQL: str = """
WITH input_nodes AS (
    SELECT
        uuidv7() AS generated_node_id,
        r.local_key,
        r.node_type,
        r.confidence,
        r.payload
    FROM jsonb_to_recordset($2::jsonb) AS r(
        local_key TEXT,
        node_type TEXT,
        confidence DOUBLE PRECISION,
        payload JSONB
    )
),
inserted_nodes AS (
    INSERT INTO quorum_nodes (node_id, run_id, local_key, node_type, confidence, payload)
    SELECT generated_node_id, $1::uuid, local_key, node_type, confidence, payload
    FROM input_nodes
    ON CONFLICT (run_id, local_key) DO SELECT
    RETURNING node_id, run_id, local_key, node_type, confidence, payload, created_at
),
input_edges AS (
    SELECT
        uuidv7() AS generated_edge_id,
        src.node_id AS source_id,
        tgt.node_id AS target_id,
        e.relation_type,
        e.causal_weight
    FROM jsonb_to_recordset($3::jsonb) AS e(
        source_key TEXT,
        target_key TEXT,
        relation_type TEXT,
        causal_weight DOUBLE PRECISION
    )
    INNER JOIN inserted_nodes AS src ON src.local_key = e.source_key
    INNER JOIN inserted_nodes AS tgt ON tgt.local_key = e.target_key
),
inserted_edges AS (
    INSERT INTO quorum_edges (edge_id, run_id, source_id, target_id, relation_type, causal_weight)
    SELECT generated_edge_id, $1::uuid, source_id, target_id, relation_type, causal_weight
    FROM input_edges
    ON CONFLICT (run_id, source_id, target_id, relation_type) DO NOTHING
    RETURNING edge_id
)
SELECT node_id, run_id, node_type, confidence, payload, created_at
FROM inserted_nodes
ORDER BY node_id ASC
"""

_UPSERT_NODES_SQL: str = """
INSERT INTO quorum_nodes (node_id, run_id, local_key, node_type, confidence, payload)
VALUES ($1::uuid, $2::uuid, $3, $4, $5::double precision, $6::jsonb)
ON CONFLICT (node_id) DO UPDATE SET
    node_type = EXCLUDED.node_type,
    confidence = EXCLUDED.confidence,
    payload = EXCLUDED.payload
"""

_UPSERT_EDGES_SQL: str = """
INSERT INTO quorum_edges (edge_id, run_id, source_id, target_id, relation_type, causal_weight)
VALUES ($1::uuid, $2::uuid, $3::uuid, $4::uuid, $5, $6::double precision)
ON CONFLICT (edge_id) DO UPDATE SET
    relation_type = EXCLUDED.relation_type,
    causal_weight = EXCLUDED.causal_weight
"""

_ASSERT_ACYCLIC_SQL: str = """
WITH RECURSIVE dag_walk AS (
    SELECT
        e.source_id,
        e.target_id,
        1 AS depth
    FROM quorum_edges AS e
    WHERE e.run_id = $1::uuid
    UNION ALL
    SELECT
        w.source_id,
        e.target_id,
        w.depth + 1
    FROM dag_walk AS w
    INNER JOIN quorum_edges AS e
        ON e.source_id = w.target_id
        AND e.run_id = $1::uuid
)
CYCLE target_id SET is_cycle USING traversal_path
SELECT traversal_path, is_cycle
FROM dag_walk
WHERE is_cycle = TRUE
LIMIT 1
"""

_FETCH_NEXT_KAHN_WAVE_SQL: str = """
SELECT n.node_id, n.run_id, n.node_type, n.confidence, n.payload, n.created_at
FROM quorum_nodes AS n
WHERE n.run_id = $1::uuid
  AND NOT EXISTS (
      SELECT 1
      FROM quorum_edges AS e
      WHERE e.run_id = $1::uuid
        AND e.target_id = n.node_id
  )
ORDER BY n.node_id ASC
"""

_FIND_FALSIFIED_CLAIMS_SQL: str = """
SELECT
    r.node_id AS rebuttal_id,
    w.node_id AS invalidated_warrant_id,
    c.node_id AS falsified_claim_id,
    r.confidence AS rebuttal_confidence,
    c.payload->>'statement' AS claim_statement
FROM quorum_nodes AS r
INNER JOIN quorum_edges AS e1
    ON e1.source_id = r.node_id
    AND e1.run_id = r.run_id
    AND e1.relation_type = 'rebuts'
INNER JOIN quorum_nodes AS w
    ON w.node_id = e1.target_id
    AND w.run_id = r.run_id
    AND w.node_type = 'warrant'
INNER JOIN quorum_edges AS e2
    ON e2.source_id = w.node_id
    AND e2.run_id = r.run_id
    AND e2.relation_type = 'warrants'
INNER JOIN quorum_nodes AS c
    ON c.node_id = e2.target_id
    AND c.run_id = r.run_id
    AND c.node_type = 'claim'
WHERE r.run_id = $1::uuid
  AND r.node_type = 'rebuttal'
  AND r.confidence >= $2::double precision
ORDER BY r.confidence DESC, c.node_id ASC
"""


class _PropositionNodeRowDTO(V2CoreBase):
    """Strict internal boundary DTO for hydrating a PropositionNode database row.

    Attributes:
        node_id: Formatted nod_<uuid7_hex> identifier.
        run_id: Formatted exe_<uuid7_hex> identifier.
        node_type: Validated PropositionNodeType enum.
        confidence: Confidence score in [0.0, 1.0].
        payload: Validated PropositionPayloadDTO.
        created_at: Timestamp extracted from PostgreSQL VIRTUAL column.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    node_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Formatted nod_<uuid7_hex> ID.")]
    run_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Formatted exe_<uuid7_hex> ID.")]
    node_type: Annotated[PropositionNodeType, Field(description="Proposition node classification.")]
    confidence: Annotated[float, Field(description="Confidence score.")]
    payload: Annotated[PropositionPayloadDTO, Field(description="Validated proposition payload.")]
    created_at: Annotated[datetime, Field(description="Timestamp from PostgreSQL VIRTUAL column.")]


class _FalsifiedClaimRowDTO(V2CoreBase):
    """Strict internal boundary DTO for hydrating a FalsifiedClaimMatch database row.

    Attributes:
        rebuttal_id: Formatted nod_<uuid7_hex> rebuttal ID.
        invalidated_warrant_id: Formatted nod_<uuid7_hex> warrant ID.
        falsified_claim_id: Formatted nod_<uuid7_hex> claim ID.
        rebuttal_confidence: Confidence score of the rebuttal node.
        claim_statement: Statement text of the falsified claim.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rebuttal_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Rebuttal node ID.")]
    invalidated_warrant_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Warrant node ID.")]
    falsified_claim_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Claim node ID.")]
    rebuttal_confidence: Annotated[float, Field(description="Rebuttal confidence score.")]
    claim_statement: Annotated[str, Field(min_length=1, description="Claim statement text.")]


def _coerce_uuid_or_str(raw: object) -> uuid.UUID | str:
    """Narrow a raw database UUID or string column value to uuid.UUID | str.

    Args:
        raw: Database value from an asyncpg record column.

    Returns:
        Value narrowed to uuid.UUID or str.
    """
    if isinstance(raw, (uuid.UUID, str)):
        return raw
    return str(raw)


def _hydrate_payload_dto(raw_payload: object) -> PropositionPayloadDTO:
    """Hydrate a raw JSONB column value into an immutable PropositionPayloadDTO.

    Args:
        raw_payload: Decoded JSONB object, UTF-8 JSON string/bytes, or PropositionPayloadDTO.

    Returns:
        Validated PropositionPayloadDTO instance.
    """
    if isinstance(raw_payload, PropositionPayloadDTO):
        return raw_payload
    if isinstance(raw_payload, (str, bytes, bytearray)):
        return PropositionPayloadDTO.model_validate_json(raw_payload)
    if isinstance(raw_payload, memoryview):
        return PropositionPayloadDTO.model_validate(from_json(bytes(raw_payload)), strict=False)
    return PropositionPayloadDTO.model_validate(raw_payload, strict=False)


def _hydrate_proposition_node(row: AsyncPgRecordProtocol) -> PropositionNode:
    """Hydrate an asyncpg record row into an immutable PropositionNode via direct subscripting.

    Args:
        row: Database record conforming to AsyncPgRecordProtocol.

    Returns:
        Strictly validated PropositionNode domain model.
    """
    node_id_str = format_prefixed_uuid7(_coerce_uuid_or_str(row["node_id"]), EntityPrefix.NODE)
    run_id_str = format_prefixed_uuid7(_coerce_uuid_or_str(row["run_id"]), EntityPrefix.EXECUTION)
    payload_dto = _hydrate_payload_dto(row["payload"])

    row_dto = _PropositionNodeRowDTO.model_validate(
        {
            "node_id": node_id_str,
            "run_id": run_id_str,
            "node_type": row["node_type"],
            "confidence": row["confidence"],
            "payload": payload_dto,
            "created_at": row["created_at"],
        },
        strict=False,
    )
    return PropositionNode(
        node_id=row_dto.node_id,
        run_id=row_dto.run_id,
        node_type=row_dto.node_type,
        confidence=row_dto.confidence,
        payload=row_dto.payload,
        created_at=row_dto.created_at,
    )


def _extract_cycle_node_ids(raw_path: object) -> tuple[str, ...]:
    """Convert a PostgreSQL CYCLE traversal_path array into prefixed nod_<uuid7_hex> strings.

    Args:
        raw_path: Raw traversal_path sequence returned by PostgreSQL CYCLE clause.

    Returns:
        Tuple of canonical nod_<uuid7_hex> identifiers forming the cycle.
    """
    if not isinstance(raw_path, Sequence) or isinstance(raw_path, (str, bytes, bytearray)):
        return ()
    formatted: list[str] = []
    for item in raw_path:
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            for sub_item in item:
                formatted.append(format_prefixed_uuid7(_coerce_uuid_or_str(sub_item), EntityPrefix.NODE))
        else:
            formatted.append(format_prefixed_uuid7(_coerce_uuid_or_str(item), EntityPrefix.NODE))
    return tuple(formatted)


class CteReasoningStrategy:
    """Production CausalReasoningPort strategy executing ANSI SQL Toulmin falsification queries.

    Attributes:
        command_timeout_seconds: Bounded query timeout in seconds from settings.py.
    """

    def __init__(
        self,
        connection: AsyncPgConnectionProtocol,
        command_timeout_seconds: float | None = None,
    ) -> None:
        """Initialize the CTE reasoning strategy over an active connection.

        Args:
            connection: Active database connection conforming to AsyncPgConnectionProtocol.
            command_timeout_seconds: Explicit command timeout in seconds, or None to use settings.py.
        """
        resolved_timeout = (
            command_timeout_seconds
            if command_timeout_seconds is not None
            else get_settings().postgres_command_timeout_seconds
        )
        self._conn: AsyncPgConnectionProtocol = connection
        self.command_timeout_seconds: float = resolved_timeout

    async def find_falsified_claims(
        self,
        run_id: str,
        min_confidence: float = 0.70,
    ) -> Sequence[FalsifiedClaimMatch]:
        """Execute the 3-way Toulmin falsification join for a workflow execution run.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.
            min_confidence: Minimum rebuttal confidence threshold in [0.0, 1.0].

        Returns:
            Sequence of FalsifiedClaimMatch DTOs ordered by rebuttal confidence descending.

        Raises:
            AppException: With VALIDATION_FAILED if run_id or min_confidence is invalid,
                or STORAGE_ACCESS_FAILED if query execution fails.
        """
        if not 0.0 <= min_confidence <= 1.0:
            msg = f"min_confidence must be between 0.0 and 1.0, got {min_confidence}."
            logger.error(
                "[CteReasoningStrategy] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "run_id": run_id},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        run_uuid = parse_prefixed_uuid7(run_id, EntityPrefix.EXECUTION)
        try:
            rows = await self._conn.fetch(
                _FIND_FALSIFIED_CLAIMS_SQL,
                run_uuid,
                float(min_confidence),
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to execute Toulmin falsification query for run '{run_id}': {exc}"
            logger.error(
                "[CteReasoningStrategy] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "run_id": run_id},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        matches: list[FalsifiedClaimMatch] = []
        for row in rows:
            row_dto = _FalsifiedClaimRowDTO.model_validate(
                {
                    "rebuttal_id": format_prefixed_uuid7(_coerce_uuid_or_str(row["rebuttal_id"]), EntityPrefix.NODE),
                    "invalidated_warrant_id": format_prefixed_uuid7(
                        _coerce_uuid_or_str(row["invalidated_warrant_id"]),
                        EntityPrefix.NODE,
                    ),
                    "falsified_claim_id": format_prefixed_uuid7(
                        _coerce_uuid_or_str(row["falsified_claim_id"]),
                        EntityPrefix.NODE,
                    ),
                    "rebuttal_confidence": row["rebuttal_confidence"],
                    "claim_statement": row["claim_statement"],
                },
                strict=False,
            )
            matches.append(
                FalsifiedClaimMatch(
                    rebuttal_id=row_dto.rebuttal_id,
                    invalidated_warrant_id=row_dto.invalidated_warrant_id,
                    falsified_claim_id=row_dto.falsified_claim_id,
                    rebuttal_confidence=row_dto.rebuttal_confidence,
                    claim_statement=row_dto.claim_statement,
                )
            )
        return tuple(matches)


class PostgresGraphAdapter:
    """Zero-ORM PostgreSQL 19 adapter implementing GraphMutationPort, TopologyResolutionPort, and CausalReasoningPort.

    Attributes:
        command_timeout_seconds: Bounded query timeout in seconds resolved from settings.py.
    """

    def __init__(
        self,
        connection: AsyncPgConnectionProtocol,
        command_timeout_seconds: float | None = None,
    ) -> None:
        """Initialize the PostgreSQL graph adapter over an active connection.

        Args:
            connection: Active database connection conforming to AsyncPgConnectionProtocol.
            command_timeout_seconds: Explicit command timeout in seconds, or None to use settings.py.
        """
        resolved_timeout = (
            command_timeout_seconds
            if command_timeout_seconds is not None
            else get_settings().postgres_command_timeout_seconds
        )
        self._conn: AsyncPgConnectionProtocol = connection
        self.command_timeout_seconds: float = resolved_timeout
        self._reasoning: CteReasoningStrategy = CteReasoningStrategy(
            connection=connection,
            command_timeout_seconds=resolved_timeout,
        )

    def _validate_wave_drafts(
        self,
        run_id: str,
        node_drafts: Sequence[NodeDraft],
        edge_drafts: Sequence[EdgeDraft],
    ) -> None:
        """Validate uniqueness of NodeDraft local_key values and EdgeDraft referential integrity.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.
            node_drafts: Wave node drafts to validate.
            edge_drafts: Wave edge drafts to validate against node_drafts.

        Raises:
            AppException: With VALIDATION_FAILED if duplicate local_key or dangling edge keys exist.
        """
        seen_keys: set[str] = set()
        for draft in node_drafts:
            if draft.local_key in seen_keys:
                msg = f"Duplicate NodeDraft local_key '{draft.local_key}' in wave for run '{run_id}'."
                logger.error(
                    "[PostgresGraphAdapter] %s: %s",
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

        for edge in edge_drafts:
            if edge.source_key not in seen_keys or edge.target_key not in seen_keys:
                msg = (
                    f"Dangling EdgeDraft reference ({edge.source_key!r} -> {edge.target_key!r}) "
                    f"in wave for run '{run_id}': endpoints must exist in node_drafts."
                )
                logger.error(
                    "[PostgresGraphAdapter] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "run_id": run_id},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

    async def materialize_wave(
        self,
        run_id: str,
        node_drafts: Sequence[NodeDraft],
        edge_drafts: Sequence[EdgeDraft],
    ) -> Sequence[PropositionNode]:
        """Materialize a Kahn topological wave of NodeDraft and EdgeDraft items in one Multi-CTE roundtrip.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.
            node_drafts: Symbolic NodeDraft instances to materialize.
            edge_drafts: Symbolic EdgeDraft instances linking local_key endpoints.

        Returns:
            Sequence of hydrated PropositionNode domain models ordered by node_id ascending.

        Raises:
            AppException: With VALIDATION_FAILED on invalid run_id, duplicate local_key, or
                dangling edge endpoints, or STORAGE_ACCESS_FAILED on database failure.
        """
        run_uuid = parse_prefixed_uuid7(run_id, EntityPrefix.EXECUTION)
        self._validate_wave_drafts(run_id, node_drafts, edge_drafts)
        if not node_drafts:
            return ()

        nodes_json = to_json(list(node_drafts)).decode("utf-8")
        edges_json = to_json(list(edge_drafts)).decode("utf-8")

        try:
            rows = await self._conn.fetch(
                _MATERIALIZE_WAVE_SQL,
                run_uuid,
                nodes_json,
                edges_json,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to materialize wave in PostgreSQL for run '{run_id}': {exc}"
            logger.error(
                "[PostgresGraphAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "run_id": run_id},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        return tuple(_hydrate_proposition_node(row) for row in rows)

    async def upsert_wave_batch(
        self,
        nodes: Sequence[PropositionNode],
        edges: Sequence[DependencyEdge],
    ) -> None:
        """Batch-upsert persisted PropositionNode and DependencyEdge models via executemany.

        Args:
            nodes: Persisted PropositionNode instances to upsert.
            edges: Persisted DependencyEdge instances to upsert.

        Raises:
            AppException: With VALIDATION_FAILED on invalid prefixed UUIDv7 identifiers or
                STORAGE_ACCESS_FAILED on database execution failure.
        """
        node_params: list[Sequence[object]] = []
        for node in nodes:
            node_uuid = parse_prefixed_uuid7(node.node_id, EntityPrefix.NODE)
            run_uuid = parse_prefixed_uuid7(node.run_id, EntityPrefix.EXECUTION)
            payload_json = to_json(node.payload).decode("utf-8")
            node_params.append(
                (
                    node_uuid,
                    run_uuid,
                    None,
                    node.node_type.value,
                    float(node.confidence),
                    payload_json,
                )
            )

        edge_params: list[Sequence[object]] = []
        for edge in edges:
            edge_uuid = parse_prefixed_uuid7(edge.edge_id, EntityPrefix.EDGE)
            run_uuid = parse_prefixed_uuid7(edge.run_id, EntityPrefix.EXECUTION)
            source_uuid = parse_prefixed_uuid7(edge.source_id, EntityPrefix.NODE)
            target_uuid = parse_prefixed_uuid7(edge.target_id, EntityPrefix.NODE)
            edge_params.append(
                (
                    edge_uuid,
                    run_uuid,
                    source_uuid,
                    target_uuid,
                    DependencyRelationType(edge.relation_type).value,
                    float(edge.causal_weight),
                )
            )

        try:
            if node_params:
                await self._conn.executemany(
                    _UPSERT_NODES_SQL,
                    node_params,
                    timeout=self.command_timeout_seconds,
                )
            if edge_params:
                await self._conn.executemany(
                    _UPSERT_EDGES_SQL,
                    edge_params,
                    timeout=self.command_timeout_seconds,
                )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to upsert wave batch in PostgreSQL: {exc}"
            logger.error(
                "[PostgresGraphAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

    async def assert_acyclic(self, run_id: str) -> None:
        """Verify that the persisted proposition graph for run_id contains zero directed cycles.

        Executes PostgreSQL ANSI SQL WITH RECURSIVE ... CYCLE traversal and raises
        CycleDetectedError immediately if a cycle is detected.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.

        Raises:
            CycleDetectedError: If a directed cycle is discovered in quorum_edges.
            AppException: With VALIDATION_FAILED on invalid run_id or STORAGE_ACCESS_FAILED on query error.
        """
        run_uuid = parse_prefixed_uuid7(run_id, EntityPrefix.EXECUTION)
        try:
            row = await self._conn.fetchrow(
                _ASSERT_ACYCLIC_SQL,
                run_uuid,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to execute cycle detection query for run '{run_id}': {exc}"
            logger.error(
                "[PostgresGraphAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "run_id": run_id},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        if row is not None and bool(row["is_cycle"]):
            cycle_path = _extract_cycle_node_ids(row["traversal_path"])
            logger.error(
                "[PostgresGraphAdapter] %s: Directed cycle detected in run '%s': %s",
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
        """Fetch all PropositionNode roots with in-degree 0 for the specified run_id.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.

        Returns:
            Sequence of PropositionNode instances ordered by node_id ascending.

        Raises:
            AppException: With VALIDATION_FAILED on invalid run_id or STORAGE_ACCESS_FAILED on query error.
        """
        run_uuid = parse_prefixed_uuid7(run_id, EntityPrefix.EXECUTION)
        try:
            rows = await self._conn.fetch(
                _FETCH_NEXT_KAHN_WAVE_SQL,
                run_uuid,
                timeout=self.command_timeout_seconds,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to fetch next Kahn wave for run '{run_id}': {exc}"
            logger.error(
                "[PostgresGraphAdapter] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "run_id": run_id},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        return tuple(_hydrate_proposition_node(row) for row in rows)

    async def find_falsified_claims(
        self,
        run_id: str,
        min_confidence: float = 0.70,
    ) -> Sequence[FalsifiedClaimMatch]:
        """Delegate Toulmin falsification query execution to CteReasoningStrategy.

        Args:
            run_id: Canonical exe_<uuid7_hex> execution identifier.
            min_confidence: Minimum rebuttal confidence threshold in [0.0, 1.0].

        Returns:
            Sequence of FalsifiedClaimMatch DTOs.

        Raises:
            AppException: Propagated from CteReasoningStrategy on validation or database error.
        """
        return await self._reasoning.find_falsified_claims(run_id=run_id, min_confidence=min_confidence)
