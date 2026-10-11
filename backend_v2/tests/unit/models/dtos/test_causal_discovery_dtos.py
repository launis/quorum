"""Unit tests for causal discovery DTO contracts.

Validates referential integrity, mathematical identity, boundary values,
immutability, and full integration with StepOutputDTO.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.enums import ExecutionStatus


def _create_sample_node(node_id: str, claim: str = "Sample claim") -> CausalNodeDTO:
    """Helper creating a valid CausalNodeDTO."""
    return CausalNodeDTO(
        node_id=node_id,
        claim=claim,
        status=ExecutionStatus.PASSED,
        source_quote="Exact quote",
        paragraph_ref="p1",
    )


def test_causal_graph_payload_referential_integrity_valid() -> None:
    """Positive test: Valid referential integrity in CausalGraphPayloadDTO."""
    n0 = _create_sample_node("node_0")
    n1 = _create_sample_node("node_1")
    edge = CausalEdgeDTO(source_id="node_0", target_id="node_1", reasoning="Prerequisite")

    payload = CausalGraphPayloadDTO(
        nodes=[n0, n1],
        edges=[edge],
        root_cause_node_ids=["node_0"],
        isolated_node_ids=["node_1"],
    )
    assert len(payload.nodes) == 2
    assert len(payload.edges) == 1
    assert payload.root_cause_node_ids == ["node_0"]
    assert payload.isolated_node_ids == ["node_1"]


def test_causal_graph_payload_dangling_edge_source_raises_validation_error() -> None:
    """Error path: Edge source_id referencing nonexistent node raises ValidationError."""
    n0 = _create_sample_node("node_0")
    edge = CausalEdgeDTO(source_id="node_999", target_id="node_0", reasoning="Missing source")

    with pytest.raises(ValidationError, match="Edge source_id 'node_999' does not exist in graph nodes"):
        CausalGraphPayloadDTO(nodes=[n0], edges=[edge])


def test_causal_graph_payload_dangling_edge_target_raises_validation_error() -> None:
    """Error path: Edge target_id referencing nonexistent node raises ValidationError."""
    n0 = _create_sample_node("node_0")
    edge = CausalEdgeDTO(source_id="node_0", target_id="node_999", reasoning="Missing target")

    with pytest.raises(ValidationError, match="Edge target_id 'node_999' does not exist in graph nodes"):
        CausalGraphPayloadDTO(nodes=[n0], edges=[edge])


def test_causal_graph_payload_dangling_root_cause_raises_validation_error() -> None:
    """Error path: root_cause_node_ids referencing nonexistent node raises ValidationError."""
    n0 = _create_sample_node("node_0")

    with pytest.raises(ValidationError, match="Root cause node_id 'node_999' does not exist in graph nodes"):
        CausalGraphPayloadDTO(nodes=[n0], root_cause_node_ids=["node_999"])


def test_causal_graph_payload_dangling_isolated_node_raises_validation_error() -> None:
    """Error path: isolated_node_ids referencing nonexistent node raises ValidationError."""
    n0 = _create_sample_node("node_0")

    with pytest.raises(ValidationError, match="Isolated node_id 'node_999' does not exist in graph nodes"):
        CausalGraphPayloadDTO(nodes=[n0], isolated_node_ids=["node_999"])


def test_fair_scoring_breakdown_identity_valid() -> None:
    """Positive test: Mathematical identity raw == deduplicated + dampened_savings succeeds."""
    breakdown = FairScoringBreakdownDTO(
        independent_error_count=1,
        cascading_fault_count=2,
        raw_penalty_points=10.0,
        deduplicated_penalty_points=7.5,
        dampened_savings_points=2.5,
    )
    assert breakdown.raw_penalty_points == 10.0
    assert abs(breakdown.raw_penalty_points - (breakdown.deduplicated_penalty_points + breakdown.dampened_savings_points)) < 1e-4


def test_fair_scoring_breakdown_identity_violation_raises_validation_error() -> None:
    """Error path: Mismatched penalty sum raises ValidationError."""
    with pytest.raises(ValidationError, match="Scoring identity violated"):
        FairScoringBreakdownDTO(
            independent_error_count=1,
            cascading_fault_count=2,
            raw_penalty_points=10.0,
            deduplicated_penalty_points=6.0,
            dampened_savings_points=2.0,
        )


def test_fair_scoring_breakdown_negative_points_raises_validation_error() -> None:
    """Boundary test: Negative raw_penalty_points raises ValidationError."""
    with pytest.raises(ValidationError):
        FairScoringBreakdownDTO(
            independent_error_count=1,
            cascading_fault_count=2,
            raw_penalty_points=-1.0,
            deduplicated_penalty_points=0.0,
            dampened_savings_points=-1.0,
        )


def test_fair_scoring_breakdown_negative_counts_raises_validation_error() -> None:
    """Boundary test: Negative error count raises ValidationError."""
    with pytest.raises(ValidationError):
        FairScoringBreakdownDTO(
            independent_error_count=-1,
            cascading_fault_count=0,
            raw_penalty_points=0.0,
            deduplicated_penalty_points=0.0,
            dampened_savings_points=0.0,
        )


def test_step_output_dto_payload_accepts_causal_payload() -> None:
    """Positive test: StepOutputDTO accepts CausalGraphPayloadDTO with data_type='causal'."""
    node = CausalNodeDTO(node_id="n0", claim="Test claim", status=ExecutionStatus.PASSED)
    payload = CausalGraphPayloadDTO(nodes=[node])
    output = StepOutputDTO(
        step_id="stp_1111111111111111",
        block_id="blk_1111111111111111",
        data_type="causal",
        payload=payload,
    )
    assert output.data_type == "causal"
    assert isinstance(output.payload, CausalGraphPayloadDTO)
    assert len(output.payload.nodes) == 1


def test_causal_tda_fusion_result_dto_valid() -> None:
    """Positive test: Complete composite CausalTdaFusionResultDTO validates."""
    n0 = _create_sample_node("n0")
    n1 = _create_sample_node("n1")
    edge = CausalEdgeDTO(source_id="n0", target_id="n1", reasoning="Direct cascade")
    graph = CausalGraphPayloadDTO(nodes=[n0, n1], edges=[edge], root_cause_node_ids=["n0"])

    diagnosis = CausalRootCauseDiagnosisDTO(
        failing_node_id="n1",
        root_cause_parent_id="n0",
        paragraph_ref="p2",
        explanation="Failed because n0 was invalid",
        penalty_points=2.5,
    )
    anti_fluff = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=1,
        logical_cohesion_score=0.92,
        detected_hollow_terms=["synergize"],
    )
    remediation = PrescriptiveRemediationDTO(
        target_node_id="n0",
        required_action="Provide verified source data for initial premise",
        unlocks_node_ids=["n1"],
        potential_score_impact=15.0,
    )
    scoring = FairScoringBreakdownDTO(
        independent_error_count=1,
        cascading_fault_count=1,
        raw_penalty_points=5.0,
        deduplicated_penalty_points=3.75,
        dampened_savings_points=1.25,
    )

    fusion = CausalTdaFusionResultDTO(
        graph=graph,
        root_cause_diagnoses=[diagnosis],
        anti_fluff_audit=anti_fluff,
        prescriptive_remediations=[remediation],
        fair_scoring=scoring,
    )
    assert fusion.graph.root_cause_node_ids == ["n0"]
    assert len(fusion.root_cause_diagnoses) == 1
    assert fusion.anti_fluff_audit.logical_cohesion_score == 0.92


def test_causal_dto_immutability_and_extra_forbidden() -> None:
    """Invariance test: All causal discovery DTOs enforce extra='forbid' and frozen=True."""
    node = _create_sample_node("n0")

    # Frozen enforcement
    with pytest.raises(ValidationError):
        node.claim = "Mutated claim"

    # Extra forbid enforcement
    with pytest.raises(ValidationError):
        CausalNodeDTO.model_validate(
            {
                "node_id": "n0",
                "claim": "Claim",
                "status": ExecutionStatus.PASSED,
                "unauthorized_key": "forbidden",
            }
        )
