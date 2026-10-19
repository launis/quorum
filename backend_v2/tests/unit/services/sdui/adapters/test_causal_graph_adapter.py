"""Unit tests for CausalGraphAdapter and SduiCausalGraphBlock serialization.

Tests compliance with Dumb Painter SDUI architecture, Zero New Output Profiles Invariant,
and strict Pydantic V2 schema validations (extra='forbid').
"""

from __future__ import annotations

import pydantic
import pytest
from pydantic import TypeAdapter

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
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
from backend_v2.models.enums import ExecutionStatus, TargetBlockType
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    SduiCausalGraphBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.causal_graph_adapter import CausalGraphAdapter
from backend_v2.services.sdui.adapters.executive_summary_adapter import ExecutiveSummaryAdapter


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
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test_executive_profile",
        workflow_id="wor_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test Executive Profile"}),
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
