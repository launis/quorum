"""Unit tests for CausalGraphAdapter and SduiCausalGraphBlock serialization.

Tests compliance with Dumb Painter SDUI architecture, Zero New Output Profiles Invariant,
and strict Pydantic V2 schema validations (extra='forbid').
"""

from __future__ import annotations

import pydantic
import pytest
from pydantic import TypeAdapter

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.proposition_graph import FalsifiedClaimMatch
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
    PrescriptiveRemediationDTO,
)
from backend_v2.models.enums import EntityPrefix, ExecutionStatus, TargetBlockType
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    SduiCausalGraphBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.causal_graph_adapter import CausalGraphAdapter
from backend_v2.services.sdui.adapters.executive_summary_adapter import ExecutiveSummaryAdapter
from backend_v2.tests.factories.model_factories import OutputProfileFactory


def _build_sample_fusion_result() -> CausalTdaFusionResultDTO:
    """Creates a mathematically valid sample fusion result for testing."""
    node1 = CausalNodeDTO(
        node_id="atm_01",
        claim="Foundational architecture assumption holds true.",
        source_quotes=("Foundational verified quote.",),
        paragraph_ref="Section 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["atm_02"],
        tda_score=5.0,
        tda_level_key="L5",
    )
    node2 = CausalNodeDTO(
        node_id="atm_02",
        claim="Downstream interface verification.",
        source_quotes=("Interface failure quote.",),
        paragraph_ref="Section 2",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["atm_01"],
        dependent_child_ids=[],
        tda_score=1.0,
        tda_level_key="L1",
    )
    edge = CausalEdgeDTO(
        source_id="atm_01",
        target_id="atm_02",
        reasoning="Dependency implies interface requirement.",
    )
    graph = CausalGraphPayloadDTO(
        nodes=[node1, node2],
        edges=[edge],
        root_cause_node_ids=["atm_01"],
        cycle_detected=False,
        isolated_node_ids=[],
        partition_node_ids={},
        edge_root_causes=[],
    )
    diag = CausalRootCauseDiagnosisDTO(
        failing_node_id="atm_02",
        root_cause_parent_id="atm_01",
        paragraph_ref="Section 2",
        explanation="Root assumption lacked schema boundary.",
        penalty_points=1.5,
    )
    audit = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=1,
        logical_cohesion_score=0.9,
        detected_hollow_terms=[],
    )
    remediation = PrescriptiveRemediationDTO(
        target_node_id="atm_02",
        required_action="Add extra='forbid' to model.",
        unlocks_node_ids=["atm_03"],
        potential_score_impact=1.5,
    )
    fair_scoring = FairScoringBreakdownDTO(
        independent_error_count=1,
        cascading_fault_count=1,
        raw_penalty_points=3.0,
        deduplicated_penalty_points=1.5,
        dampened_savings_points=1.5,
    )
    return CausalTdaFusionResultDTO(
        graph=graph,
        root_cause_diagnoses=[diag],
        anti_fluff_audit=audit,
        prescriptive_remediations=[remediation],
        fair_scoring=fair_scoring,
    )


def _build_sample_adapter_context(
    causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None,
    is_data_starved: bool = False,
) -> AdapterContext:
    """Builds a minimal AdapterContext for adapter testing."""
    profile: OutputProfile = OutputProfileFactory.build(
        content_blocks=[],
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )
    cache = None
    if is_data_starved:
        cache = RenderedSynthesisCache(data_starvation=DataStarvationEvent(total_atoms=0, reason="insufficient_tokens"))

    return AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
        mcp_tools_map={},
        causal_result=causal_result,
    )


def test_sdui_causal_graph_block_serialization_roundtrip() -> None:
    """TC-CONTRACT-01: Verifies SduiCausalGraphBlock roundtrip serialization into AnySduiBlock union."""
    fusion = _build_sample_fusion_result()
    ctx = _build_sample_adapter_context(causal_result=fusion)
    block = CausalGraphAdapter.build_action_card(ctx)

    assert block.block_type == "causal_graph"
    assert len(block.critical_path_nodes) == 2
    assert len(block.critical_edges) == 1
    assert len(block.root_cause_diagnoses) == 1
    assert block.intact_claims_count == 1
    assert block.total_claims_count == 2

    # Serialize to JSON and re-validate via discriminated union AnySduiBlock
    json_str = block.model_dump_json()
    revalidated: AnySduiBlock = TypeAdapter(AnySduiBlock).validate_json(json_str)
    assert isinstance(revalidated, SduiCausalGraphBlock)
    assert revalidated.intact_claims_count == 1
    assert revalidated.total_claims_count == 2
    assert revalidated.summary.translations["en"] == block.summary.translations["en"]


def test_sdui_causal_graph_block_extra_field_forbid() -> None:
    """TC-CONTRACT-02: Asserts that unrecognized fields in SduiCausalGraphBlock trigger ValidationError."""
    fusion = _build_sample_fusion_result()
    ctx = _build_sample_adapter_context(causal_result=fusion)
    block = CausalGraphAdapter.build_action_card(ctx)
    payload = block.model_dump(mode="python")

    # Inject unrecognized field
    payload["unrecognized_extraneous_field"] = "malicious_or_accidental_payload"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        SduiCausalGraphBlock.model_validate(payload)

    assert "extra_forbidden" in str(exc_info.value)


def test_executive_summary_adapter_injects_causal_block_when_present() -> None:
    """TC-CONTRACT-03: Asserts ExecutiveSummaryAdapter injects SduiCausalGraphBlock into EXECUTIVE_SUMMARY_BLOCK."""
    fusion = _build_sample_fusion_result()
    ctx = _build_sample_adapter_context(causal_result=fusion)

    blocks = ExecutiveSummaryAdapter.build(ctx)

    # Must contain SduiCausalGraphBlock
    causal_blocks = [b for b in blocks if isinstance(b, SduiCausalGraphBlock)]
    assert len(causal_blocks) == 1
    causal_card = causal_blocks[0]
    assert causal_card.block_type == "causal_graph"
    assert causal_card.intact_claims_count == 1
    assert causal_card.total_claims_count == 2


def test_executive_summary_adapter_omits_causal_block_when_absent() -> None:
    """TC-CONTRACT-04: Asserts ExecutiveSummaryAdapter cleanly omits SduiCausalGraphBlock when causal_result is None."""
    ctx = _build_sample_adapter_context(causal_result=None)

    blocks = ExecutiveSummaryAdapter.build(ctx)

    causal_blocks = [b for b in blocks if isinstance(b, SduiCausalGraphBlock)]
    assert len(causal_blocks) == 0


def test_causal_graph_adapter_data_starvation_omits_block() -> None:
    """TC-CONTRACT-05: Asserts CausalGraphAdapter returns empty list when data is starved."""
    fusion = _build_sample_fusion_result()
    ctx = _build_sample_adapter_context(causal_result=fusion, is_data_starved=True)

    blocks = CausalGraphAdapter.build(ctx)
    assert blocks == []


def test_causal_graph_adapter_build_valid_returns_card() -> None:
    """Asserts CausalGraphAdapter.build returns list with SduiCausalGraphBlock when valid."""
    fusion = _build_sample_fusion_result()
    ctx = _build_sample_adapter_context(causal_result=fusion)
    blocks = CausalGraphAdapter.build(ctx)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiCausalGraphBlock)


def test_causal_graph_adapter_build_action_card_none_raises() -> None:
    """Asserts build_action_card raises AppException if causal_result is None."""
    ctx = _build_sample_adapter_context(causal_result=None)
    with pytest.raises(AppException) as exc_info:
        CausalGraphAdapter.build_action_card(ctx)
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_causal_graph_adapter_with_graph_payload_only() -> None:
    """Asserts CausalGraphAdapter handles raw CausalGraphPayloadDTO without fusion."""
    fusion = _build_sample_fusion_result()
    ctx = _build_sample_adapter_context(causal_result=fusion.graph)
    card = CausalGraphAdapter.build_action_card(ctx)
    assert card.block_type == "causal_graph"
    assert card.anti_fluff_audit is not None
    assert card.fair_scoring is None
    assert len(card.root_cause_diagnoses) == 0


def test_causal_graph_adapter_no_critical_nodes_falls_back_to_all_nodes() -> None:
    """Asserts CausalGraphAdapter falls back to all nodes when no critical nodes exist."""
    node = CausalNodeDTO(
        node_id="atm_clean",
        claim="Clean proposition.",
        source_quotes=("Clean quote.",),
        paragraph_ref="Section 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
        tda_score=5.0,
        tda_level_key="L5",
    )
    graph = CausalGraphPayloadDTO(
        nodes=[node],
        edges=[],
        root_cause_node_ids=[],
        cycle_detected=False,
        isolated_node_ids=[],
        partition_node_ids={},
        edge_root_causes=[],
    )
    ctx = _build_sample_adapter_context(causal_result=graph)
    card = CausalGraphAdapter.build_action_card(ctx)
    assert len(card.critical_path_nodes) == 1
    assert card.critical_path_nodes[0].node_id == "atm_clean"


def test_causal_graph_adapter_with_cycle_and_isolated_nodes_boundary() -> None:
    """Asserts boundary values when raw CausalGraphPayloadDTO has cycle_detected=True and isolated nodes."""
    node = CausalNodeDTO(
        node_id="atm_iso",
        claim="Isolated proposition in cycle.",
        source_quotes=("Isolated quote.",),
        paragraph_ref="Section 3",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=[],
        dependent_child_ids=[],
        tda_score=1.0,
        tda_level_key="L1",
    )
    graph = CausalGraphPayloadDTO(
        nodes=[node],
        edges=[],
        root_cause_node_ids=["atm_iso"],
        cycle_detected=True,
        isolated_node_ids=["atm_iso"],
        partition_node_ids={},
        edge_root_causes=[],
    )
    ctx = _build_sample_adapter_context(causal_result=graph)
    card = CausalGraphAdapter.build_action_card(ctx)
    assert card.anti_fluff_audit.cycle_detected is True
    assert card.anti_fluff_audit.isolated_concept_count == 1
    assert card.anti_fluff_audit.logical_cohesion_score == 0.5
    assert card.intact_claims_count == 0
    assert card.total_claims_count == 1


def test_adapter_context_invalid_causal_result_type_raises() -> None:
    """Asserts AdapterContext rejects invalid causal_result types under strict Pydantic validation."""
    profile: OutputProfile = OutputProfileFactory.build(
        content_blocks=[],
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )
    with pytest.raises(pydantic.ValidationError):
        AdapterContext.model_validate(
            {
                "execution": None,
                "locale": "en",
                "penalties_applied": [],
                "mcp_audit_map": None,
                "global_score": None,
                "profile": profile,
                "profile_cache": None,
                "user_name": None,
                "org_name": None,
                "parsed_matrices": {},
                "mcp_tools_map": {},
                "causal_result": "invalid_untyped_payload",
            }
        )


def test_causal_graph_adapter_enriches_falsified_warrant_and_short_circuit_lineage() -> None:
    """Asserts build_action_card enriches nodes and block with falsified warrants and short-circuit claims."""
    rebuttal_id = generate_opaque_id(EntityPrefix.NODE)
    warrant_id = generate_opaque_id(EntityPrefix.NODE)
    falsified_id = generate_opaque_id(EntityPrefix.NODE)
    unmapped_rebuttal_id = generate_opaque_id(EntityPrefix.NODE)
    unmapped_warrant_id = generate_opaque_id(EntityPrefix.NODE)

    node_rebuttal = CausalNodeDTO(
        node_id=rebuttal_id,
        claim="  Rebuttal evidence invalidates premise.  ",
        source_quotes=("Rebuttal quote.",),
        paragraph_ref="Section 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[warrant_id],
        tda_score=5.0,
        tda_level_key="L5",
    )
    node_warrant = CausalNodeDTO(
        node_id=warrant_id,
        claim="  Warrant connecting premise to conclusion.  ",
        source_quotes=("Warrant quote.",),
        paragraph_ref="Section 2",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=[rebuttal_id],
        dependent_child_ids=[falsified_id],
        tda_score=1.0,
        tda_level_key="L1",
    )
    node_falsified = CausalNodeDTO(
        node_id=falsified_id,
        claim="Falsified downstream claim statement.",
        source_quotes=("Falsified quote.",),
        paragraph_ref="Section 3",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
        tda_score=3.0,
        tda_level_key="L3",
        short_circuited_by_claims=["Pre-existing short circuit"],
        falsified_warrant_claims=["Pre-existing warrant lineage"],
    )
    graph = CausalGraphPayloadDTO(
        nodes=[node_rebuttal, node_warrant, node_falsified],
        edges=[
            CausalEdgeDTO(
                source_id=rebuttal_id,
                target_id=warrant_id,
                reasoning="Rebuttal challenges warrant.",
            ),
            CausalEdgeDTO(
                source_id=warrant_id,
                target_id=falsified_id,
                reasoning="Warrant underpins claim.",
            ),
        ],
        root_cause_node_ids=[rebuttal_id],
        cycle_detected=False,
        isolated_node_ids=[],
        partition_node_ids={},
        edge_root_causes=[],
    )
    diag = CausalRootCauseDiagnosisDTO(
        failing_node_id=warrant_id,
        root_cause_parent_id=rebuttal_id,
        paragraph_ref="Section 2",
        explanation="Warrant was invalidated by rebuttal.",
        penalty_points=1.5,
        root_cause_claim="  Diagnosed root cause claim.  ",
        failing_node_claim="Warrant connecting premise to conclusion.",
    )
    fc_mapped = FalsifiedClaimMatch(
        rebuttal_id=rebuttal_id,
        invalidated_warrant_id=warrant_id,
        falsified_claim_id=falsified_id,
        rebuttal_confidence=0.95,
        claim_statement="Falsified downstream claim statement.",
    )
    fc_unmapped_nodes = FalsifiedClaimMatch(
        rebuttal_id=unmapped_rebuttal_id,
        invalidated_warrant_id=unmapped_warrant_id,
        falsified_claim_id=falsified_id,
        rebuttal_confidence=0.85,
        claim_statement="Secondary falsified claim statement.",
    )
    fusion = CausalTdaFusionResultDTO(
        graph=graph,
        root_cause_diagnoses=[diag],
        anti_fluff_audit=AntiFluffAuditDTO(
            isolated_concept_count=0,
            cycle_detected=False,
            unsupported_claims_count=1,
            logical_cohesion_score=0.85,
            detected_hollow_terms=[],
        ),
        prescriptive_remediations=[],
        fair_scoring=FairScoringBreakdownDTO(
            independent_error_count=1,
            cascading_fault_count=1,
            raw_penalty_points=3.0,
            deduplicated_penalty_points=1.5,
            dampened_savings_points=1.5,
        ),
        falsified_claims=[fc_mapped, fc_unmapped_nodes],
    )
    ctx = _build_sample_adapter_context(causal_result=fusion)
    card = CausalGraphAdapter.build_action_card(ctx)

    # All 3 nodes should be in critical_path_nodes (including falsified_id via extra_node_ids)
    assert len(card.critical_path_nodes) == 3
    warrant_enriched = next(n for n in card.critical_path_nodes if n.node_id == warrant_id)
    assert "Rebuttal evidence invalidates premise." in warrant_enriched.short_circuited_by_claims
    assert "Diagnosed root cause claim." in warrant_enriched.short_circuited_by_claims

    falsified_enriched = next(n for n in card.critical_path_nodes if n.node_id == falsified_id)
    expected_mapped_lineage = (
        "Rebuttal evidence invalidates premise. -> "
        "Warrant connecting premise to conclusion. -> "
        "Falsified downstream claim statement."
    )
    expected_unmapped_lineage = (
        f"{unmapped_rebuttal_id} -> {unmapped_warrant_id} -> Secondary falsified claim statement."
    )
    assert expected_mapped_lineage in falsified_enriched.falsified_warrant_claims
    assert expected_unmapped_lineage in falsified_enriched.falsified_warrant_claims
    assert "Pre-existing warrant lineage" in falsified_enriched.falsified_warrant_claims

    assert "Diagnosed root cause claim." in card.short_circuited_by_claims
    assert "Rebuttal evidence invalidates premise." in card.short_circuited_by_claims
    assert "Pre-existing short circuit" in card.short_circuited_by_claims
    assert expected_mapped_lineage in card.falsified_warrant_claims
    assert expected_unmapped_lineage in card.falsified_warrant_claims
    assert "Pre-existing warrant lineage" in card.falsified_warrant_claims
