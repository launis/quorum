"""Contract Test Suite & ISTQB Negative Verification for PostgreSQL 19 Zero-ORM Architecture.

Verifies 1:1 behavioral parity across InMemoryUnitOfWork and PostgresUnitOfWork (backed by
InMemoryAsyncPgPool from backend_v2/tests/fakes/in_memory_uow.py), Single-Round Multi-CTE
wave materialization with ON CONFLICT DO SELECT RETURNING, Toulmin falsification queries,
ReportBinaryPayloadDTO TOAST roundtrips, binary pydantic_core JSONB codecs, 1:1 DDL Schema
vs. Domain DTO Column Naming Parity across all 12 tables, and ISTQB negative boundaries.
"""

from __future__ import annotations

import re
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
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
)
from backend_v2.database.postgres.entity_adapter import (
    _coerce_float,
    _coerce_uuid_or_str,
    _decode_jsonb_column,
)
from backend_v2.database.postgres.graph_adapter import (
    _coerce_uuid_or_str as _graph_coerce_uuid_or_str,
)
from backend_v2.database.postgres.graph_adapter import (
    _extract_cycle_node_ids,
    _hydrate_payload_dto,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, User
from backend_v2.models.core_base import (
    I18nText,
    V2CoreBase,
    generate_uuid7_opaque_id,
    parse_prefixed_uuid7,
)
from backend_v2.models.domain.execution import (
    ExecutionRecord,
    ExecutionStep,
    ExecutionSummarySnapshot,
    FrozenContext,
)
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
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.mcp import (
    MCPIconDTO,
    MCPServerInfoDTO,
    MCPToolExecutionDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
)
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
    StepType,
    StepZone,
    StorageBackend,
    ToolCapability,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
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
    }
    for match in pattern.finditer(sql_text):
        table_name = match.group(1).lower()
        body = match.group(2)
        cols: set[str] = set()
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("--"):
                continue
            cleaned = line.rstrip(",")
            tokens = cleaned.split()
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
# Step 5, Positive Case 1: Single-Round Wave Materialization & Roundtrip
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
            created_at=datetime.now(timezone.utc),
        )
        await uow.graph.upsert_wave_batch((updated_ground,), (direct_edge,))
        await uow.graph.assert_acyclic(run_id)

    # Verify state persisted after UoW commit
    async with uow:
        committed_roots = await uow.topology.fetch_next_kahn_wave(run_id)
        assert len(committed_roots) == 1
        assert committed_roots[0].confidence == 0.99


# ============================================================================
# Step 5, Positive Case 2: Toulmin Falsification Query Parity
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
# Step 5, Positive Case 3: Report Binary TOAST Roundtrip & Binary JSONB Codec
# ============================================================================


@pytest.mark.asyncio
async def test_report_binary_toast_and_execution_roundtrip(uow: QuorumUnitOfWork) -> None:
    """Verify ReportBinaryPayloadDTO TOAST roundtrip, ExecutionRecord FinOps + MCP trace roundtrip, and JSONB codec."""
    report_id = generate_uuid7_opaque_id(EntityPrefix.REPORT)
    pdf_payload = b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"
    now_utc = datetime.now(timezone.utc)

    binary_dto = ReportBinaryPayloadDTO(
        report_id=report_id,
        mime_type="application/pdf",
        pdf_bytes=pdf_payload,
        size_bytes=len(pdf_payload),
        created_at=now_utc,
    )

    exec_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    wf_id = generate_uuid7_opaque_id(EntityPrefix.WORKFLOW)
    gw_id = generate_uuid7_opaque_id(EntityPrefix.SYSTEM_CONFIG)
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
        step_name="step_fact_verification",
        event_type="output",
        content="Step completed with external MCP verification.",
        mcp_audit_traces=[mcp_trace],
    )
    execution_record = ExecutionRecord(
        id=exec_id,
        workflow_id=wf_id,
        workflow_version=2,
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        progress=100,
        status_message="Completed",
        frozen_context=FrozenContext(
            compiled_prompts={"stp_a1b2c3d4e5f60718": "<system_directive>Verify</system_directive>"},
            mcp_tool_audit=[mcp_trace],
        ),
        steps=[
            ExecutionStep(
                id="stp_a1b2c3d4e5f60718",
                label="Fact Verification",
                status=ExecutionStatus.PASSED,
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
# Step 5, Positive Case 4: PostgreSQL 19 DDL Schema vs. Domain DTO Naming Parity
# ============================================================================


def test_schema_dto_naming_parity() -> None:
    """Assert 1:1 bi-directional column-to-field naming parity across all 12 tables and MCP JSONB structures."""
    sql_text = _MIGRATION_SQL_PATH.read_text(encoding="utf-8")
    assert "SET default_toast_compression = 'lz4';" in sql_text
    assert "CREATE STATISTICS IF NOT EXISTS stat_quorum_nodes_run_created" in sql_text
    assert "CREATE STATISTICS IF NOT EXISTS stat_quorum_edges_run_created" in sql_text

    parsed_tables = _extract_sql_table_columns(sql_text)
    expected_12_tables = {
        "organizations",
        "users",
        "system_configs",
        "prompt_blocks",
        "steps",
        "workflows",
        "output_profiles",
        "executions",
        "report_artifacts",
        "report_binaries",
        "quorum_nodes",
        "quorum_edges",
    }
    assert set(parsed_tables.keys()) == expected_12_tables

    # 1. quorum_nodes <-> PropositionNode + NodeDraft.local_key
    assert parsed_tables["quorum_nodes"] == set(PropositionNode.model_fields.keys()) | {"local_key"}

    # 2. quorum_edges <-> DependencyEdge
    assert parsed_tables["quorum_edges"] == set(DependencyEdge.model_fields.keys())

    # 3. report_binaries <-> ReportBinaryPayloadDTO
    assert parsed_tables["report_binaries"] == set(ReportBinaryPayloadDTO.model_fields.keys())

    # 4. executions <-> ExecutionRecord
    assert parsed_tables["executions"] == set(ExecutionRecord.model_fields.keys())

    # 5. report_artifacts <-> ReportArtifact + has_pdf sidecar flag
    assert parsed_tables["report_artifacts"] == set(ReportArtifact.model_fields.keys()) | {"has_pdf"}

    # 6. workflows <-> Workflow
    assert parsed_tables["workflows"] == set(Workflow.model_fields.keys())

    # 7. steps <-> Step
    assert parsed_tables["steps"] == set(Step.model_fields.keys())

    # 8. prompt_blocks <-> Polymorphic union of all concrete PromptBlock models
    prompt_block_union_fields = (
        set(MatrixPromptBlock.model_fields.keys())
        | set(SystemRulePromptBlock.model_fields.keys())
        | set(PersonaPromptBlock.model_fields.keys())
        | set(ProtocolPromptBlock.model_fields.keys())
    )
    assert parsed_tables["prompt_blocks"] == prompt_block_union_fields

    # 9. output_profiles <-> OutputProfile
    assert parsed_tables["output_profiles"] == set(OutputProfile.model_fields.keys())

    # 10. system_configs <-> Union of SystemConfigModelRegistry and SystemConfigMCPGateways
    system_config_union_fields = set(SystemConfigModelRegistry.model_fields.keys()) | set(
        SystemConfigMCPGateways.model_fields.keys()
    )
    assert parsed_tables["system_configs"] == system_config_union_fields

    # 11. users <-> User
    assert parsed_tables["users"] == set(User.model_fields.keys())

    # 12. organizations <-> Organization
    assert parsed_tables["organizations"] == set(Organization.model_fields.keys())

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
        id=generate_uuid7_opaque_id(EntityPrefix.SYSTEM_CONFIG),
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
        id=generate_uuid7_opaque_id(EntityPrefix.STEP),
        slug="step_mcp_research",
        name=I18nText(translations={"fi": "Tutkimusvaihe", "en": "Research Step"}),
        type=StepType.LLM,
        extraction_protocol_block_id=generate_uuid7_opaque_id(EntityPrefix.PROMPT_BLOCK),
        criteria_block_ids=[generate_uuid7_opaque_id(EntityPrefix.PROMPT_BLOCK)],
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
# Step 5, Negative Case 1: DAG Cycle Detection Fail-Fast
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
# Step 5, Negative Case 2: Transactional Rollback & Isolation
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
# Step 5, Negative Case 3: ISTQB Boundary Value Analysis & Pool/Adapter Faults
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
    try:
        pool.inject_fault("acquire", OSError("pool exhausted"))
        with pytest.raises(AppException) as exc_acq:
            async with manager_pw.acquire_connection():
                pass
        assert exc_acq.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()

    try:
        pool.inject_fault("set_type_codec", RuntimeError("codec registration rejected"))
        with pytest.raises(AppException) as exc_codec:
            async with manager_pw.acquire_connection():
                pass
        assert exc_codec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()

    try:
        pool.inject_fault("execute", RuntimeError("DDL execution error"))
        with pytest.raises(AppException) as exc_ddl:
            await manager_pw.apply_migrations()
        assert exc_ddl.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
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
    finally:
        pool.clear_faults()

    try:
        pool.inject_fault("tx_rollback", RuntimeError("rollback transport error"))
        with pytest.raises(AppException) as exc_tx_rb:
            async with PostgresUnitOfWork(pool_manager=manager_pw) as rb_uow:
                await rb_uow.rollback()
        assert exc_tx_rb.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()

    # ReportBinaryPayloadDTO size mismatch raises AppException(VALIDATION_FAILED)
    bad_binary = ReportBinaryPayloadDTO(
        report_id=generate_uuid7_opaque_id(EntityPrefix.REPORT),
        pdf_bytes=b"12345",
        size_bytes=999,
        created_at=datetime.now(timezone.utc),
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
    finally:
        pool.clear_faults()

    manager_close_ok = PostgresPoolManager(settings=settings_with_pw, pool=pool)
    await manager_close_ok.close()
    assert pool.closed is True
    # Calling close() again when pool is already None is a safe no-op
    await manager_close_ok.close()

    # Lazy asyncpg import path when pool is None: module-scoped monkeypatch
    class _FakeAsyncPgDriverModule:
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

    monkeypatch.setattr(
        "backend_v2.database.postgres.pool._import_asyncpg_module",
        lambda: _FakeAsyncPgDriverModule(),
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
    manager = PostgresPoolManager(settings=settings, pool=pool)
    run_id = generate_uuid7_opaque_id(EntityPrefix.EXECUTION)
    node_id_1 = generate_uuid7_opaque_id(EntityPrefix.NODE)
    node_id_2 = generate_uuid7_opaque_id(EntityPrefix.NODE)
    edge_id = generate_uuid7_opaque_id(EntityPrefix.EDGE)
    report_id = generate_uuid7_opaque_id(EntityPrefix.REPORT)
    now_utc = datetime.now(timezone.utc)

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
        assert default_graph.command_timeout_seconds == 22.5
        assert default_reasoning.command_timeout_seconds == 22.5

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
                workflow_id=generate_uuid7_opaque_id(EntityPrefix.WORKFLOW),
                target_locale="en",
            )
        )
    assert exc_unbound_save_exec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value
    with pytest.raises(AppException) as exc_unbound_get_exec:
        await unbound_uow.entities.get_execution(run_id)
    assert exc_unbound_get_exec.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED.value

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
            workflow_id=generate_uuid7_opaque_id(EntityPrefix.WORKFLOW),
            target_locale="en",
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
        finally:
            pool.clear_faults()

    # Verify InMemoryAsyncPgRecord membership check
    rec = InMemoryAsyncPgRecord({"node_id": "nod_123"})
    assert "node_id" in rec
    assert 42 not in rec


# ============================================================================
# Step 5, Negative Case 4: Zero-ORM AST Guardrail & Codebase Verification
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

    # Synthetic negative verification for ZORM004 (rogue SQL table outside the closed 12-table topology)
    bad_sql_file = tmp_path / "rogue_schema.sql"
    bad_sql_file.write_text(
        "CREATE TABLE IF NOT EXISTS rogue_shadow_table (id UUID PRIMARY KEY);\n",
        encoding="utf-8",
    )
    sql_findings = audit_sql_migration_file(bad_sql_file)
    assert len(sql_findings) == 1
    assert sql_findings[0].rule_code == ZeroOrmRuleCode.ZORM004
