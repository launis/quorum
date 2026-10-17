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
from backend_v2.models.enums import CausalRootCauseType, ExecutionStatus


def _create_sample_node(
    node_id: str, claim: str = "Sample claim", source_input_key: str | None = None
) -> CausalNodeDTO:
    """Helper creating a valid CausalNodeDTO."""
    return CausalNodeDTO(
        node_id=node_id,
        claim=claim,
        status=ExecutionStatus.PASSED,
        source_quote="Exact quote",
        paragraph_ref="p1",
        blame_parent_ids=[],
        dependent_child_ids=[],
        source_input_key=source_input_key,
    )


def _create_sample_payload(
    nodes: list[CausalNodeDTO],
    edges: list[CausalEdgeDTO] | None = None,
    root_cause_node_ids: list[str] | None = None,
    isolated_node_ids: list[str] | None = None,
    partition_node_ids: dict[str, list[str]] | None = None,
    edge_root_causes: list[str] | None = None,
) -> CausalGraphPayloadDTO:
    """Helper creating a valid CausalGraphPayloadDTO with all default collections supplied."""
    return CausalGraphPayloadDTO(
        nodes=nodes,
        edges=edges if edges is not None else [],
        root_cause_node_ids=root_cause_node_ids if root_cause_node_ids is not None else [],
        isolated_node_ids=isolated_node_ids if isolated_node_ids is not None else [],
        partition_node_ids=partition_node_ids if partition_node_ids is not None else {},
        edge_root_causes=edge_root_causes if edge_root_causes is not None else [],
    )


def test_causal_graph_payload_referential_integrity_valid() -> None:
    """Positive test: Valid referential integrity in CausalGraphPayloadDTO."""
    n0 = _create_sample_node("node_0")
    n1 = _create_sample_node("node_1")
    edge = CausalEdgeDTO(source_id="node_0", target_id="node_1", reasoning="Prerequisite")

    payload = _create_sample_payload(
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
        _create_sample_payload(nodes=[n0], edges=[edge])


def test_causal_graph_payload_dangling_edge_target_raises_validation_error() -> None:
    """Error path: Edge target_id referencing nonexistent node raises ValidationError."""
    n0 = _create_sample_node("node_0")
    edge = CausalEdgeDTO(source_id="node_0", target_id="node_999", reasoning="Missing target")

    with pytest.raises(ValidationError, match="Edge target_id 'node_999' does not exist in graph nodes"):
        _create_sample_payload(nodes=[n0], edges=[edge])


def test_causal_graph_payload_dangling_root_cause_raises_validation_error() -> None:
    """Error path: root_cause_node_ids referencing nonexistent node raises ValidationError."""
    n0 = _create_sample_node("node_0")

    with pytest.raises(ValidationError, match="Root cause node_id 'node_999' does not exist in graph nodes"):
        _create_sample_payload(nodes=[n0], root_cause_node_ids=["node_999"])


def test_causal_graph_payload_dangling_isolated_node_raises_validation_error() -> None:
    """Error path: isolated_node_ids referencing nonexistent node raises ValidationError."""
    n0 = _create_sample_node("node_0")

    with pytest.raises(ValidationError, match="Isolated node_id 'node_999' does not exist in graph nodes"):
        _create_sample_payload(nodes=[n0], isolated_node_ids=["node_999"])


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
    assert (
        abs(breakdown.raw_penalty_points - (breakdown.deduplicated_penalty_points + breakdown.dampened_savings_points))
        < 1e-4
    )


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
    node = _create_sample_node("n0")
    payload = _create_sample_payload(nodes=[node])
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
    graph = _create_sample_payload(nodes=[n0, n1], edges=[edge], root_cause_node_ids=["n0"])

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
    # Frozen and strict config enforcement
    node_config = CausalNodeDTO.model_config
    assert node_config["frozen"] is True
    assert node_config["strict"] is True
    assert node_config["extra"] == "forbid"

    graph_config = CausalGraphPayloadDTO.model_config
    assert graph_config["frozen"] is True
    assert graph_config["strict"] is True
    assert graph_config["extra"] == "forbid"

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


def test_causal_node_source_input_key_provenance() -> None:
    """Positive & boundary test: source_input_key propagates correctly on CausalNodeDTO."""
    node_with_key = _create_sample_node("n_prov", claim="Claim with provenance", source_input_key="technical_report")
    assert node_with_key.source_input_key == "technical_report"

    node_default = _create_sample_node("n_def")
    assert node_default.source_input_key is None


def test_causal_graph_payload_partition_node_ids_referential_integrity() -> None:
    """Positive & error paths: partition_node_ids referential integrity checks."""
    n0 = _create_sample_node("node_0")
    n1 = _create_sample_node("node_1")

    # Valid partitions
    payload = _create_sample_payload(
        nodes=[n0, n1],
        partition_node_ids={"doc_a": ["node_0"], "doc_b": ["node_1"]},
    )
    assert payload.partition_node_ids == {"doc_a": ["node_0"], "doc_b": ["node_1"]}

    # Error path: dangling node in partition
    with pytest.raises(ValidationError, match="Partition 'doc_c' references node_id 'node_missing'"):
        _create_sample_payload(
            nodes=[n0],
            partition_node_ids={"doc_c": ["node_missing"]},
        )


def test_causal_graph_payload_edge_root_causes_referential_integrity() -> None:
    """Positive & error paths: edge_root_causes referential integrity checks."""
    n0 = _create_sample_node("node_0")
    n1 = _create_sample_node("node_1")
    edge = CausalEdgeDTO(source_id="node_0", target_id="node_1", reasoning="Direct edge")

    # Valid edge root cause
    payload = _create_sample_payload(
        nodes=[n0, n1],
        edges=[edge],
        edge_root_causes=["node_0->node_1"],
    )
    assert payload.edge_root_causes == ["node_0->node_1"]

    # Error path: edge_root_causes referencing non-existent edge
    with pytest.raises(ValidationError, match="Edge root cause 'node_1->node_0' does not match any active edge"):
        _create_sample_payload(
            nodes=[n0, n1],
            edges=[edge],
            edge_root_causes=["node_1->node_0"],
        )


def test_causal_root_cause_diagnosis_root_cause_type() -> None:
    """Positive test: root_cause_type enum defaults and explicit assignment."""
    diag_default = CausalRootCauseDiagnosisDTO(
        failing_node_id="n1",
        root_cause_parent_id="n0",
        paragraph_ref="p1",
        explanation="Failure explanation",
        penalty_points=5.0,
    )
    assert diag_default.root_cause_type == CausalRootCauseType.NODE_FAILURE

    diag_warrant = CausalRootCauseDiagnosisDTO(
        failing_node_id="n1",
        root_cause_parent_id="n0",
        paragraph_ref="p1",
        explanation="Warrant failure",
        penalty_points=5.0,
        root_cause_type=CausalRootCauseType.WARRANT_GROUNDING_FAILURE,
    )
    assert diag_warrant.root_cause_type == CausalRootCauseType.WARRANT_GROUNDING_FAILURE


def test_causal_tda_fusion_result_total_deliverable_nodes() -> None:
    """Positive & boundary test: total_deliverable_nodes defaults to 0 and accepts non-negative integers."""
    n0 = _create_sample_node("n0")
    graph = _create_sample_payload(nodes=[n0])
    anti_fluff = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=1.0,
        detected_hollow_terms=[],
    )
    scoring = FairScoringBreakdownDTO(
        independent_error_count=0,
        cascading_fault_count=0,
        raw_penalty_points=0.0,
        deduplicated_penalty_points=0.0,
        dampened_savings_points=0.0,
    )

    fusion = CausalTdaFusionResultDTO(
        graph=graph,
        root_cause_diagnoses=[],
        anti_fluff_audit=anti_fluff,
        prescriptive_remediations=[],
        fair_scoring=scoring,
        total_deliverable_nodes=5,
    )
    assert fusion.total_deliverable_nodes == 5

    # Boundary test: negative value raises ValidationError
    with pytest.raises(ValidationError):
        CausalTdaFusionResultDTO(
            graph=graph,
            root_cause_diagnoses=[],
            anti_fluff_audit=anti_fluff,
            prescriptive_remediations=[],
            fair_scoring=scoring,
            total_deliverable_nodes=-1,
        )
