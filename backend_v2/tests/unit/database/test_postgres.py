"""Contract Test Suite & ISTQB Negative Verification for PostgreSQL 19 Zero-ORM Architecture.

Verifies 1:1 behavioral parity across InMemoryUnitOfWork and PostgresUnitOfWork (backed by
InMemoryAsyncPgPool from backend_v2/tests/fakes/in_memory_uow.py), Single-Round Multi-CTE
wave materialization with ON CONFLICT DO SELECT RETURNING, Toulmin falsification queries,
ReportBinaryPayloadDTO TOAST roundtrips, binary pydantic_core JSONB codecs, 1:1 DDL Schema
vs. Domain DTO Column Naming Parity across all 12 tables, and ISTQB negative boundaries.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import types
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import pytest
from pydantic import ConfigDict, Field, ValidationError

from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.database.postgres import (
    AsyncPgConnectionProtocol,
    AsyncPgPoolProtocol,
    CteReasoningStrategy,
    PostgresEntityAdapter,
    PostgresGraphAdapter,
    PostgresPoolManager,
    PostgresUnitOfWork,
    decode_jsonb_binary,
    encode_jsonb_binary,
    init_connection,
)
from backend_v2.database.postgres.entity_adapter import (
    _coerce_float,
    _coerce_uuid_or_str,
    _decode_jsonb_column,
)
from backend_v2.database.postgres.graph_adapter import (
    _MATERIALIZE_WAVE_SQL,
    _extract_cycle_node_ids,
    _hydrate_payload_dto,
)
from backend_v2.database.postgres.graph_adapter import (
    _coerce_uuid_or_str as _graph_coerce_uuid_or_str,
)
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.main import _validate_database_preflight
from backend_v2.models.auth import Invitation, Organization, SubscriptionStatus, TenantSecretDTO, User, UserRole
from backend_v2.models.core_base import (
    I18nText,
    V2CoreBase,
    generate_uuid7,
    generate_uuid7_opaque_id,
    parse_prefixed_uuid7,
)
from backend_v2.models.domain.base import AuditLogRecord, UsageRecord
from backend_v2.models.domain.execution import (
    ExecutionAssignment,
    ExecutionRecord,
    ExecutionStep,
    ExecutionSummarySnapshot,
    FrozenContext,
)
from backend_v2.models.domain.inputs import WorkflowInputs
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
    ReportBinaryPayloadDTO,
)
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    MCPAuditTrace,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.mcp import (
    MCPIconDTO,
    MCPServerInfoDTO,
    MCPToolExecutionDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
)
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import (
    CognitiveTier,
    DependencyRelationType,
    EngineType,
    EntityPrefix,
    ExecutionStatus,
    JSONSchemaPropertyType,
    MCPAuthType,
    MCPTransportType,
    PropositionNodeType,
    SecretScope,
    SecretStorageMode,
    StepType,
    StepZone,
    StorageBackend,
    SystemLocale,
    ToolCapability,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.seed.run_seed import _seed_postgres
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_uow import (
    InMemoryAsyncPgPool,
    InMemoryAsyncPgRecord,
    InMemoryUnitOfWork,
)
from scripts.audit_zero_orm_strictness import (
    ZeroOrmRuleCode,
    audit_python_file,
    audit_sql_migration_file,
    run_zero_orm_audit,
)

_MIGRATION_SQL_PATH: Path = (
    Path(__file__).resolve().parents[3] / "database" / "migrations" / "001_pg19_uuidv7_schema.sql"
)


class _UnitOfWorkHarness(V2CoreBase):
    """Typed test container pairing a QuorumUnitOfWork factory with its backing pool if present.

    Attributes:
        backend_label: Identifier of the UoW implementation under test ('in_memory' or 'postgres').
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    backend_label: Annotated[str, Field(min_length=1, description="UoW variant label.")]


def _build_uow_instance(variant: str) -> QuorumUnitOfWork:
    """Construct either an InMemoryUnitOfWork or a PostgresUnitOfWork backed by InMemoryAsyncPgPool.

    Args:
        variant: Either 'in_memory' or 'postgres'.

    Returns:
        Configured QuorumUnitOfWork instance.
    """
    if variant == "in_memory":
        return InMemoryUnitOfWork()
    pool = InMemoryAsyncPgPool()
    settings = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="db.internal",
        postgres_port=5432,
        postgres_user="quorum",
        postgres_db="quorum",
        postgres_command_timeout_seconds=12.0,
    )
    pool_manager = PostgresPoolManager(settings=settings, pool=pool)
    return PostgresUnitOfWork(pool_manager=pool_manager)


@pytest.fixture(params=["in_memory", "postgres"])
def uow(request: pytest.FixtureRequest) -> QuorumUnitOfWork:
    """Provide parameterized QuorumUnitOfWork across InMemoryUnitOfWork and PostgresUnitOfWork.

    Args:
        request: Pytest fixture request carrying 'in_memory' or 'postgres' param.

    Returns:
        Parameterized QuorumUnitOfWork instance.
    """
    variant = str(request.param)
    harness = _UnitOfWorkHarness(backend_label=variant)
    return _build_uow_instance(harness.backend_label)


def _extract_sql_table_columns(sql_text: str) -> dict[str, set[str]]:
    """Parse all CREATE TABLE blocks in 001_pg19_uuidv7_schema.sql into column sets.

    Args:
        sql_text: Raw SQL DDL content.

    Returns:
        Mapping of lowercase table_name to its set of declared column names.
    """
    pattern = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)\s*\((.*?)\);",
        re.IGNORECASE | re.DOTALL,
    )
    tables: dict[str, set[str]] = {}
    sql_Constraint_keywords = {
        "CONSTRAINT",
        "PRIMARY",
        "FOREIGN",
        "UNIQUE",
        "CHECK",
        "OR",
        "AND",
    }
    for match in pattern.finditer(sql_text):
        table_name = match.group(1).lower()
        body = match.group(2)
        top_level_items: list[str] = []
        buf: list[str] = []
        depth = 0
        in_quote = False
        for raw_line in body.splitlines():
            code_line = raw_line.split("--", 1)[0]
            for ch in code_line:
                if ch == "'":
                    in_quote = not in_quote
                    buf.append(ch)
                elif not in_quote and ch == "(":
                    depth += 1
                    buf.append(ch)
                elif not in_quote and ch == ")":
                    depth = max(0, depth - 1)
                    buf.append(ch)
                elif not in_quote and depth == 0 and ch == ",":
                    top_level_items.append("".join(buf).strip())
                    buf = []
                else:
                    buf.append(ch)
            buf.append(" ")
        if "".join(buf).strip():
            top_level_items.append("".join(buf).strip())

        cols: set[str] = set()
        for item in top_level_items:
            tokens = item.split()
            if not tokens:
                continue
            first_word = tokens[0].upper()
            if first_word in sql_Constraint_keywords:
                continue
            col_name = tokens[0].strip('"').lower()
            cols.add(col_name)
        tables[table_name] = cols
    return tables


# ============================================================================
# Positive Case 1: Single-Round Wave Materialization & Roundtrip
# ============================================================================


@pytest.mark.asyncio
async def test_single_round_wave_materialization(uow: QuorumUnitOfWork) -> None:
    """Verify Single-Round Multi-CTE wave materialization, DO SELECT idempotency, Kahn wave, and upsert."""
    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    atom_id = generate_uuid7_opaque_id(EntityPrefix.TDA)

    node_drafts = (
        NodeDraft(
            local_key="ground_1",
            node_type=PropositionNodeType.GROUND,
            confidence=0.95,
            payload=PropositionPayloadDTO(
                statement="Empirical revenue grew 24% YoY in Q4.",
                source_atom_id=atom_id,
                source_quotes=("revenue grew 24% YoY",),
                metadata={"quarter": "Q4", "verified": True},
            ),
        ),
        NodeDraft(
            local_key="warrant_1",
            node_type=PropositionNodeType.WARRANT,
            confidence=0.88,
            payload=PropositionPayloadDTO(
                statement="Sustained YoY growth above 20% indicates product-market expansion.",
                source_quotes=("growth above 20%",),
                metadata={"tier": 2},
            ),
        ),
        NodeDraft(
            local_key="claim_1",
            node_type=PropositionNodeType.CLAIM,
            confidence=0.91,
            payload=PropositionPayloadDTO(
                statement="The enterprise segment achieved strong product-market expansion.",
                source_quotes=("enterprise segment achieved",),
                metadata={"score": 4.5},
            ),
        ),
    )

    edge_drafts = (
        EdgeDraft(
            source_key="ground_1",
            target_key="warrant_1",
            relation_type=DependencyRelationType.SUPPORTS,
            causal_weight=0.85,
        ),
        EdgeDraft(
            source_key="warrant_1",
            target_key="claim_1",
            relation_type=DependencyRelationType.WARRANTS,
            causal_weight=0.90,
        ),
    )

    async with uow:
        materialized = await uow.graph.materialize_wave(run_id, node_drafts, edge_drafts)
        assert len(materialized) == 3

        # Verify canonical nod_<uuid7_hex> IDs in monotonically increasing order and created_at
        node_ids = [n.node_id for n in materialized]
        assert node_ids == sorted(node_ids)
        for node in materialized:
            parsed_uuid = parse_prefixed_uuid7(node.node_id, EntityPrefix.NODE)
            assert parsed_uuid.version == 7
            assert node.run_id == run_id
            assert isinstance(node.created_at, datetime)

        # Verify ON CONFLICT (run_id, local_key) DO SELECT RETURNING idempotency
        rematerialized = await uow.graph.materialize_wave(run_id, node_drafts, edge_drafts)
        assert [n.node_id for n in rematerialized] == node_ids

        # Verify Kahn wave resolution (only ground_1 has in_degree == 0)
        roots = await uow.topology.fetch_next_kahn_wave(run_id)
        assert len(roots) == 1
        assert roots[0].node_type == PropositionNodeType.GROUND
        assert roots[0].payload.statement == "Empirical revenue grew 24% YoY in Q4."

        # Verify DAG acyclicity passes on valid chain
        await uow.graph.assert_acyclic(run_id)

        # Verify empty wave returns empty sequence cleanly
        empty_wave = await uow.graph.materialize_wave(run_id, (), ())
        assert len(empty_wave) == 0

        # Verify upsert_wave_batch updates node confidence and inserts an additional edge
        updated_ground = materialized[0].model_copy(update={"confidence": 0.99})
        direct_edge = DependencyEdge(
            edge_id=generate_uuid7_opaque_id(EntityPrefix.EDGE),
            run_id=run_id,
            source_id=materialized[0].node_id,
            target_id=materialized[2].node_id,
            relation_type=DependencyRelationType.CAUSES,
            causal_weight=0.75,
            created_at=datetime.now(UTC),
        )
        await uow.graph.upsert_wave_batch((updated_ground,), (direct_edge,))
        await uow.graph.assert_acyclic(run_id)

    # Verify state persisted after UoW commit
    async with uow:
        committed_roots = await uow.topology.fetch_next_kahn_wave(run_id)
        assert len(committed_roots) == 1
        assert committed_roots[0].confidence == 0.99


# ============================================================================
# Positive Case 2: Toulmin Falsification Query Parity
# ============================================================================


@pytest.mark.asyncio
async def test_toulmin_falsification_query_parity(uow: QuorumUnitOfWork) -> None:
    """Verify Toulmin rebuttal -> rebuts -> warrant -> warrants -> claim falsification parity."""
    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)

    node_drafts = (
        NodeDraft(
            local_key="rebuttal_high",
            node_type=PropositionNodeType.REBUTTAL,
            confidence=0.92,
            payload=PropositionPayloadDTO(
                statement="Independent audit revealed Q4 revenue included non-recurring one-off credits.",
                metadata={},
            ),
        ),
        NodeDraft(
            local_key="rebuttal_low",
            node_type=PropositionNodeType.REBUTTAL,
            confidence=0.55,
            payload=PropositionPayloadDTO(
                statement="Minor seasonal fluctuation noted in Q4.",
                metadata={},
            ),
        ),
        NodeDraft(
            local_key="warrant_core",
            node_type=PropositionNodeType.WARRANT,
            confidence=0.84,
            payload=PropositionPayloadDTO(
                statement="Recurring revenue growth proves sustainable expansion.",
                metadata={},
            ),
        ),
        NodeDraft(
            local_key="claim_target",
            node_type=PropositionNodeType.CLAIM,
            confidence=0.89,
            payload=PropositionPayloadDTO(
                statement="Core SaaS ARR expanded organically without one-off distortion.",
                metadata={},
            ),
        ),
    )

    edge_drafts = (
        EdgeDraft(
            source_key="rebuttal_high",
            target_key="warrant_core",
            relation_type=DependencyRelationType.REBUTS,
            causal_weight=-0.92,
        ),
        EdgeDraft(
            source_key="rebuttal_low",
            target_key="warrant_core",
            relation_type=DependencyRelationType.REBUTS,
            causal_weight=-0.55,
        ),
        EdgeDraft(
            source_key="warrant_core",
            target_key="claim_target",
            relation_type=DependencyRelationType.WARRANTS,
            causal_weight=0.88,
        ),
    )

    async with uow:
        nodes = await uow.graph.materialize_wave(run_id, node_drafts, edge_drafts)
        by_statement = {n.payload.statement: n for n in nodes}

        matches = await uow.reasoning.find_falsified_claims(run_id, min_confidence=0.80)
        assert len(matches) == 1
        match = matches[0]
        assert isinstance(match, FalsifiedClaimMatch)
        assert (
            match.rebuttal_id
            == by_statement["Independent audit revealed Q4 revenue included non-recurring one-off credits."].node_id
        )
        assert (
            match.invalidated_warrant_id
            == by_statement["Recurring revenue growth proves sustainable expansion."].node_id
        )
        assert (
            match.falsified_claim_id
            == by_statement["Core SaaS ARR expanded organically without one-off distortion."].node_id
        )
        assert match.rebuttal_confidence == 0.92
        assert match.claim_statement == "Core SaaS ARR expanded organically without one-off distortion."

        # Lowering threshold to 0.50 returns both rebuttals ordered by confidence descending
        all_matches = await uow.reasoning.find_falsified_claims(run_id, min_confidence=0.50)
        assert len(all_matches) == 2
        assert all_matches[0].rebuttal_confidence == 0.92
        assert all_matches[1].rebuttal_confidence == 0.55


# ============================================================================
# Positive Case 3: Report Binary TOAST Roundtrip & Binary JSONB Codec
# ============================================================================


@pytest.mark.asyncio
async def test_report_binary_toast_and_execution_roundtrip(uow: QuorumUnitOfWork) -> None:
    """Verify ReportBinaryPayloadDTO TOAST roundtrip, ExecutionRecord FinOps + MCP trace roundtrip, and JSONB codec."""
    report_id = generate_uuid7_opaque_id(EntityPrefix.REPORT)
    pdf_payload = b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"
    now_utc = datetime.now(UTC)

    binary_dto = ReportBinaryPayloadDTO(
        report_id=report_id,
        mime_type="application/pdf",
        pdf_bytes=pdf_payload,
        size_bytes=len(pdf_payload),
        created_at=now_utc,
    )

    exec_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    wf_id = generate_uuid7_opaque_id(EntityPrefix.WORKFLOW)
    gw_id = generate_uuid7_opaque_id(EntityPrefix.MCP_GATEWAY)
    mcp_trace = MCPAuditTrace(
        id=generate_uuid7_opaque_id(EntityPrefix.TDA),
        tool_id="web_search_exa",
        gateway_id=gw_id,
        gateway_slug="exa_gateway",
        namespaced_alias="exa_gateway__web_search_exa",
        step_name="step_fact_verification",
        claim_text="Revenue grew 24% YoY",
        query="company Q4 revenue YoY growth",
        knowledge_gap="Verify external audited Q4 filings",
        search_rationale="Cross-check internal claim against SEC filing",
        reasoning="Confirmed in Q4 10-K report",
        response_summary="Audited Q4 revenue increased 24.0% year-over-year.",
        source_urls=["https://sec.gov/Archives/edgar/data/10k"],
        impacted_axis_names=["Financial Accuracy"],
        timestamp=now_utc,
        duration_ms=412,
    )
    trace_event = TraceEvent(
        event_id=generate_uuid7(),
        timestamp=now_utc,
        step_name="step_fact_verification",
        event_type="output",
        content="Step completed with external MCP verification.",
        metadata=TraceEventMetadataDTO(mcp_audit_traces=[]),
        mcp_audit_traces=[mcp_trace],
    )
    execution_record = ExecutionRecord(
        id=exec_id,
        organization_id=generate_uuid7_opaque_id(EntityPrefix.ORGANIZATION),
        workflow_id=wf_id,
        workflow_version=2,
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        progress=100,
        status_message="Completed",
        context_variables=ContextVariablesDTO(variables={}),
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        profile_syntheses={},
        source_identity_manifest={},
        frozen_context=FrozenContext(
            compiled_prompts={"stp_0195f3a0000070008000a1b2c3d4e5f6": "<system_directive>Verify</system_directive>"},
            injected_theory=InjectedTheoryManifestDTO(theories={}),
            generated_schemas=GeneratedSchemaManifestDTO(schemas={}),
            ui_hints_snapshot={},
            mcp_tool_audit=[mcp_trace],
        ),
        steps=[
            ExecutionStep(
                id="stp_0195f3a0000070008000a1b2c3d4e5f6",
                label="Fact Verification",
                status=ExecutionStatus.PASSED,
                scorecard_atoms={},
                prompt_tokens=1200,
                completion_tokens=350,
                cached_tokens=800,
                reasoning_tokens=150,
                cost_usd=0.0042,
                duration_ms=1850,
                progress=100,
            )
        ],
        execution_trace=[trace_event],
        prompt_tokens=1200,
        completion_tokens=350,
        cached_tokens=800,
        reasoning_tokens=150,
        cumulative_synthesis_tokens=450,
        dag_cost_usd=0.0042,
        cumulative_synthesis_cost=0.0018,
        cost_estimate=0.0060,
        models_used={"gemini-2.5-pro": 1550},
        execution_summary=ExecutionSummarySnapshot(
            strictness_level=85,
            is_ensemble_run=True,
            is_degraded=False,
            system_concurrency_snapshot={"max_concurrent_workflows": 5},
        ),
        metadata=ExecutionMetadata(
            matrix_sampling_strategy=5,
            workflow_version=2,
        ),
        duration_ms=2340,
        created_at=now_utc,
        updated_at=now_utc,
        completed_at=now_utc,
    )

    async with uow:
        assert await uow.entities.get_report_binary(report_id) is None
        await uow.entities.save_report_binary(binary_dto)
        fetched_binary = await uow.entities.get_report_binary(report_id)
        assert fetched_binary is not None
        assert fetched_binary.report_id == report_id
        assert fetched_binary.pdf_bytes == pdf_payload
        assert fetched_binary.size_bytes == len(pdf_payload)

        assert await uow.entities.get_execution(exec_id) is None
        saved_exec_id = await uow.entities.save_execution(execution_record)
        assert saved_exec_id == exec_id
        fetched_exec = await uow.entities.get_execution(exec_id)
        assert fetched_exec is not None
        assert fetched_exec.id == exec_id
        assert fetched_exec.workflow_id == wf_id
        assert fetched_exec.prompt_tokens == 1200
        assert fetched_exec.dag_cost_usd == pytest.approx(0.0042)
        assert fetched_exec.frozen_context is not None
        assert len(fetched_exec.frozen_context.mcp_tool_audit) == 1
        assert fetched_exec.frozen_context.mcp_tool_audit[0].namespaced_alias == "exa_gateway__web_search_exa"
        assert fetched_exec.metadata is not None
        assert fetched_exec.metadata.matrix_sampling_strategy == 5

    # Also test binary pydantic_core JSONB wire codec roundtrip with 0x01 version byte
    encoded_wire = encode_jsonb_binary({"lz4_toast": True, "tokens": [10, 20, 30]})
    assert encoded_wire[0] == 1
    decoded_wire = decode_jsonb_binary(encoded_wire)
    assert decoded_wire == {"lz4_toast": True, "tokens": [10, 20, 30]}
    assert decode_jsonb_binary(memoryview(encoded_wire)) == {"lz4_toast": True, "tokens": [10, 20, 30]}


# ============================================================================
# Positive Case 4: PostgreSQL 19 DDL Schema vs. Domain DTO Naming Parity
# ============================================================================


def test_schema_dto_naming_parity() -> None:
    """Assert 1:1 bi-directional column-to-field naming parity across all 22 tables and MCP JSONB structures."""
    sql_text = _MIGRATION_SQL_PATH.read_text(encoding="utf-8")
    assert "SET default_toast_compression = 'lz4';" in sql_text
    assert "CREATE STATISTICS IF NOT EXISTS stat_quorum_nodes_run_created" in sql_text
    assert "CREATE STATISTICS IF NOT EXISTS stat_quorum_edges_run_created" in sql_text

    parsed_tables = _extract_sql_table_columns(sql_text)
    expected_22_tables = {
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
        "step_criteria_blocks",
        "workflows",
        "workflow_step_refs",
        "output_profiles",
        "executions",
        "execution_payloads",
        "report_artifacts",
        "report_binaries",
        "quorum_nodes",
        "quorum_edges",
        "audit_logs",
        "usage_records",
    }
    assert set(parsed_tables.keys()) == expected_22_tables

    # 1. quorum_nodes <-> PropositionNode + NodeDraft.local_key
    assert parsed_tables["quorum_nodes"] == set(PropositionNode.model_fields.keys()) | {"local_key"}

    # 2. quorum_edges <-> DependencyEdge
    assert parsed_tables["quorum_edges"] == set(DependencyEdge.model_fields.keys())

    # 3. report_binaries <-> ReportBinaryPayloadDTO
    assert parsed_tables["report_binaries"] == set(ReportBinaryPayloadDTO.model_fields.keys())

    # 4. executions + execution_payloads <-> ExecutionRecord 1:1 hot/cold sidecar split
    sidecar_payload_fields = {
        "raw_inputs",
        "frozen_context",
        "context_variables",
        "execution_trace",
        "profile_syntheses",
    }
    assert parsed_tables["execution_payloads"] == sidecar_payload_fields | {"execution_id", "updated_at"}
    assert parsed_tables["executions"] == set(ExecutionRecord.model_fields.keys()) - sidecar_payload_fields

    # 5. report_artifacts <-> ReportArtifact + has_pdf sidecar flag
    assert parsed_tables["report_artifacts"] == set(ReportArtifact.model_fields.keys()) | {"has_pdf"}

    # 6. workflows <-> Workflow + VIRTUAL created_at
    assert parsed_tables["workflows"] == set(Workflow.model_fields.keys()) | {"created_at"}
    assert parsed_tables["workflow_step_refs"] == {"workflow_id", "step_id"}

    # 7. steps <-> Step (criteria_block_ids normalized into step_criteria_blocks) + VIRTUAL created_at
    assert parsed_tables["steps"] == (set(Step.model_fields.keys()) - {"criteria_block_ids"}) | {"created_at"}
    assert parsed_tables["step_criteria_blocks"] == {"step_id", "prompt_block_id", "position"}

    # 8. prompt_blocks <-> Polymorphic union of all concrete PromptBlock models + VIRTUAL created_at
    prompt_block_union_fields = (
        set(MatrixPromptBlock.model_fields.keys())
        | set(SystemRulePromptBlock.model_fields.keys())
        | set(PersonaPromptBlock.model_fields.keys())
        | set(ProtocolPromptBlock.model_fields.keys())
    )
    assert parsed_tables["prompt_blocks"] == prompt_block_union_fields | {"created_at"}

    # 9. output_profiles <-> OutputProfile + VIRTUAL created_at
    assert parsed_tables["output_profiles"] == set(OutputProfile.model_fields.keys()) | {"created_at"}

    # 10a. model_registries <-> SystemConfigModelRegistry + VIRTUAL created_at
    assert parsed_tables["model_registries"] == set(SystemConfigModelRegistry.model_fields.keys()) | {"created_at"}

    # 10b. mcp_gateways <-> SystemConfigMCPGateways + VIRTUAL created_at
    assert parsed_tables["mcp_gateways"] == set(SystemConfigMCPGateways.model_fields.keys()) | {"created_at"}

    # 11. users <-> User
    assert parsed_tables["users"] == set(User.model_fields.keys())

    # 12. organizations <-> Organization
    assert parsed_tables["organizations"] == set(Organization.model_fields.keys())

    # 13. invitations <-> Invitation
    assert parsed_tables["invitations"] == set(Invitation.model_fields.keys())

    # 14. tenant_secrets <-> TenantSecretDTO + mcp_gateway_id + VIRTUAL created_at
    assert parsed_tables["tenant_secrets"] == set(TenantSecretDTO.model_fields.keys()) | {
        "mcp_gateway_id",
        "created_at",
    }

    # 15. execution_assignments <-> ExecutionAssignment
    assert parsed_tables["execution_assignments"] == set(ExecutionAssignment.model_fields.keys())

    # 16. task_briefs <-> TaskBrief + VIRTUAL created_at
    assert parsed_tables["task_briefs"] == set(TaskBrief.model_fields.keys()) | {"created_at"}

    # 17. audit_logs <-> AuditLogRecord
    assert parsed_tables["audit_logs"] == set(AuditLogRecord.model_fields.keys())

    # 18. usage_records <-> UsageRecord (with canonical SQL column names mapped via AliasChoices)
    expected_usage_sql_columns = (
        set(UsageRecord.model_fields.keys()) - {"org_id", "model", "input_tokens", "output_tokens", "timestamp"}
    ) | {"organization_id", "model_name", "prompt_tokens", "completion_tokens", "created_at"}
    assert parsed_tables["usage_records"] == expected_usage_sql_columns

    # Verify lossless binary JSONB roundtrip of MCP schemas (AllowedMCPTool, MCPServerInfoDTO, Step.mcp_tool_params)
    server_info = MCPServerInfoDTO(
        name="exa-mcp-server",
        version="1.4.0",
        title="Exa Search Gateway",
        description="High-precision neural search gateway",
        website_url="https://exa.ai",
        icons=[MCPIconDTO(src="https://exa.ai/icon.png", mime_type="image/png", sizes=["64x64"])],
    )
    recovered_server_info = MCPServerInfoDTO.model_validate(
        decode_jsonb_binary(encode_jsonb_binary(server_info.model_dump(mode="json", exclude_none=True)))
    )
    assert recovered_server_info == server_info

    mcp_gateway = SystemConfigMCPGateways(
        id=generate_uuid7_opaque_id(EntityPrefix.MCP_GATEWAY),
        organization_id="org_0195f3a0000070008000000000000001",
        name="Exa Search Gateway",
        slug="exa_search",
        endpoint_url="https://mcp.exa.ai/v1",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.BEARER,
        auth_env_var="EXA_API_KEY",
        timeout_seconds=30,
        tools=[
            AllowedMCPTool(
                tool_id="web_search_exa",
                capability=ToolCapability.SEARCH,
                name=I18nText(translations={"fi": "Exa-verkkohaku", "en": "Exa Web Search"}),
                description="Perform neural web search.",
                input_schema=MCPToolInputSchemaDTO(
                    properties={
                        "query": MCPToolSchemaPropertyDTO(
                            type=JSONSchemaPropertyType.STRING,
                            description="Search query string.",
                        ),
                        "num_results": MCPToolSchemaPropertyDTO(
                            type=JSONSchemaPropertyType.INTEGER,
                            description="Max results.",
                            default=5,
                        ),
                    },
                    required=["query"],
                ),
                enabled=True,
                execution=MCPToolExecutionDTO(task_support="optional"),
            )
        ],
    )
    recovered_gateway = SystemConfigMCPGateways.model_validate(
        decode_jsonb_binary(encode_jsonb_binary(mcp_gateway.model_dump(mode="json", exclude_none=True)))
    )
    assert recovered_gateway == mcp_gateway

    step_model = Step(
        organization_id="org_0195f3a0000070008000000000000001",
        id=generate_uuid7_opaque_id(EntityPrefix.STEP),
        slug="step_mcp_research",
        name=I18nText(translations={"fi": "Tutkimusvaihe", "en": "Research Step"}),
        type=StepType.LLM,
        extraction_protocol_block_id=generate_uuid7_opaque_id(EntityPrefix.PROMPT_BLOCK),
        criteria_block_ids=[generate_uuid7_opaque_id(EntityPrefix.PROMPT_BLOCK)],
        pre_hooks=[],
        post_hooks=[],
        expected_inputs=[],
        allowed_mcp_tools=["exa_search__web_search_exa"],
        mcp_tool_params={"exa_search__web_search_exa": {"num_results": 10, "use_autoprompt": True}},
        cognitive_tier=CognitiveTier.DEEP,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
    )
    recovered_step = Step.model_validate(
        decode_jsonb_binary(encode_jsonb_binary(step_model.model_dump(mode="json", exclude_none=True)))
    )
    assert recovered_step.mcp_tool_params == {"exa_search__web_search_exa": {"num_results": 10, "use_autoprompt": True}}


# ============================================================================
# Negative Case 1: DAG Cycle Detection Fail-Fast
# ============================================================================


@pytest.mark.asyncio
async def test_dag_cycle_detection_fail_fast(uow: QuorumUnitOfWork) -> None:
    """Verify introducing a 3-node cycle (A -> B -> C -> A) triggers CycleDetectedError Fail-Fast."""
    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)

    node_drafts = (
        NodeDraft(
            local_key="node_a",
            node_type=PropositionNodeType.CLAIM,
            confidence=0.80,
            payload=PropositionPayloadDTO(statement="Proposition A", metadata={}),
        ),
        NodeDraft(
            local_key="node_b",
            node_type=PropositionNodeType.WARRANT,
            confidence=0.82,
            payload=PropositionPayloadDTO(statement="Proposition B", metadata={}),
        ),
        NodeDraft(
            local_key="node_c",
            node_type=PropositionNodeType.GROUND,
            confidence=0.85,
            payload=PropositionPayloadDTO(statement="Proposition C", metadata={}),
        ),
    )

    cyclic_edges = (
        EdgeDraft(
            source_key="node_a",
            target_key="node_b",
            relation_type=DependencyRelationType.CAUSES,
            causal_weight=0.7,
        ),
        EdgeDraft(
            source_key="node_b",
            target_key="node_c",
            relation_type=DependencyRelationType.CAUSES,
            causal_weight=0.7,
        ),
        EdgeDraft(
            source_key="node_c",
            target_key="node_a",
            relation_type=DependencyRelationType.CAUSES,
            causal_weight=0.7,
        ),
    )

    async with uow:
        materialized = await uow.graph.materialize_wave(run_id, node_drafts, cyclic_edges)
        assert len(materialized) == 3

        with pytest.raises(CycleDetectedError) as exc_info:
            await uow.graph.assert_acyclic(run_id)

        err = exc_info.value
        assert err.run_id == run_id
        assert err.error_code == ErrorCodes.VALIDATION_FAILED.value
        assert len(err.cycle_path) >= 3


# ============================================================================
# Negative Case 2: Transactional Rollback & Isolation
# ============================================================================


@pytest.mark.asyncio
async def test_transaction_rollback_and_isolation(uow: QuorumUnitOfWork) -> None:
    """Verify dangling EdgeDraft references, duplicate local_key, and mid-wave exceptions roll back cleanly."""
    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)

    valid_node = NodeDraft(
        local_key="valid_node",
        node_type=PropositionNodeType.GROUND,
        confidence=0.90,
        payload=PropositionPayloadDTO(statement="Valid isolated ground proposition.", metadata={}),
    )
    dangling_edge = EdgeDraft(
        source_key="valid_node",
        target_key="nonexistent_node",
        relation_type=DependencyRelationType.SUPPORTS,
        causal_weight=0.50,
    )

    # 1. Dangling edge target_key triggers AppException(VALIDATION_FAILED) and rolls back UoW
    with pytest.raises(AppException) as exc_dangling:
        async with uow:
            await uow.graph.materialize_wave(run_id, (valid_node,), (dangling_edge,))
    assert exc_dangling.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    async with uow:
        assert len(await uow.topology.fetch_next_kahn_wave(run_id)) == 0

    # 2. Duplicate local_key in wave triggers AppException(VALIDATION_FAILED)
    duplicate_node = NodeDraft(
        local_key="valid_node",
        node_type=PropositionNodeType.CLAIM,
        confidence=0.75,
        payload=PropositionPayloadDTO(statement="Duplicate local_key proposition.", metadata={}),
    )
    with pytest.raises(AppException) as exc_dup:
        async with uow:
            await uow.graph.materialize_wave(run_id, (valid_node, duplicate_node), ())
    assert exc_dup.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # 3. Mid-transaction exception after materialize_wave rolls back all persisted nodes
    with pytest.raises(RuntimeError, match="Simulated post-wave failure"):
        async with uow:
            inserted = await uow.graph.materialize_wave(run_id, (valid_node,), ())
            assert len(inserted) == 1
            raise RuntimeError("Simulated post-wave failure")

    async with uow:
        remaining = await uow.topology.fetch_next_kahn_wave(run_id)
        assert len(remaining) == 0


# ============================================================================
# Negative Case 3: ISTQB Boundary Value Analysis & Pool/Adapter Faults
# ============================================================================


@pytest.mark.asyncio
async def test_istqb_boundary_value_and_wire_header_failures(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify ISTQB boundaries on Draft models, PrefixedUUID7, JSONB wire headers, and Pool/UoW fault paths."""
    # 1. NodeDraft confidence boundaries: min - 0.001 (-0.001) and max + 0.001 (1.001)
    with pytest.raises(ValidationError):
        NodeDraft(
            local_key="bva_low",
            node_type=PropositionNodeType.CLAIM,
            confidence=-0.001,
            payload=PropositionPayloadDTO(statement="Below minimum confidence.", metadata={}),
        )
    with pytest.raises(ValidationError):
        NodeDraft(
            local_key="bva_high",
            node_type=PropositionNodeType.CLAIM,
            confidence=1.001,
            payload=PropositionPayloadDTO(statement="Above maximum confidence.", metadata={}),
        )

    # 2. EdgeDraft causal_weight boundaries (-1.001, 1.001) and self-loop (source_key == target_key)
    with pytest.raises(ValidationError):
        EdgeDraft(
            source_key="n1",
            target_key="n2",
            relation_type=DependencyRelationType.CAUSES,
            causal_weight=-1.001,
        )
    with pytest.raises(ValidationError):
        EdgeDraft(
            source_key="n1",
            target_key="n2",
            relation_type=DependencyRelationType.CAUSES,
            causal_weight=1.001,
        )
    with pytest.raises(ValidationError):
        EdgeDraft(
            source_key="same_key",
            target_key="same_key",
            relation_type=DependencyRelationType.SUPPORTS,
            causal_weight=0.5,
        )

    # 3. parse_prefixed_uuid7 wrong prefix and UUIDv4 rejection
    valid_nod_id = generate_uuid7_opaque_id(EntityPrefix.NODE)
    with pytest.raises(AppException) as exc_prefix:
        parse_prefixed_uuid7(valid_nod_id, EntityPrefix.WORKFLOW)
    assert exc_prefix.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    uuid4_nod = f"nod_{uuid.uuid4().hex}"
    with pytest.raises(AppException) as exc_v4:
        parse_prefixed_uuid7(uuid4_nod, EntityPrefix.NODE)
    assert exc_v4.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # 4. Binary JSONB codec invalid header (0x02), empty buffer (b""), malformed JSON, and unserializable object
    with pytest.raises(AppException) as exc_empty_wire:
        decode_jsonb_binary(b"")
    assert exc_empty_wire.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

    with pytest.raises(AppException) as exc_ver_wire:
        decode_jsonb_binary(b"\x02{}")
    assert exc_ver_wire.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

    with pytest.raises(AppException) as exc_bad_json:
        decode_jsonb_binary(b"\x01{invalid_json")
    assert exc_bad_json.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

    with pytest.raises(AppException) as exc_encode_fail:
        encode_jsonb_binary(object())
    assert exc_encode_fail.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

    # 5. PostgresPoolManager DSN resolution, migrations, close, and fault isolation
    pool = InMemoryAsyncPgPool()
    settings_with_pw = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="pg.quorum.local",
        postgres_port=5432,
        postgres_user="quorum_user",
        postgres_password="env_injected_secret_value",
        postgres_db="quorum_db",
        postgres_command_timeout_seconds=10.0,
    )
    manager_pw = PostgresPoolManager(settings=settings_with_pw, pool=pool)
    assert "quorum_user:env_injected_secret_value@pg.quorum.local:5432/quorum_db" in manager_pw.resolve_dsn()

    settings_no_pw = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="pg.quorum.local",
        postgres_port=5432,
        postgres_user="quorum_user",
        postgres_password=None,
        postgres_db="quorum_db",
        postgres_command_timeout_seconds=10.0,
    )
    manager_no_pw = PostgresPoolManager(settings=settings_no_pw, pool=pool)
    assert manager_no_pw.resolve_dsn() == "postgresql://quorum_user@pg.quorum.local:5432/quorum_db"

    settings_dsn = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_dsn="postgresql://override_host:5432/custom_db",
    )
    manager_dsn = PostgresPoolManager(settings=settings_dsn, pool=pool)
    assert manager_dsn.resolve_dsn() == "postgresql://override_host:5432/custom_db"

    await manager_pw.apply_migrations()
    assert pool.store.migrations_applied == 1

    # Missing migration file raises AppException(STORAGE_ACCESS_FAILED)
    missing_mgr = PostgresPoolManager(
        settings=settings_with_pw,
        pool=pool,
        migration_sql_path=tmp_path / "missing_schema.sql",
    )
    with pytest.raises(AppException) as exc_missing_sql:
        await missing_mgr.apply_migrations()
    assert exc_missing_sql.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

    # Fault injection on pool operations with strict try...finally cleanup
    pre_existing_app_err = AppException(
        message="Pre-existing AppException passthrough",
        status_code=500,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )
    try:
        pool.inject_fault("acquire", OSError("pool exhausted"))
        with pytest.raises(AppException) as exc_acq:
            async with manager_pw.acquire_connection():
                pass
        assert exc_acq.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("acquire", pre_existing_app_err)
        with pytest.raises(AppException) as exc_acq_direct:
            async with manager_pw.acquire_connection():
                pass
        assert exc_acq_direct.value is pre_existing_app_err
    finally:
        pool.clear_faults()

    try:
        pool.inject_fault("set_type_codec", RuntimeError("codec registration rejected"))
        with pytest.raises(AppException) as exc_codec:
            async with manager_pw.acquire_connection():
                pass
        assert exc_codec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("set_type_codec", pre_existing_app_err)
        with pytest.raises(AppException) as exc_codec_direct:
            async with manager_pw.acquire_connection():
                pass
        assert exc_codec_direct.value is pre_existing_app_err
    finally:
        pool.clear_faults()

    try:
        pool.inject_fault("execute", RuntimeError("DDL execution error"))
        with pytest.raises(AppException) as exc_ddl:
            await manager_pw.apply_migrations()
        assert exc_ddl.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("execute", pre_existing_app_err)
        with pytest.raises(AppException) as exc_ddl_direct:
            await manager_pw.apply_migrations()
        assert exc_ddl_direct.value is pre_existing_app_err
    finally:
        pool.clear_faults()

    # PostgresUnitOfWork commit/rollback outside active transaction raises AppException
    pg_uow = PostgresUnitOfWork(pool_manager=manager_pw)
    with pytest.raises(AppException) as exc_no_tx_commit:
        await pg_uow.commit()
    assert exc_no_tx_commit.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

    with pytest.raises(AppException) as exc_no_tx_rollback:
        await pg_uow.rollback()
    assert exc_no_tx_rollback.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

    # Fault during UoW acquire, init_connection, transaction start, commit, and rollback
    try:
        pool.inject_fault("acquire", RuntimeError("uow acquire failed"))
        with pytest.raises(AppException) as exc_uow_acq:
            async with PostgresUnitOfWork(pool_manager=manager_pw):
                pass
        assert exc_uow_acq.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("acquire", pre_existing_app_err)
        with pytest.raises(AppException) as exc_uow_acq_direct:
            async with PostgresUnitOfWork(pool_manager=manager_pw):
                pass
        assert exc_uow_acq_direct.value is pre_existing_app_err
    finally:
        pool.clear_faults()

    try:
        pool.inject_fault("set_type_codec", RuntimeError("uow codec failed"))
        with pytest.raises(AppException) as exc_uow_codec:
            async with PostgresUnitOfWork(pool_manager=manager_pw):
                pass
        assert exc_uow_codec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()

    try:
        pool.inject_fault("transaction", RuntimeError("repeatable_read unavailable"))
        with pytest.raises(AppException) as exc_tx_start:
            async with PostgresUnitOfWork(pool_manager=manager_pw):
                pass
        assert exc_tx_start.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()

    # Idempotent commit() and rollback() inside active UoW
    async with PostgresUnitOfWork(pool_manager=manager_pw) as idem_commit_uow:
        await idem_commit_uow.commit()
        await idem_commit_uow.commit()

    async with PostgresUnitOfWork(pool_manager=manager_pw) as idem_rb_uow:
        await idem_rb_uow.rollback()
        await idem_rb_uow.rollback()

    try:
        pool.inject_fault("tx_commit", RuntimeError("commit serialization error"))
        with pytest.raises(AppException) as exc_tx_commit:
            async with PostgresUnitOfWork(pool_manager=manager_pw):
                pass
        assert exc_tx_commit.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("tx_commit", pre_existing_app_err)
        with pytest.raises(AppException) as exc_tx_commit_direct:
            async with PostgresUnitOfWork(pool_manager=manager_pw):
                pass
        assert exc_tx_commit_direct.value is pre_existing_app_err
    finally:
        pool.clear_faults()

    try:
        pool.inject_fault("tx_rollback", RuntimeError("rollback transport error"))
        with pytest.raises(AppException) as exc_tx_rb:
            async with PostgresUnitOfWork(pool_manager=manager_pw) as rb_uow:
                await rb_uow.rollback()
        assert exc_tx_rb.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("tx_rollback", pre_existing_app_err)
        with pytest.raises(AppException) as exc_tx_rb_direct:
            async with PostgresUnitOfWork(pool_manager=manager_pw) as rb_uow_direct:
                await rb_uow_direct.rollback()
        assert exc_tx_rb_direct.value is pre_existing_app_err
    finally:
        pool.clear_faults()

    # ReportBinaryPayloadDTO size mismatch raises AppException(VALIDATION_FAILED)
    bad_binary = ReportBinaryPayloadDTO(
        report_id=generate_uuid7_opaque_id(EntityPrefix.REPORT),
        pdf_bytes=b"12345",
        size_bytes=999,
        created_at=datetime.now(UTC),
    )
    async with PostgresUnitOfWork(pool_manager=manager_pw) as active_uow:
        with pytest.raises(AppException) as exc_size:
            await active_uow.entities.save_report_binary(bad_binary)
        assert exc_size.value.error_code == ErrorCodes.VALIDATION_FAILED.value

        # Invalid min_confidence in find_falsified_claims raises AppException(VALIDATION_FAILED)
        run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
        with pytest.raises(AppException) as exc_conf:
            await active_uow.reasoning.find_falsified_claims(run_id, min_confidence=1.5)
        assert exc_conf.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # Pool close and fault handling
    try:
        pool.inject_fault("close", RuntimeError("socket close failed"))
        with pytest.raises(AppException) as exc_close:
            await manager_pw.close()
        assert exc_close.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

        manager_close_direct = PostgresPoolManager(settings=settings_with_pw, pool=pool)
        pool.inject_fault("close", pre_existing_app_err)
        with pytest.raises(AppException) as exc_close_direct:
            await manager_close_direct.close()
        assert exc_close_direct.value is pre_existing_app_err
    finally:
        pool.clear_faults()

    manager_close_ok = PostgresPoolManager(settings=settings_with_pw, pool=pool)
    await manager_close_ok.close()
    assert pool.closed is True
    # Calling close() again when pool is already None is a safe no-op
    await manager_close_ok.close()

    # Lazy asyncpg import path when pool is None: module-scoped monkeypatch
    class _FakeAsyncPgDriverModule(types.ModuleType):
        async def create_pool(
            self,
            dsn: str,
            *,
            min_size: int,
            max_size: int,
            command_timeout: float,
            timeout: float,
            init: Callable[[AsyncPgConnectionProtocol], object],
        ) -> AsyncPgPoolProtocol:
            _ = (dsn, min_size, max_size, command_timeout, timeout, init)
            return InMemoryAsyncPgPool()

    monkeypatch.setitem(
        sys.modules,
        "asyncpg",
        _FakeAsyncPgDriverModule("asyncpg"),
    )
    lazy_mgr = PostgresPoolManager(settings=settings_dsn, pool=None)
    connected_pool = await lazy_mgr.connect()
    assert isinstance(connected_pool, InMemoryAsyncPgPool)
    # Second connect() call returns cached self._pool
    assert await lazy_mgr.connect() is connected_pool

    # Invalid module returned by _import_asyncpg_module raises AppException(STORAGE_ACCESS_FAILED)
    monkeypatch.setattr(
        "backend_v2.database.postgres.pool._import_asyncpg_module",
        lambda: object(),
    )
    bad_driver_mgr = PostgresPoolManager(settings=settings_dsn, pool=None)
    with pytest.raises(AppException) as exc_bad_mod:
        await bad_driver_mgr.connect()
    assert exc_bad_mod.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

    # Missing asyncpg driver raises AppException(STORAGE_ACCESS_FAILED)
    def _raise_import_error() -> object:
        raise ModuleNotFoundError("No module named 'asyncpg'")

    monkeypatch.setattr(
        "backend_v2.database.postgres.pool._import_asyncpg_module",
        _raise_import_error,
    )
    missing_driver_mgr = PostgresPoolManager(settings=settings_dsn, pool=None)
    with pytest.raises(AppException) as exc_missing_driver:
        await missing_driver_mgr.connect()
    assert exc_missing_driver.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value


@pytest.mark.asyncio
async def test_adapter_database_driver_fault_translation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify PostgresGraphAdapter, CteReasoningStrategy, and PostgresEntityAdapter translate driver errors."""
    pool = InMemoryAsyncPgPool()
    settings = Settings(storage_backend=StorageBackend.POSTGRES, postgres_command_timeout_seconds=22.5)
    monkeypatch.setattr(
        "backend_v2.database.postgres.graph_adapter.get_settings",
        lambda: settings,
        raising=False,
    )
    monkeypatch.setattr(
        "backend_v2.database.postgres.entity_adapter.get_settings",
        lambda: settings,
        raising=False,
    )
    manager = PostgresPoolManager(settings=settings, pool=pool)
    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    node_id_1 = generate_uuid7_opaque_id(EntityPrefix.NODE)
    node_id_2 = generate_uuid7_opaque_id(EntityPrefix.NODE)
    edge_id = generate_uuid7_opaque_id(EntityPrefix.EDGE)
    report_id = generate_uuid7_opaque_id(EntityPrefix.REPORT)
    now_utc = datetime.now(UTC)

    # Verify column coercion and graph adapter helpers
    assert _graph_coerce_uuid_or_str(12345) == "12345"
    sample_payload = PropositionPayloadDTO(statement="Already hydrated", metadata={})
    assert _hydrate_payload_dto(sample_payload) is sample_payload
    assert _hydrate_payload_dto(b'{"statement": "From bytes", "metadata": {}}').statement == "From bytes"
    assert _hydrate_payload_dto(memoryview(b'{"statement": "From memoryview", "metadata": {}}')).statement == (
        "From memoryview"
    )
    assert _hydrate_payload_dto({"statement": "From mapping", "metadata": {}}).statement == "From mapping"
    assert _extract_cycle_node_ids("not_a_sequence") == ()
    raw_u1 = parse_prefixed_uuid7(node_id_1, EntityPrefix.NODE)
    raw_u2 = parse_prefixed_uuid7(node_id_2, EntityPrefix.NODE)
    assert _extract_cycle_node_ids([[raw_u1, raw_u2]]) == (node_id_1, node_id_2)

    async with manager.acquire_connection() as default_conn:
        default_graph = PostgresGraphAdapter(connection=default_conn)
        default_reasoning = CteReasoningStrategy(connection=default_conn)
        default_entities = PostgresEntityAdapter(connection=default_conn)
        assert default_graph.command_timeout_seconds == 22.5
        assert default_reasoning.command_timeout_seconds == 22.5
        assert default_entities.command_timeout_seconds == 22.5

    # Verify calling UoW ports outside 'async with uow:' fails fast with STORAGE_ACCESS_FAILED
    unbound_uow = PostgresUnitOfWork(pool_manager=manager)
    assert isinstance(unbound_uow, QuorumUnitOfWork)
    with pytest.raises(AppException) as exc_unbound_fetch:
        await unbound_uow.topology.fetch_next_kahn_wave(run_id)
    assert exc_unbound_fetch.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    with pytest.raises(AppException) as exc_unbound_row:
        await unbound_uow.entities.get_report_binary(report_id)
    assert exc_unbound_row.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    with pytest.raises(AppException) as exc_unbound_exec:
        await unbound_uow.entities.save_report_binary(
            ReportBinaryPayloadDTO(
                report_id=report_id,
                pdf_bytes=b"PDF",
                size_bytes=3,
                created_at=now_utc,
            )
        )
    assert exc_unbound_exec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    with pytest.raises(AppException) as exc_unbound_many:
        await unbound_uow.graph.upsert_wave_batch(
            (
                PropositionNode(
                    node_id=node_id_1,
                    run_id=run_id,
                    node_type=PropositionNodeType.CLAIM,
                    confidence=0.8,
                    payload=PropositionPayloadDTO(statement="Statement", metadata={}),
                    created_at=now_utc,
                ),
            ),
            (),
        )
    assert exc_unbound_many.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    with pytest.raises(AppException) as exc_unbound_save_exec:
        await unbound_uow.entities.save_execution(
            ExecutionRecord(
                id=run_id,
                organization_id=generate_uuid7_opaque_id(EntityPrefix.ORGANIZATION),
                workflow_id=generate_uuid7_opaque_id(EntityPrefix.WORKFLOW),
                target_locale="en",
                execution_trace=[],
                context_variables=ContextVariablesDTO(variables={}),
                raw_inputs=WorkflowInputs(dynamic_inputs={}),
                frozen_context=None,
                steps=[],
                profile_syntheses={},
                source_identity_manifest={},
                models_used={},
                created_at=now_utc,
                updated_at=now_utc,
            )
        )
    assert exc_unbound_save_exec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    with pytest.raises(AppException) as exc_unbound_get_exec:
        await unbound_uow.entities.get_execution(run_id)
    assert exc_unbound_get_exec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    assert isinstance(unbound_uow.graph, PostgresGraphAdapter)
    with pytest.raises(AppException) as exc_unbound_codec:
        await init_connection(unbound_uow.graph._conn)
    assert exc_unbound_codec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    with pytest.raises(AppException) as exc_unbound_tx:
        unbound_uow.graph._conn.transaction(isolation="repeatable_read")
    assert exc_unbound_tx.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

    # Verify column coercion helpers handle non-UUID/str, memoryview, already-decoded objects, and str floats
    assert _coerce_uuid_or_str(12345) == "12345"
    assert _decode_jsonb_column(memoryview(b'{"k": 1}')) == {"k": 1}
    assert _decode_jsonb_column([1, 2, 3]) == [1, 2, 3]
    assert _coerce_float("0.0042") == pytest.approx(0.0042)

    async with manager.acquire_connection() as conn:
        graph = PostgresGraphAdapter(connection=conn, command_timeout_seconds=5.0)
        entities = PostgresEntityAdapter(connection=conn, command_timeout_seconds=5.0)
        reasoning = CteReasoningStrategy(connection=conn, command_timeout_seconds=5.0)

        draft = NodeDraft(
            local_key="k1",
            node_type=PropositionNodeType.CLAIM,
            confidence=0.8,
            payload=PropositionPayloadDTO(statement="Statement", metadata={}),
        )
        node_model = PropositionNode(
            node_id=node_id_1,
            run_id=run_id,
            node_type=PropositionNodeType.CLAIM,
            confidence=0.8,
            payload=PropositionPayloadDTO(statement="Statement", metadata={}),
            created_at=now_utc,
        )
        edge_model = DependencyEdge(
            edge_id=edge_id,
            run_id=run_id,
            source_id=node_id_1,
            target_id=node_id_2,
            relation_type=DependencyRelationType.SUPPORTS,
            causal_weight=0.5,
            created_at=now_utc,
        )
        report_dto = ReportBinaryPayloadDTO(
            report_id=report_id,
            pdf_bytes=b"PDF",
            size_bytes=3,
            created_at=now_utc,
        )
        exec_record = ExecutionRecord(
            id=run_id,
            organization_id=generate_uuid7_opaque_id(EntityPrefix.ORGANIZATION),
            workflow_id=generate_uuid7_opaque_id(EntityPrefix.WORKFLOW),
            target_locale="en",
            execution_trace=[],
            context_variables=ContextVariablesDTO(variables={}),
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
            frozen_context=None,
            steps=[],
            profile_syntheses={},
            source_identity_manifest={},
            models_used={},
            created_at=now_utc,
            updated_at=now_utc,
        )

        try:
            pool.inject_fault("fetch", RuntimeError("connection reset during fetch"))
            with pytest.raises(AppException) as exc_mat:
                await graph.materialize_wave(run_id, (draft,), ())
            assert exc_mat.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            with pytest.raises(AppException) as exc_kahn:
                await graph.fetch_next_kahn_wave(run_id)
            assert exc_kahn.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            with pytest.raises(AppException) as exc_fals:
                await reasoning.find_falsified_claims(run_id, min_confidence=0.7)
            assert exc_fals.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            # Verify pre-existing AppException from driver is re-raised directly without re-wrapping
            app_err = AppException(
                message="Direct AppException from connection",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            pool.inject_fault("fetch", app_err)
            with pytest.raises(AppException) as exc_direct_fetch:
                await graph.materialize_wave(run_id, (draft,), ())
            assert exc_direct_fetch.value is app_err

            with pytest.raises(AppException) as exc_direct_fals:
                await reasoning.find_falsified_claims(run_id, min_confidence=0.7)
            assert exc_direct_fals.value is app_err
        finally:
            pool.clear_faults()

        try:
            pool.inject_fault("executemany", RuntimeError("batch write failed"))
            with pytest.raises(AppException) as exc_upsert:
                await graph.upsert_wave_batch((node_model,), (edge_model,))
            assert exc_upsert.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
        finally:
            pool.clear_faults()

        try:
            pool.inject_fault("fetchrow", RuntimeError("fetchrow timeout"))
            with pytest.raises(AppException) as exc_acyclic:
                await graph.assert_acyclic(run_id)
            assert exc_acyclic.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            app_row_err = AppException(
                message="Direct AppException from fetchrow",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            pool.inject_fault("fetchrow", app_row_err)
            with pytest.raises(AppException) as exc_direct_acyclic:
                await graph.assert_acyclic(run_id)
            assert exc_direct_acyclic.value is app_row_err

            pool.inject_fault("fetchrow", RuntimeError("fetchrow timeout"))

            with pytest.raises(AppException) as exc_get_bin:
                await entities.get_report_binary(report_id)
            assert exc_get_bin.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            with pytest.raises(AppException) as exc_get_exec:
                await entities.get_execution(run_id)
            assert exc_get_exec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            with pytest.raises(AppException) as exc_verify_counts:
                await entities.verify_seed_table_counts({"organizations": 0})
            assert exc_verify_counts.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            pool.inject_fault("fetchrow", app_row_err)
            with pytest.raises(AppException) as exc_verify_counts_direct:
                await entities.verify_seed_table_counts({"organizations": 0})
            assert exc_verify_counts_direct.value is app_row_err
        finally:
            pool.clear_faults()

        try:
            pool.inject_fault("execute", RuntimeError("command execute failed"))
            with pytest.raises(AppException) as exc_save_bin:
                await entities.save_report_binary(report_dto)
            assert exc_save_bin.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            with pytest.raises(AppException) as exc_save_exec:
                await entities.save_execution(exec_record)
            assert exc_save_exec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            org_model = Organization(
                id="org_0195f3a0000070008000111111111111",
                slug="fault-org",
                name="Fault Org",
                is_active=True,
                tier="enterprise",
                subscription_status=SubscriptionStatus.ACTIVE,
                quota_limit=500.0,
                tpm_limit=100000,
                rpm_limit=1000,
                allowed_email_domains=[],
            )
            with pytest.raises(AppException) as exc_upsert_org:
                await entities.upsert_organization(org_model)
            assert exc_upsert_org.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

            app_exec_err = AppException(
                message="Direct AppException from execute",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            pool.inject_fault("execute", app_exec_err)
            with pytest.raises(AppException) as exc_upsert_org_direct:
                await entities.upsert_organization(org_model)
            assert exc_upsert_org_direct.value is app_exec_err
        finally:
            pool.clear_faults()

    # Verify InMemoryAsyncPgRecord membership check
    rec = InMemoryAsyncPgRecord({"node_id": "nod_123"})
    assert "node_id" in rec
    assert 42 not in rec


# ============================================================================
# Negative Case 4: Zero-ORM AST Guardrail & Codebase Verification
# ============================================================================


def test_zero_orm_ast_guardrail_verification(tmp_path: Path) -> None:
    """Verify audit_zero_orm_strictness.py passes on real codebase and catches ZORM001-ZORM006 violations."""
    repo_root = Path(__file__).resolve().parents[4]
    real_report = run_zero_orm_audit(
        [
            repo_root / "backend_v2" / "database" / "postgres",
            repo_root / "backend_v2" / "models" / "domain" / "proposition_graph.py",
            repo_root / "backend_v2" / "database" / "migrations" / "001_pg19_uuidv7_schema.sql",
        ]
    )
    assert real_report.is_clean
    assert len(real_report.findings) == 0

    # Synthetic negative verification for ZORM001, ZORM002, ZORM003, ZORM005, ZORM006
    untyped_dict_annotation = "dict" + "[str, Any]"
    bad_adapter_file = tmp_path / "graph_adapter.py"
    bad_adapter_file.write_text(
        "import sqlalchemy\n"
        "import orjson\n"
        "from typing import Any\n\n"
        f"def bad_fn(row: {untyped_dict_annotation}, llm_client: object) -> None:\n"
        "    try:\n"
        "        _ = dict(row)\n"
        "        _ = row['unapproved_drift_column']\n"
        "        llm_client.execute_structured_task()\n"
        "    except Exception:\n"
        "        pass\n",
        encoding="utf-8",
    )
    py_findings = audit_python_file(bad_adapter_file)
    rule_codes = {f.rule_code for f in py_findings}
    assert ZeroOrmRuleCode.ZORM001 in rule_codes
    assert ZeroOrmRuleCode.ZORM002 in rule_codes
    assert ZeroOrmRuleCode.ZORM003 in rule_codes
    assert ZeroOrmRuleCode.ZORM005 in rule_codes
    assert ZeroOrmRuleCode.ZORM006 in rule_codes

    # Synthetic negative verification for ZORM004 (rogue SQL table and banned TEXT PRIMARY KEY)
    bad_sql_file = tmp_path / "rogue_schema.sql"
    bad_sql_file.write_text(
        "CREATE TABLE IF NOT EXISTS rogue_shadow_table (id UUID PRIMARY KEY);\n"
        "CREATE TABLE IF NOT EXISTS workflows (\n"
        "    id TEXT PRIMARY KEY\n"
        ");\n",
        encoding="utf-8",
    )
    sql_findings = audit_sql_migration_file(bad_sql_file)
    assert len(sql_findings) == 2
    assert all(f.rule_code == ZeroOrmRuleCode.ZORM004 for f in sql_findings)


@pytest.mark.asyncio
async def test_postgres_uow_crud_and_occ_boundary_invariants() -> None:
    """Verify create_unit_of_work, PostgresUnitOfWork entity CRUD roundtrips, OCC conflict, and negative boundaries."""
    from backend_v2.database.factory import create_unit_of_work
    from backend_v2.models.dtos.trace import ExecutionUpdateDTO
    from backend_v2.tests.factories.model_factories import ExecutionRecordFactory

    pool = InMemoryAsyncPgPool()
    settings = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="db.internal",
        postgres_port=5432,
        postgres_user="quorum",
        postgres_db="quorum",
        postgres_command_timeout_seconds=12.0,
    )
    pool_manager = PostgresPoolManager(settings=settings, pool=pool)
    factory_uow = create_unit_of_work(settings=settings, pool_manager=pool_manager)
    assert isinstance(factory_uow, QuorumUnitOfWork)

    org_id_val = "org_0195f3a0000070008000111111111111"
    org = Organization(
        id=org_id_val,
        slug="alpha-org",
        name="Alpha Org",
        is_active=True,
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=100000,
        rpm_limit=1000,
        allowed_email_domains=[],
    )
    async with create_unit_of_work(settings=settings, pool_manager=pool_manager) as uow:
        assert await uow.entities.upsert_organization(org) == org_id_val
        fetched = await uow.entities.get_organization(org_id_val)
        assert fetched is not None
        assert fetched.name == "Alpha Org"
        assert await uow.entities.delete_organization(org_id_val) is True
        assert await uow.entities.delete_organization(org_id_val) is False

        with pytest.raises(AppException) as exc_bad_id:
            await uow.entities.get_organization("   ")
        assert exc_bad_id.value.error_code == ErrorCodes.VALIDATION_FAILED.value

        exec_rec = ExecutionRecordFactory.build(
            id="exe_0195f3a0000070008000111111111111",
            workflow_id="wf_0195f3a0000070008000111111111111",
            state_version=1,
        )
        await uow.entities.save_execution(exec_rec)
        assert await uow.entities.update_execution_occ(
            exec_rec.id,
            ExecutionUpdateDTO(expected_state_version=1, current_step="Wave 1 done"),
        )
        updated_exec = await uow.entities.get_execution(exec_rec.id)
        assert updated_exec is not None
        assert updated_exec.state_version == 2

        with pytest.raises(AppException) as exc_occ:
            await uow.entities.update_execution_occ(
                exec_rec.id,
                ExecutionUpdateDTO(expected_state_version=1, current_step="Stale write"),
            )
        assert exc_occ.value.error_code == ErrorCodes.CONFLICT.value


@pytest.mark.asyncio
async def test_seed_collection_batch_and_verify_counts_invariants(uow: QuorumUnitOfWork) -> None:
    """Verify seed_collection_batch, collection helpers, and verify_seed_table_counts across all tables."""
    from backend_v2.models.dtos.report_artifact import ReportMetadataDTO, ReportStoragePathsDTO
    from backend_v2.models.enums import PromptBlockCategory, ReportStatus
    from backend_v2.tests.factories.model_factories import (
        MatrixPromptBlockFactory,
        OutputProfileFactory,
        SystemConfigMCPGatewaysFactory,
        SystemConfigModelRegistryFactory,
        SystemRulePromptBlockFactory,
        TaskBriefFactory,
        WorkflowFactory,
    )

    now = datetime.now(UTC)
    org_sample = Organization(
        id="org_0195f3a0000070008000000000000001",
        slug="quorum-root",
        name="Quorum Root",
        is_active=True,
        tier="enterprise",
        contact_email="admin@quorum.ai",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=1000.0,
        tpm_limit=100000,
        rpm_limit=1000,
        allowed_email_domains=[],
        created_at=now,
    )
    user_sample = User(
        id="usr_0195f3a00000700a83fd6b3d77c748f4",
        organization_id=org_sample.id,
        email="admin@quorum.ai",
        name="Root Admin",
        role=UserRole.ROOT,
        is_active=True,
        language=SystemLocale.FI,
        theme_mode="dark",
        created_at=now,
    )
    reg_sample = SystemConfigModelRegistryFactory.build(
        id=generate_uuid7_opaque_id(EntityPrefix.MODEL_REGISTRY),
    )
    gw_sample = SystemConfigMCPGatewaysFactory.build(
        id=generate_uuid7_opaque_id(EntityPrefix.MCP_GATEWAY),
        organization_id=org_sample.id,
    )
    block_matrix = MatrixPromptBlockFactory.build(
        id=generate_uuid7_opaque_id(EntityPrefix.PROMPT_BLOCK),
        organization_id=org_sample.id,
    )
    block_persona = PersonaPromptBlock(
        id=generate_uuid7_opaque_id(EntityPrefix.PROMPT_BLOCK),
        organization_id=org_sample.id,
        slug="test_persona_block",
        label=I18nText(translations={"fi": "Persoona", "en": "Persona"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        output_extensions=[],
        role_enforcement="Act as an executive analyst.",
        tone_directives=[],
    )
    block_protocol = ProtocolPromptBlock(
        id=generate_uuid7_opaque_id(EntityPrefix.PROMPT_BLOCK),
        organization_id=org_sample.id,
        slug="test_protocol_block",
        label=I18nText(translations={"fi": "Protokolla", "en": "Protocol"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        category_id=PromptBlockCategory.PROTOCOL,
        output_extensions=[],
        protocol_instructions="Execute structured verification.",
    )
    block_rule = SystemRulePromptBlockFactory.build(
        id=generate_uuid7_opaque_id(EntityPrefix.PROMPT_BLOCK),
        organization_id=org_sample.id,
    )
    sample_blocks = [block_matrix, block_persona, block_protocol, block_rule]
    brief_sample = TaskBriefFactory.build(
        id=generate_uuid7_opaque_id(EntityPrefix.TASK_BRIEF),
        organization_id=org_sample.id,
    )
    step_sample = Step(
        id=generate_uuid7_opaque_id(EntityPrefix.STEP),
        organization_id=org_sample.id,
        slug="test_step_blueprint",
        name=I18nText(translations={"fi": "Vaihe", "en": "Step"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        type=StepType.LLM,
        zone=StepZone.ZONE_B,
        engine_type=EngineType.PROMPT,
        cognitive_tier=CognitiveTier.FAST,
        role_block_id=block_rule.id,
        extraction_protocol_block_id=block_protocol.id,
        execution_persona_block_id=block_persona.id,
        criteria_block_ids=[block_matrix.id],
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        expected_inputs=[],
    )
    wf_sample = WorkflowFactory.build(
        id=generate_uuid7_opaque_id(EntityPrefix.WORKFLOW),
        organization_id=org_sample.id,
        model_registry_id=reg_sample.id,
        mcp_gateway_id=gw_sample.id,
        steps=[],
    )
    profile_sample = OutputProfileFactory.build(
        id=generate_uuid7_opaque_id(EntityPrefix.OUTPUT_PROFILE),
        organization_id=org_sample.id,
        workflow_id=wf_sample.id,
    )

    sample_exec = ExecutionRecord(
        id=generate_uuid7_opaque_id(EntityPrefix.EXECUTION),
        organization_id=org_sample.id,
        workflow_id=wf_sample.id,
        workflow_version=2,
        output_profile_id=profile_sample.id,
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        progress=100,
        status_message="Completed",
        execution_trace=[],
        context_variables=ContextVariablesDTO(variables={}),
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        frozen_context=None,
        steps=[],
        profile_syntheses={},
        source_identity_manifest={},
        models_used={},
        created_at=now,
        updated_at=now,
        completed_at=now,
    )
    sample_report = ReportArtifact(
        id=generate_uuid7_opaque_id(EntityPrefix.REPORT),
        execution_id=sample_exec.id,
        workflow_id=sample_exec.workflow_id,
        profile_id=profile_sample.id,
        locale="fi",
        title="Sample Report",
        status=ReportStatus.READY,
        storage_paths=ReportStoragePathsDTO(pdf_path=f"{sample_exec.id}/reports/report.pdf"),
        metadata=ReportMetadataDTO(cost_usd=0.01),
        created_at=now,
        updated_at=now,
    )
    sample_binary = ReportBinaryPayloadDTO(
        report_id=sample_report.id,
        mime_type="application/pdf",
        pdf_bytes=b"%PDF-1.7 sample",
        size_bytes=len(b"%PDF-1.7 sample"),
        created_at=now,
    )

    async with uow:
        assert await uow.entities.seed_collection_batch("organizations", [org_sample]) == 1
        assert await uow.entities.seed_collection_batch("users", [user_sample]) == 1
        assert await uow.entities.seed_collection_batch("model_registries", [reg_sample]) == 1
        assert await uow.entities.seed_collection_batch("mcp_gateways", [gw_sample]) == 1
        assert await uow.entities.seed_collection_batch("prompt_blocks", sample_blocks) == 4
        assert await uow.entities.seed_collection_batch("task_briefs", [brief_sample]) == 1
        assert await uow.entities.seed_collection_batch("steps", [step_sample]) == 1
        assert await uow.entities.seed_collection_batch("workflows", [wf_sample]) == 1
        assert await uow.entities.seed_collection_batch("output_profiles", [profile_sample]) == 1
        assert await uow.entities.seed_collection_batch("executions", [sample_exec]) == 1
        assert await uow.entities.seed_collection_batch("report_artifacts", [sample_report]) == 1
        assert await uow.entities.seed_collection_batch("report_binaries", [sample_binary]) == 1

        verified = await uow.entities.verify_seed_table_counts(
            {
                "organizations": 1,
                "users": 1,
                "model_registries": 1,
                "mcp_gateways": 1,
                "prompt_blocks": 4,
                "task_briefs": 1,
                "steps": 1,
                "workflows": 1,
                "output_profiles": 1,
                "executions": 1,
                "report_artifacts": 1,
                "report_binaries": 1,
            }
        )
        assert verified["organizations"] == 1
        assert verified["executions"] == 1

        if isinstance(uow.entities, PostgresEntityAdapter):
            invitation_sample = Invitation(
                id=generate_uuid7_opaque_id(EntityPrefix.INVITATION),
                organization_id=org_sample.id,
                email="invitee@quorum.ai",
                token_hash="a" * 64,
                invited_by=user_sample.id,
                expires_at=now,
                created_at=now,
            )
            secret_sample = TenantSecretDTO(
                id=generate_uuid7_opaque_id(EntityPrefix.TENANT_SECRET),
                organization_id=org_sample.id,
                scope=SecretScope.LLM_PROVIDER,
                target_identifier="google_vertex",
                storage_mode=SecretStorageMode.ENVELOPE_KMS,
                kek_version="kek-v1",
                masked_hint="...abcd",
                updated_by=user_sample.id,
                updated_at=now,
            )
            assignment_sample = ExecutionAssignment(
                id=generate_uuid7_opaque_id(EntityPrefix.ASSIGNMENT),
                organization_id=org_sample.id,
                assigned_email="assignee@quorum.ai",
                workflow_id=wf_sample.id,
                locked_inputs=WorkflowInputs(dynamic_inputs={}),
                assignee_input_keys=[],
                draft_inputs=WorkflowInputs(dynamic_inputs={}),
                token_hash="b" * 64,
                hard_deadline_at=now,
                created_by=user_sample.id,
                created_at=now,
            )

            # Exercise typed entity CRUD roundtrips on PostgresEntityAdapter
            assert await uow.entities.upsert_organization(org_sample) == org_sample.id
            fetched_org = await uow.entities.get_organization(org_sample.id)
            assert fetched_org is not None and fetched_org.id == org_sample.id
            assert len(await uow.entities.list_organizations()) >= 1

            assert await uow.entities.upsert_user(user_sample) == user_sample.id
            fetched_user = await uow.entities.get_user(user_sample.id)
            assert fetched_user is not None and fetched_user.id == user_sample.id
            assert len(await uow.entities.list_users()) >= 1
            assert len(await uow.entities.list_users(organization_id=user_sample.organization_id)) >= 1

            assert await uow.entities.upsert_invitation(invitation_sample) == invitation_sample.id
            fetched_inv = await uow.entities.get_invitation(invitation_sample.id)
            assert fetched_inv is not None and fetched_inv.id == invitation_sample.id
            assert len(await uow.entities.list_invitations()) >= 1
            assert len(await uow.entities.list_invitations(organization_id=org_sample.id)) >= 1

            assert await uow.entities.upsert_tenant_secret(secret_sample) == secret_sample.id
            fetched_sec = await uow.entities.get_tenant_secret(secret_sample.id)
            assert fetched_sec is not None and fetched_sec.id == secret_sample.id
            assert len(await uow.entities.list_tenant_secrets()) >= 1
            assert len(await uow.entities.list_tenant_secrets(organization_id=org_sample.id)) >= 1

            assert await uow.entities.upsert_execution_assignment(assignment_sample) == assignment_sample.id
            fetched_asgn = await uow.entities.get_execution_assignment(assignment_sample.id)
            assert fetched_asgn is not None and fetched_asgn.id == assignment_sample.id
            assert len(await uow.entities.list_execution_assignments()) >= 1
            assert len(await uow.entities.list_execution_assignments(organization_id=org_sample.id)) >= 1

            assert await uow.entities.upsert_model_registry(reg_sample) == reg_sample.id
            fetched_reg = await uow.entities.get_model_registry(reg_sample.id)
            assert fetched_reg is not None and fetched_reg.id == reg_sample.id

            assert await uow.entities.upsert_mcp_gateway(gw_sample) == gw_sample.id
            fetched_gw = await uow.entities.get_mcp_gateway(gw_sample.id)
            assert fetched_gw is not None and fetched_gw.id == gw_sample.id

            assert await uow.entities.upsert_prompt_block(block_matrix) == block_matrix.id
            fetched_blk = await uow.entities.get_prompt_block(block_matrix.id)
            assert fetched_blk is not None and fetched_blk.id == block_matrix.id

            assert await uow.entities.upsert_step(step_sample) == step_sample.id
            fetched_stp = await uow.entities.get_step(step_sample.id)
            assert fetched_stp is not None and fetched_stp.id == step_sample.id

            assert await uow.entities.upsert_workflow(wf_sample) == wf_sample.id
            fetched_wf = await uow.entities.get_workflow(wf_sample.id)
            assert fetched_wf is not None and fetched_wf.id == wf_sample.id

            assert await uow.entities.upsert_output_profile(profile_sample) == profile_sample.id
            fetched_prf = await uow.entities.get_output_profile(profile_sample.id)
            assert fetched_prf is not None and fetched_prf.id == profile_sample.id

            assert await uow.entities.upsert_report_artifact(sample_report) == sample_report.id
            fetched_rep = await uow.entities.get_report_artifact(sample_report.id)
            assert fetched_rep is not None and fetched_rep.id == sample_report.id

            assert (
                await uow.entities._execute_upsert(
                    "SELECT 1",
                    entity_label="organization",
                    entity_id=org_sample.id,
                )
                == org_sample.id
            )

            # ISTQB Negative Boundaries on entity get methods with malformed Opaque Stripe IDs
            with pytest.raises(AppException) as exc_bad_user_id:
                await uow.entities.get_user("usr_invalid")
            assert exc_bad_user_id.value.error_code == ErrorCodes.VALIDATION_FAILED.value

            with pytest.raises(AppException) as exc_bad_wf_id:
                await uow.entities.get_workflow("wor_invalid")
            assert exc_bad_wf_id.value.error_code == ErrorCodes.VALIDATION_FAILED.value

            # Exercise delete_tenant_secret, audit_logs, usage_records, and SQL FinOps rollups
            assert await uow.entities.delete_tenant_secret(secret_sample.id) is True
            assert await uow.entities.delete_tenant_secret(secret_sample.id) is False

            audit_sample = AuditLogRecord(
                id=generate_uuid7_opaque_id(EntityPrefix.AUDIT_LOG),
                organization_id=org_sample.id,
                actor_id=user_sample.id,
                execution_id=sample_exec.id,
                event_type="EXECUTION_AUDITED",
                resource_type="execution",
                resource_id=sample_exec.id,
                details={"status": "verified"},
                created_at=now,
            )
            assert await uow.entities.insert_audit_log(audit_sample) == audit_sample.id
            listed_audits = await uow.entities.list_audit_logs(organization_id=org_sample.id)
            assert len(listed_audits) == 1 and listed_audits[0].id == audit_sample.id

            with pytest.raises(AppException) as dup_audit_exc:
                await uow.entities.insert_audit_log(audit_sample)
            assert dup_audit_exc.value.error_code == ErrorCodes.CONFLICT.value

            usage_sample = UsageRecord(
                id=generate_uuid7_opaque_id(EntityPrefix.USAGE_RECORD),
                org_id=org_sample.id,
                user_id=user_sample.id,
                execution_id=sample_exec.id,
                model="gemini-2.5-pro",
                input_tokens=200,
                output_tokens=80,
                cached_tokens=40,
                reasoning_tokens=20,
                cache_creation_input_tokens=10,
                cost_usd=0.06,
                estimated_savings_usd=0.02,
                timestamp=now,
            )
            assert await uow.entities.insert_usage_record(usage_sample) == usage_sample.id
            listed_usage = await uow.entities.list_usage_records(organization_id=org_sample.id)
            assert len(listed_usage) == 1 and listed_usage[0].id == usage_sample.id

            rollup_summary = await uow.entities.aggregate_organization_usage(organization_id=org_sample.id)
            assert rollup_summary.record_count == 1
            assert rollup_summary.total_prompt_tokens == 200
            assert rollup_summary.total_completion_tokens == 80
            assert rollup_summary.total_cost_usd == pytest.approx(0.06)

        # Negative boundary 1: unsupported collection name raises VALIDATION_FAILED
        with pytest.raises(AppException) as exc_bad_col:
            await uow.entities.seed_collection_batch("rogue_collection", [org_sample])
        assert exc_bad_col.value.error_code == ErrorCodes.VALIDATION_FAILED.value

        # Negative boundary 2: mismatched entity type for collection raises VALIDATION_FAILED
        with pytest.raises(AppException) as exc_type_mismatch:
            await uow.entities.seed_collection_batch("users", [org_sample])
        assert exc_type_mismatch.value.error_code == ErrorCodes.VALIDATION_FAILED.value

        # Negative boundary 3: unknown table in verify_seed_table_counts raises VALIDATION_FAILED
        with pytest.raises(AppException) as exc_unknown_tbl:
            await uow.entities.verify_seed_table_counts({"unknown_table": 1})
        assert exc_unknown_tbl.value.error_code == ErrorCodes.VALIDATION_FAILED.value

        # Negative boundary 4: count below expected threshold raises STORAGE_ACCESS_FAILED
        with pytest.raises(AppException) as exc_count_low:
            await uow.entities.verify_seed_table_counts({"organizations": 5})
        assert exc_count_low.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value


def test_qgr017_ast_guardrail_blocks_tinydb_resurrection(tmp_path: Path) -> None:
    """Verify QGR017 AST guardrail catches synthetic legacy imports and file path string literals."""
    from scripts._ast_guardrails import scan_files_for_guardrails

    banned_pkg = "tiny" + "db"
    banned_file = "db_v2" + ".json"
    synthetic_file = tmp_path / "synthetic_violation.py"
    synthetic_file.write_text(
        f"import {banned_pkg}\nDB_PATH = 'data/{banned_file}'\n",
        encoding="utf-8",
    )
    violations, is_success = scan_files_for_guardrails([str(synthetic_file)], strict=True)
    assert is_success is False
    qgr017_hits = [v for v in violations if v.rule_code == "QGR017"]
    assert len(qgr017_hits) >= 2


@pytest.mark.asyncio
async def test_pg19_iam_schema_evolution_and_startup_preflight_migrations() -> None:
    """Verify idempotent IAM column migrations, startup/seeder apply_migrations execution, and direct PK lookups."""
    repo_root = Path(__file__).resolve().parents[4]
    sql_text = (repo_root / "backend_v2" / "database" / "migrations" / "001_pg19_uuidv7_schema.sql").read_text(
        encoding="utf-8"
    )
    normalized_sql = " ".join(sql_text.lower().split())

    # 1. Verify idempotent ALTER TABLE ADD COLUMN IF NOT EXISTS statements for evolved IAM and split tables
    assert "alter table organizations add column if not exists allowed_email_domains" in normalized_sql
    assert "alter table users add column if not exists firebase_uid" in normalized_sql
    assert "alter table users add column if not exists deleted_at" in normalized_sql
    assert "and table_name = 'system_configs'" in normalized_sql
    assert "mcp_gateways, model_registries, system_configs, audit_logs" in normalized_sql
    assert "alter table tenant_secrets add column if not exists mcp_gateway_id" in normalized_sql

    # 2. Verify _validate_database_preflight and _seed_postgres apply migrations on PostgresUnitOfWork before table checks
    pool = InMemoryAsyncPgPool()
    for table in ("organizations", "users", "workflows", "prompt_blocks", "task_briefs", "steps", "output_profiles"):
        pool.store.seed_tables[table][f"{table[:3]}_0195f3a0000070008000111111111111"] = (
            f"{table[:3]}_0195f3a0000070008000111111111111",
        )
    from backend_v2.tests.factories.model_factories import SystemConfigModelRegistryFactory

    org_uuid = parse_prefixed_uuid7("org_0195f3a0000070008000000000000001", EntityPrefix.ORGANIZATION)
    mrg_uuid = parse_prefixed_uuid7("mrg_0195f3a0000070008000111111111111", EntityPrefix.MODEL_REGISTRY)
    preflight_reg = SystemConfigModelRegistryFactory.build(id="mrg_0195f3a0000070008000111111111111")
    pool.store.seed_tables["model_registries"][str(mrg_uuid)] = (
        mrg_uuid,
        preflight_reg.slug,
        preflight_reg.name,
        preflight_reg.default_provider.value,
        json.dumps(preflight_reg.model_dump(mode="json")["tier_definitions"]),
        datetime.now(UTC),
    )
    mcp_uuid = parse_prefixed_uuid7("mcp_0195f3a0000070008000111111111111", EntityPrefix.MCP_GATEWAY)
    pool.store.seed_tables["mcp_gateways"][str(mcp_uuid)] = (
        mcp_uuid,
        org_uuid,
        "default_mcp_gateway",
        "Tavily MCP Gateway",
        "https://mcp.tavily.com/mcp",
        "streamable_http",
        "bearer",
        "TAVILY_API_KEY",
        None,
        30,
        "[]",
        datetime.now(UTC),
    )
    settings = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="db.internal",
        postgres_port=5432,
        postgres_user="quorum",
        postgres_db="quorum",
        postgres_command_timeout_seconds=10.0,
    )
    pool_manager = PostgresPoolManager(settings=settings, pool=pool)
    pg_uow = PostgresUnitOfWork(pool_manager=pool_manager)

    assert pool.store.migrations_applied == 0
    await _validate_database_preflight(logging.getLogger("test.preflight"), uow=pg_uow)
    assert pool.store.migrations_applied == 1

    await _seed_postgres({}, dry_run=False, uow=pg_uow)
    assert pool.store.migrations_applied == 3

    # 3. Verify IdentityRepositoryImpl.get_user and get_organization resolve via O(1) EntityPersistencePort lookups
    base_identity_uow = InMemoryUnitOfWork()
    user_id = "usr_0195f3a00000700a83fd6b3d77c748f4"
    org_id = "org_0195f3a0000070008000000000000001"
    expected_user = User(
        id=user_id,
        email="root@quorum.ai",
        role=UserRole.ROOT,
        organization_id=org_id,
        is_active=True,
        language=SystemLocale.FI,
        theme_mode="dark",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    expected_org = Organization(
        id=org_id,
        name="Quorum System",
        is_active=True,
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=1000.0,
        tpm_limit=100000,
        rpm_limit=1000,
        allowed_email_domains=[],
    )
    async with InMemoryUnitOfWork(base_identity_uow.store) as seed_uow:
        await seed_uow.entities.upsert_organization(expected_org)
        await seed_uow.entities.upsert_user(expected_user)

    identity_repo = IdentityRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_identity_uow.store))
    resolved_user = await identity_repo.get_user(user_id)
    assert resolved_user is not None
    assert resolved_user.id == user_id

    resolved_org = await identity_repo.get_organization(org_id)
    assert resolved_org is not None
    assert resolved_org.id == org_id


@pytest.mark.asyncio
async def test_materialize_wave_sql_updates_existing_edge_causal_weight_idempotently(
    uow: QuorumUnitOfWork,
) -> None:
    """Verify _MATERIALIZE_WAVE_SQL and materialize_wave update causal_weight on conflicting edges."""
    normalized_sql = " ".join(_MATERIALIZE_WAVE_SQL.split())
    assert (
        "ON CONFLICT (run_id, source_id, target_id, relation_type) DO UPDATE SET causal_weight = EXCLUDED.causal_weight RETURNING edge_id"
        in normalized_sql
    )

    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    drafts = (
        NodeDraft(
            local_key="claim_1",
            node_type=PropositionNodeType.CLAIM,
            confidence=0.9,
            payload=PropositionPayloadDTO(statement="Claim 1", metadata={}),
        ),
        NodeDraft(
            local_key="ground_1",
            node_type=PropositionNodeType.GROUND,
            confidence=0.85,
            payload=PropositionPayloadDTO(statement="Ground 1", metadata={}),
        ),
    )
    initial_edges = (
        EdgeDraft(
            source_key="ground_1",
            target_key="claim_1",
            relation_type=DependencyRelationType.SUPPORTS,
            causal_weight=0.45,
        ),
    )
    updated_edges = (
        EdgeDraft(
            source_key="ground_1",
            target_key="claim_1",
            relation_type=DependencyRelationType.SUPPORTS,
            causal_weight=0.92,
        ),
    )

    async with uow:
        first_nodes = await uow.graph.materialize_wave(run_id, drafts, initial_edges)
        second_nodes = await uow.graph.materialize_wave(run_id, drafts, updated_edges)
        await uow.commit()

    assert [n.node_id for n in first_nodes] == [n.node_id for n in second_nodes]
    if isinstance(uow, InMemoryUnitOfWork):
        matching_edges = [e for e in uow.store.edges.values() if e.run_id == run_id]
        assert len(matching_edges) == 1
        assert matching_edges[0].causal_weight == pytest.approx(0.92)


@pytest.mark.asyncio
async def test_model_registry_and_mcp_gateway_prefix_and_secret_cascade_and_dropped_fields(
    uow: QuorumUnitOfWork,
) -> None:
    """Verify mrg_/mcp_ prefix enforcement, tenant_secrets.mcp_gateway_id ON DELETE CASCADE, and dropped api_key/parsing_mode rejection."""
    from backend_v2.models.domain.system_config import ModelProfile
    from backend_v2.models.llm import LLMProviderConfig
    from backend_v2.tests.factories.model_factories import (
        ModelProfileFactory,
        SystemConfigMCPGatewaysFactory,
        SystemConfigModelRegistryFactory,
    )

    now = datetime.now(UTC)
    org_id = "org_0195f3a0000070008000000000000001"
    user_id = "usr_0195f3a00000700a83fd6b3d77c748f4"

    # Contract #1: SystemConfigModelRegistry requires mrg_ prefix; SystemConfigMCPGateways requires mcp_ prefix
    reg = SystemConfigModelRegistryFactory.build(
        id=generate_uuid7_opaque_id(EntityPrefix.MODEL_REGISTRY),
    )
    gw = SystemConfigMCPGatewaysFactory.build(
        id=generate_uuid7_opaque_id(EntityPrefix.MCP_GATEWAY),
        organization_id=org_id,
    )
    assert reg.id.startswith("mrg_")
    assert gw.id.startswith("mcp_")

    retired_sys_id = "sys" + "_0195f3a0000070008000e26807f3bfa3"
    with pytest.raises(ValidationError):
        SystemConfigModelRegistryFactory.build(
            id=retired_sys_id,
        )
    with pytest.raises(ValidationError):
        SystemConfigModelRegistryFactory.build(
            id=gw.id,
        )
    with pytest.raises(ValidationError):
        SystemConfigMCPGatewaysFactory.build(
            id=reg.id,
            organization_id=org_id,
        )
    with pytest.raises(ValidationError):
        SystemConfigModelRegistry.model_validate(
            {**reg.model_dump(mode="json"), "type": "model_registry"},
        )

    # Contract #4: ModelProfile and LLMProviderConfig reject deprecated api_key and parsing_mode fields
    valid_profile_dump = ModelProfileFactory.build().model_dump(mode="json")
    with pytest.raises(ValidationError):
        ModelProfile.model_validate({**valid_profile_dump, "api_key": "leaked-key"})
    with pytest.raises(ValidationError):
        ModelProfile.model_validate({**valid_profile_dump, "parsing_mode": "structured_output"})
    with pytest.raises(ValidationError):
        LLMProviderConfig.model_validate(
            {
                "model_name": "gemini-2.5-pro",
                "provider_type": "google_vertex",
                "parsing_mode": "structured_output",
            }
        )

    # Contract #2: Deleting an MCP gateway cascades to its bound MCP_GATEWAY TenantSecretDTO
    mcp_secret = TenantSecretDTO(
        id=generate_uuid7_opaque_id(EntityPrefix.TENANT_SECRET),
        organization_id=org_id,
        scope=SecretScope.MCP_GATEWAY,
        target_identifier=gw.id,
        storage_mode=SecretStorageMode.ENVELOPE_KMS,
        kek_version="kek-v1",
        masked_hint="...9999",
        updated_by=user_id,
        updated_at=now,
    )
    invalid_mcp_secret = TenantSecretDTO(
        id=generate_uuid7_opaque_id(EntityPrefix.TENANT_SECRET),
        organization_id=org_id,
        scope=SecretScope.MCP_GATEWAY,
        target_identifier="tavily_non_canonical_slug",
        storage_mode=SecretStorageMode.ENVELOPE_KMS,
        kek_version="kek-v1",
        masked_hint="...9999",
        updated_by=user_id,
        updated_at=now,
    )

    async with uow:
        with pytest.raises(AppException) as exc_invalid_mcp:
            await uow.entities.upsert_tenant_secret(invalid_mcp_secret)
        assert exc_invalid_mcp.value.error_code == ErrorCodes.VALIDATION_FAILED.value
        await uow.entities.upsert_mcp_gateway(gw)
        await uow.entities.upsert_tenant_secret(mcp_secret)
        assert await uow.entities.get_tenant_secret(mcp_secret.id) is not None
        assert await uow.entities.delete_mcp_gateway(gw.id) is True
        assert await uow.entities.get_mcp_gateway(gw.id) is None
        assert await uow.entities.get_tenant_secret(mcp_secret.id) is None
