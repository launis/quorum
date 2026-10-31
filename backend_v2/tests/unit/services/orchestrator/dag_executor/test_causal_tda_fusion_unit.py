"""Unit tests for backend_v2.services.orchestrator.dag_executor.causal_tda_fusion.

Covers transform_causal_nodes_to_atoms and compute_causal_tda_fusion_result across
positive, negative, and boundary partitions.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.proposition_graph import FalsifiedClaimMatch
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.models.dtos.atom_result import AtomResultDTO, ExtractedValueDTO
from backend_v2.models.dtos.causal_discovery import (
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    FairScoringBreakdownDTO,
)
from backend_v2.models.enums import DependencyRelationType, ExecutionStatus
from backend_v2.services.orchestrator.dag_executor.causal_tda_fusion import (
    compute_causal_tda_fusion_result,
    transform_causal_nodes_to_atoms,
)


def _make_graph(
    nodes: list[CausalNodeDTO],
    edges: list[CausalEdgeDTO] | None = None,
    root_cause_node_ids: list[str] | None = None,
    cycle_detected: bool = False,
    isolated_node_ids: list[str] | None = None,
    edge_root_causes: list[str] | None = None,
) -> CausalGraphPayloadDTO:
    """Build a validated CausalGraphPayloadDTO instance for unit testing.

    Args:
        nodes: List of causal nodes in the graph.
        edges: Optional list of directed causal edges.
        root_cause_node_ids: Optional list of root cause node identifiers.
        cycle_detected: Whether a cycle was detected in the graph.
        isolated_node_ids: Optional list of isolated node identifiers.
        edge_root_causes: Optional list of edge root cause keys.

    Returns:
        Validated CausalGraphPayloadDTO instance.
    """
    return CausalGraphPayloadDTO(
        nodes=nodes,
        edges=edges if edges is not None else [],
        root_cause_node_ids=root_cause_node_ids if root_cause_node_ids is not None else [],
        cycle_detected=cycle_detected,
        isolated_node_ids=isolated_node_ids if isolated_node_ids is not None else [],
        partition_node_ids={},
        edge_root_causes=edge_root_causes if edge_root_causes is not None else [],
    )


def test_transform_causal_nodes_to_atoms_empty_and_populated() -> None:
    """Verify transform_causal_nodes_to_atoms maps empty, populated, and nullable nodes."""
    assert transform_causal_nodes_to_atoms([]) == []

    nodes = [
        CausalNodeDTO(
            node_id="tda_0195f3a0000070008000000000000001",
            claim="First causal proposition.",
            source_quotes=("Quote A", "Quote B"),
            paragraph_ref="P1",
            status=ExecutionStatus.PASSED,
            blame_parent_ids=[],
            dependent_child_ids=[],
        ),
        CausalNodeDTO(
            node_id="tda_0195f3a0000070008000000000000002",
            claim="Second causal proposition without quotes.",
            source_quotes=None,
            paragraph_ref=None,
            status=ExecutionStatus.FAILED,
            blame_parent_ids=[],
            dependent_child_ids=[],
        ),
    ]

    atoms = transform_causal_nodes_to_atoms(nodes)
    assert len(atoms) == 2
    assert isinstance(atoms[0], FlattenedAtom)
    assert atoms[0].atom_id == "tda_0195f3a0000070008000000000000001"
    assert atoms[0].question == "First causal proposition."
    assert atoms[0].anchor_target == "P1"
    assert atoms[0].extraction_rule == "Quote A [...] Quote B"
    assert atoms[1].atom_id == "tda_0195f3a0000070008000000000000002"
    assert atoms[1].anchor_target == ""
    assert atoms[1].extraction_rule == ""


def test_compute_causal_tda_fusion_result_falsification_and_elevation() -> None:
    """Verify compute_causal_tda_fusion_result projects atom statuses, scores, and remediations."""
    node1 = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000001",
        claim="Foundational root claim",
        source_quotes=("Verbatim quote 1",),
        paragraph_ref="P1",
        status=ExecutionStatus.PASSED,
        tda_score=1.0,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a0000070008000000000000002"],
        source_input_key="deliverable_doc",
    )
    node2 = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000002",
        claim="Downstream dependent claim",
        source_quotes=("Verbatim quote 2",),
        paragraph_ref="P2",
        status=ExecutionStatus.FAILED,
        tda_score=1.0,
        blame_parent_ids=["tda_0195f3a0000070008000000000000001"],
        dependent_child_ids=[],
        source_input_key="deliverable_doc",
    )
    node3 = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000003",
        claim="Exogenous reference claim",
        source_quotes=None,
        paragraph_ref="P3",
        status=ExecutionStatus.PASSED,
        tda_score=3.0,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a0000070008000000000000002"],
        source_input_key="assignment_doc",
    )
    edges = [
        CausalEdgeDTO(
            source_id="tda_0195f3a0000070008000000000000001",
            target_id="tda_0195f3a0000070008000000000000002",
            reasoning="Direct causal link",
        ),
        CausalEdgeDTO(
            source_id="tda_0195f3a0000070008000000000000003",
            target_id="tda_0195f3a0000070008000000000000002",
            reasoning="Exogenous support link",
        ),
    ]
    graph = _make_graph(
        nodes=[node1, node2, node3],
        edges=edges,
        root_cause_node_ids=["tda_0195f3a0000070008000000000000001"],
        cycle_detected=False,
    )

    evaluated_atoms = [
        AtomResultDTO(
            tda_id="tda_0195f3a0000070008000000000000001",
            matrix_id="blk_0195f3a0000070018111222233334444",
            status=ExecutionStatus.FAILED,
            evaluation_reasoning="Falsified by TDA evaluation.",
            source_quotes=None,
            extensions={},
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        ),
        AtomResultDTO(
            tda_id="tda_0195f3a0000070008000000000000002",
            matrix_id=None,
            status=ExecutionStatus.PASSED,
            extracted_data=ExtractedValueDTO(value=5.0),
            evaluation_reasoning="Elevated by TDA evaluation.",
            source_quotes=("Verbatim quote 2",),
            extensions={},
            depends_on_tda_ids=[],
            short_circuit_reason_tda_ids=[],
        ),
    ]
    expected_inputs = [
        ExpectedInput(
            input_key="deliverable_doc",
            label=I18nText(translations={"en": "Deliverable"}),
            required=True,
            is_endorsed_deliverable=True,
            input_modes=["text"],
            description=I18nText(translations={"en": "Main deliverable"}),
        ),
        ExpectedInput(
            input_key="assignment_doc",
            label=I18nText(translations={"en": "Assignment"}),
            required=True,
            is_endorsed_deliverable=False,
            input_modes=["assignment"],
            description=I18nText(translations={"en": "Assignment brief"}),
        ),
    ]

    result = compute_causal_tda_fusion_result(
        graph=graph,
        evaluative_matrices={"blk_0195f3a0000070018111222233334444": 1.0},
        evaluated_atoms=evaluated_atoms,
        dampening_factor=0.5,
        expected_inputs=expected_inputs,
    )

    projected_by_id = {n.node_id: n for n in result.graph.nodes}
    assert projected_by_id["tda_0195f3a0000070008000000000000001"].status == ExecutionStatus.FAILED
    assert projected_by_id["tda_0195f3a0000070008000000000000001"].tda_score == 1.0
    assert projected_by_id["tda_0195f3a0000070008000000000000002"].status == ExecutionStatus.PASSED
    assert projected_by_id["tda_0195f3a0000070008000000000000002"].tda_score == 5.0
    assert projected_by_id["tda_0195f3a0000070008000000000000003"].status == ExecutionStatus.PASSED
    assert result.total_deliverable_nodes == 2
    assert len(result.prescriptive_remediations) == 1
    assert result.prescriptive_remediations[0].target_node_id == "tda_0195f3a0000070008000000000000001"
    assert result.prescriptive_remediations[0].unlocks_node_ids == ["tda_0195f3a0000070008000000000000002"]


def test_compute_causal_tda_fusion_result_fallback_deliverables_and_cycles() -> None:
    """Verify deliverable fallback filtering, empty deliverable cohesion, and cycle penalty."""
    node1 = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000001",
        claim="Isolated claim in secondary doc",
        source_quotes=None,
        paragraph_ref="P1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=["tda_0195f3a0000070008000000000000002"],
        dependent_child_ids=[],
        source_input_key="other_doc",
    )
    node2 = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000002",
        claim="Root cause node",
        source_quotes=("Quote",),
        paragraph_ref="P2",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a0000070008000000000000001"],
        source_input_key="other_doc",
    )
    graph_cycle = _make_graph(
        nodes=[node1, node2],
        edges=[
            CausalEdgeDTO(
                source_id="tda_0195f3a0000070008000000000000002",
                target_id="tda_0195f3a0000070008000000000000001",
                reasoning="Link",
            )
        ],
        root_cause_node_ids=["tda_0195f3a0000070008000000000000002"],
        cycle_detected=True,
    )

    fallback_inputs = [
        ExpectedInput(
            input_key="unmatched_deliverable",
            label=I18nText(translations={"en": "Unmatched"}),
            required=True,
            is_endorsed_deliverable=False,
            input_modes=["text"],
            description=I18nText(translations={"en": "Unmatched text input"}),
        )
    ]

    empty_deliverable_res = compute_causal_tda_fusion_result(
        graph=graph_cycle,
        expected_inputs=fallback_inputs,
    )
    assert empty_deliverable_res.total_deliverable_nodes == 0
    assert empty_deliverable_res.anti_fluff_audit.logical_cohesion_score == 1.0
    assert empty_deliverable_res.fair_scoring.independent_error_count == 1
    assert empty_deliverable_res.fair_scoring.cascading_fault_count == 1

    cycle_res = compute_causal_tda_fusion_result(graph=graph_cycle, expected_inputs=None)
    assert cycle_res.anti_fluff_audit.cycle_detected is True
    assert cycle_res.anti_fluff_audit.logical_cohesion_score == 0.5


def test_compute_causal_tda_fusion_result_degenerate_scale_raises_error() -> None:
    """Verify degenerate scoring breakdown or referential integrity violation raises ValidationError."""
    with pytest.raises(ValidationError, match="Scoring identity violated"):
        FairScoringBreakdownDTO(
            independent_error_count=1,
            cascading_fault_count=1,
            raw_penalty_points=2.0,
            deduplicated_penalty_points=2.0,
            dampened_savings_points=1.0,
        )

    with pytest.raises(ValidationError):
        _make_graph(
            nodes=[],
            root_cause_node_ids=["tda_0195f3a0000070008000000000000001"],
        )


def test_compute_causal_tda_fusion_topological_metrics_lcc_conv_and_steering() -> None:
    """Verify r_LCC, r_conv, and kappa_steer computation over disjoint components and dialogue steering."""
    d1 = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000001",
        claim="Deliverable root 1",
        source_quotes=("Quote 1",),
        paragraph_ref="P1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a0000070008000000000000003"],
        source_input_key="deliverable_doc",
    )
    d2 = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000002",
        claim="Deliverable root 2",
        source_quotes=("Quote 2",),
        paragraph_ref="P2",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a0000070008000000000000003"],
        source_input_key="deliverable_doc",
    )
    d3 = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000003",
        claim="Convergent synthesis node",
        source_quotes=("Quote 3",),
        paragraph_ref="P3",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
        source_input_key="deliverable_doc",
    )
    d4 = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000004",
        claim="Disjoint island node",
        source_quotes=("Quote 4",),
        paragraph_ref="P4",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
        source_input_key="deliverable_doc",
    )
    chat_node = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000005",
        claim="Dialogue steering directive",
        source_quotes=("Chat quote",),
        paragraph_ref="C1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a0000070008000000000000001"],
        source_input_key="chat_log",
    )
    edges = [
        CausalEdgeDTO(
            source_id="tda_0195f3a0000070008000000000000001",
            target_id="tda_0195f3a0000070008000000000000003",
            reasoning="Premise 1 to synthesis",
        ),
        CausalEdgeDTO(
            source_id="tda_0195f3a0000070008000000000000002",
            target_id="tda_0195f3a0000070008000000000000003",
            reasoning="Premise 2 to synthesis",
        ),
        CausalEdgeDTO(
            source_id="tda_0195f3a0000070008000000000000005",
            target_id="tda_0195f3a0000070008000000000000001",
            reasoning="Dialogue steers root 1",
        ),
    ]
    graph = _make_graph(nodes=[d1, d2, d3, d4, chat_node], edges=edges)
    expected_inputs = [
        ExpectedInput(
            input_key="deliverable_doc",
            label=I18nText(translations={"en": "Deliverable"}),
            required=True,
            is_endorsed_deliverable=True,
            input_modes=["text"],
            description=I18nText(translations={"en": "Deliverable"}),
        ),
        ExpectedInput(
            input_key="chat_log",
            label=I18nText(translations={"en": "Chat"}),
            required=True,
            is_chat_history=True,
            input_modes=["text"],
            description=I18nText(translations={"en": "Chat history"}),
        ),
    ]
    res = compute_causal_tda_fusion_result(graph=graph, expected_inputs=expected_inputs)
    # 4 deliverable nodes: {d1, d2, d3} form component of size 3 -> r_LCC = 3/4 = 0.75
    assert res.anti_fluff_audit.largest_component_ratio == 0.75
    # d3 has 2 incoming parents -> r_conv = 1/4 = 0.25
    assert res.anti_fluff_audit.branch_convergence_ratio == 0.25
    # Deliverable roots (zero internal in-degree): d1, d2, d4 (3 roots); d1 is steered by chat_node -> 1/3 = 0.3333
    assert res.anti_fluff_audit.steering_coupling_ratio == 0.3333

    single_res = compute_causal_tda_fusion_result(graph=_make_graph(nodes=[d1]))
    assert single_res.total_deliverable_nodes == 1
    assert single_res.anti_fluff_audit.largest_component_ratio == 1.0


def test_transform_causal_nodes_to_atoms_blank_fields_raise_app_exception() -> None:
    """Verify transform_causal_nodes_to_atoms raises AppException on blank node_id or claim."""
    blank_id_node = CausalNodeDTO(
        node_id="   ",
        claim="Valid proposition.",
        source_quotes=None,
        paragraph_ref=None,
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    with pytest.raises(AppException) as exc_info:
        transform_causal_nodes_to_atoms([blank_id_node])
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    blank_claim_node = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000001",
        claim="",
        source_quotes=None,
        paragraph_ref=None,
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    with pytest.raises(AppException) as claim_exc_info:
        transform_causal_nodes_to_atoms([blank_claim_node])
    assert claim_exc_info.value.details is not None
    assert claim_exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.parametrize("invalid_dampening", [-0.1, 1.5])
def test_compute_causal_tda_fusion_result_out_of_bounds_dampening_raises_app_exception(
    invalid_dampening: float,
) -> None:
    """Verify compute_causal_tda_fusion_result raises AppException when dampening_factor is out of bounds."""
    node = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000001",
        claim="Valid proposition.",
        source_quotes=("Quote",),
        paragraph_ref="P1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    graph = _make_graph(nodes=[node])
    with pytest.raises(AppException) as exc_info:
        compute_causal_tda_fusion_result(graph=graph, dampening_factor=invalid_dampening)
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_causal_tda_fusion_resolves_claim_texts_and_falsified_claims() -> None:
    """Verify compute_causal_tda_fusion_result populates root_cause_claim, failing_node_claim, and falsified_claims."""
    root_node = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000001",
        claim="Foundational parent premise is unsubstantiated.",
        source_quotes=("Quote 1",),
        paragraph_ref="P1",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a0000070008000000000000002"],
    )
    child_node = CausalNodeDTO(
        node_id="tda_0195f3a0000070008000000000000002",
        claim="Downstream architectural conclusion collapses.",
        source_quotes=("Quote 2",),
        paragraph_ref="P2",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["tda_0195f3a0000070008000000000000001"],
        dependent_child_ids=[],
    )
    edge = CausalEdgeDTO(
        source_id="tda_0195f3a0000070008000000000000001",
        target_id="tda_0195f3a0000070008000000000000002",
        reasoning="Parent premise warrants child conclusion.",
    )
    falsified_match = FalsifiedClaimMatch(
        rebuttal_id="nod_0195f3a0000070008000000000000011",
        invalidated_warrant_id="nod_0195f3a0000070008000000000000012",
        falsified_claim_id="nod_0195f3a0000070008000000000000013",
        rebuttal_confidence=0.92,
        claim_statement="In-memory serialization adds zero overhead.",
    )
    graph = _make_graph(
        nodes=[root_node, child_node],
        edges=[edge],
        root_cause_node_ids=["tda_0195f3a0000070008000000000000001"],
    )
    result = compute_causal_tda_fusion_result(
        graph=graph,
        falsified_claims=[falsified_match],
    )
    assert len(result.root_cause_diagnoses) == 1
    diag = result.root_cause_diagnoses[0]
    assert diag.root_cause_claim == "Foundational parent premise is unsubstantiated."
    assert diag.failing_node_claim == "Downstream architectural conclusion collapses."
    assert diag.warrant_relation == "warrants"
    assert len(result.falsified_claims) == 1
    assert result.falsified_claims[0].claim_statement == "In-memory serialization adds zero overhead."


def test_causal_root_cause_diagnosis_invalid_warrant_relation_raises_validation_error() -> None:
    """Verify CausalRootCauseDiagnosisDTO rejects invalid warrant_relation literal values."""
    with pytest.raises(ValidationError):
        CausalRootCauseDiagnosisDTO.model_validate(
            {
                "failing_node_id": "tda_0195f3a0000070008000000000000002",
                "root_cause_parent_id": "tda_0195f3a0000070008000000000000001",
                "paragraph_ref": "P2",
                "explanation": "Cascading failure.",
                "penalty_points": 1.0,
                "warrant_relation": "invalid_relation",
            }
        )
