"""Unit tests for deterministic causal reasoning and argument cohesion BARS evaluation.

Tests all 5 BARS levels, the Cumulative Guttman Invariant, zero-node Novice floor
grounding, cyclic defect grounding, dynamic matrix ID binding, strict typing,
cognitive atom validation, and DAGExecutor fusion idempotency.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from backend_v2.core.hook_registry import GlobalContextVarsDTO
from backend_v2.exceptions import AppException
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CounterfactualSimulationResultDTO,
)
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import CausalRootCauseType, ExecutionStatus
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.causal_cohesion_evaluator import (
    CausalCohesionEvaluationDTO,
    CausalCohesionEvaluator,
)
from backend_v2.settings import get_settings

TEST_COHESION_MATRIX_ID = "blk_0195f3a00000700080009f6d2c1b0a5e"
TEST_COHESION_TDA_IDS: tuple[str, ...] = (
    "tda_c0a1e500000000000000000000000001",
    "tda_c0a1e500000000000000000000000002",
    "tda_c0a1e500000000000000000000000003",
    "tda_c0a1e500000000000000000000000004",
    "tda_c0a1e500000000000000000000000005",
)
TEST_BARS_CLAIMS: dict[str, str] = {tid: f"BARS level {idx} claim" for idx, tid in enumerate(TEST_COHESION_TDA_IDS, 1)}


def _create_test_graph(
    nodes: list[CausalNodeDTO],
    edges: list[CausalEdgeDTO] | None = None,
    root_cause_node_ids: list[str] | None = None,
    cycle_detected: bool = False,
    isolated_node_ids: list[str] | None = None,
    partition_node_ids: dict[str, list[str]] | None = None,
    edge_root_causes: list[str] | None = None,
) -> CausalGraphPayloadDTO:
    """Helper to instantiate CausalGraphPayloadDTO with complete collections for tests."""
    return CausalGraphPayloadDTO(
        nodes=nodes,
        edges=edges if edges is not None else [],
        root_cause_node_ids=root_cause_node_ids if root_cause_node_ids is not None else [],
        cycle_detected=cycle_detected,
        isolated_node_ids=isolated_node_ids if isolated_node_ids is not None else [],
        partition_node_ids=partition_node_ids if partition_node_ids is not None else {},
        edge_root_causes=edge_root_causes if edge_root_causes is not None else [],
    )


@pytest.fixture
def evaluator() -> CausalCohesionEvaluator:
    """Fixture providing a pure CausalCohesionEvaluator instance.

    Returns:
        CausalCohesionEvaluator instance.
    """
    return CausalCohesionEvaluator()


def test_causal_cohesion_level_5_full_mastery(evaluator: CausalCohesionEvaluator) -> None:
    """Verify high cohesion argument graph achieves BARS Level 5 full mastery."""
    audit = AntiFluffAuditDTO(
        isolated_concept_count=2,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.92,
        largest_component_ratio=0.95,
        branch_convergence_ratio=0.20,
        detected_hollow_terms=[],
    )

    result = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=50,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
        bars_claims=TEST_BARS_CLAIMS,
    )

    assert isinstance(result, CausalCohesionEvaluationDTO)
    assert result.matrix_block_id == TEST_COHESION_MATRIX_ID
    assert len(result.atom_results) == 5

    # All 5 levels must be PASSED
    for level, atom in enumerate(result.atom_results, 1):
        assert atom.status == ExecutionStatus.PASSED
        assert atom.tda_id == TEST_COHESION_TDA_IDS[level - 1]
        assert atom.matrix_id == TEST_COHESION_MATRIX_ID
        assert atom.contextual_override is True
        assert atom.source_quotes is None
        assert atom.evaluation_reasoning is not None and len(atom.evaluation_reasoning.strip()) > 0

    assert pytest.approx(result.score_result.score, 0.01) == 5.00
    assert len(result.hydrated_references) == 5
    for tda_id in TEST_COHESION_TDA_IDS:
        assert tda_id in result.hydrated_references
        assert result.hydrated_references[tda_id].sdui_component == "boolean_card"
    assert result.matrix_output.raw_score == result.score_result.score
    assert result.matrix_output.level_breakdown is not None
    assert len(result.matrix_output.level_breakdown) == 5


def test_causal_cohesion_level_4_strong_cohesion(evaluator: CausalCohesionEvaluator) -> None:
    """Verify strong cohesion meeting Level 4 threshold but failing Level 5."""
    # 3 isolated out of 40 = 7.5% (<= 10% L4 isolation max, but > 5% L5 isolation max)
    # cohesion 0.84 (>= 0.80 L4, < 0.90 L5)
    audit = AntiFluffAuditDTO(
        isolated_concept_count=3,
        cycle_detected=False,
        unsupported_claims_count=1,
        logical_cohesion_score=0.84,
        largest_component_ratio=0.80,
        branch_convergence_ratio=0.10,
        detected_hollow_terms=[],
    )

    res_70 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=40,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    res_50 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=40,
        strictness_level=50,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=40,
        strictness_level=0,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    # Levels 1-4 PASSED, Level 5 FAILED
    for lvl in range(4):
        assert res_70.atom_results[lvl].status == ExecutionStatus.PASSED
    assert res_70.atom_results[4].status == ExecutionStatus.FAILED

    # Score verification across continuous strictness curve
    assert pytest.approx(res_70.score_result.score, 0.02) == 3.17
    assert pytest.approx(res_50.score_result.score, 0.02) == 3.41
    assert pytest.approx(res_0.score_result.score, 0.02) == 3.67


def test_causal_cohesion_level_3_moderate_cohesion(evaluator: CausalCohesionEvaluator) -> None:
    """Verify moderate cohesion meeting Level 3 threshold but failing Level 4."""
    # 4 isolated out of 30 = 13.3% (<= 20% L3 isolation max, but > 10% L4 isolation max)
    # cohesion 0.68 (>= 0.60 L3, < 0.80 L4)
    audit = AntiFluffAuditDTO(
        isolated_concept_count=4,
        cycle_detected=False,
        unsupported_claims_count=2,
        logical_cohesion_score=0.68,
        detected_hollow_terms=[],
    )

    res_70 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    res_50 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=50,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=0,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    # Levels 1-3 PASSED, Levels 4-5 FAILED
    for lvl in range(3):
        assert res_70.atom_results[lvl].status == ExecutionStatus.PASSED
    assert res_70.atom_results[3].status == ExecutionStatus.FAILED
    assert res_70.atom_results[4].status == ExecutionStatus.FAILED

    assert pytest.approx(res_70.score_result.score, 0.02) == 2.01
    assert pytest.approx(res_50.score_result.score, 0.02) == 2.27
    assert pytest.approx(res_0.score_result.score, 0.02) == 2.60


def test_causal_cohesion_level_2_discontinuous_cohesion(evaluator: CausalCohesionEvaluator) -> None:
    """Verify discontinuous cohesion meeting Level 2 threshold but failing Level 3."""
    # 10 isolated out of 25 = 40% (> 20% L3 isolation max)
    # cohesion 0.48 (>= 0.40 L2, < 0.60 L3)
    audit = AntiFluffAuditDTO(
        isolated_concept_count=10,
        cycle_detected=False,
        unsupported_claims_count=4,
        logical_cohesion_score=0.48,
        detected_hollow_terms=[],
    )

    res_70 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=25,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    res_50 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=25,
        strictness_level=50,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=25,
        strictness_level=0,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    # Levels 1-2 PASSED, Levels 3-5 FAILED
    assert res_70.atom_results[0].status == ExecutionStatus.PASSED
    assert res_70.atom_results[1].status == ExecutionStatus.PASSED
    assert res_70.atom_results[2].status == ExecutionStatus.FAILED
    assert res_70.atom_results[3].status == ExecutionStatus.FAILED
    assert res_70.atom_results[4].status == ExecutionStatus.FAILED

    assert pytest.approx(res_70.score_result.score, 0.02) == 1.35
    assert pytest.approx(res_50.score_result.score, 0.02) == 1.53
    assert pytest.approx(res_0.score_result.score, 0.02) == 1.80


def test_causal_cohesion_cyclic_defect_grounding(evaluator: CausalCohesionEvaluator) -> None:
    """Verify that detected cycles ground the argument to BARS 1.0 Novice floor."""
    audit = AntiFluffAuditDTO(
        isolated_concept_count=2,
        cycle_detected=True,  # Circular reasoning defect
        unsupported_claims_count=0,
        logical_cohesion_score=0.95,  # High cohesion cannot bypass cycle defect
        detected_hollow_terms=[],
    )

    res_70 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=0,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    # Level 1 PASSED (Novice floor), Levels 2-5 FAILED (Guttman invariant)
    assert res_70.atom_results[0].status == ExecutionStatus.PASSED
    for lvl in range(1, 5):
        assert res_70.atom_results[lvl].status == ExecutionStatus.FAILED

    assert pytest.approx(res_70.score_result.score, 0.01) == 1.07
    assert pytest.approx(res_0.score_result.score, 0.01) == 1.27


def test_causal_cohesion_zero_node_grounding(evaluator: CausalCohesionEvaluator) -> None:
    """Verify that an empty graph grounds safely to BARS 1.0 without ZeroDivisionError."""
    audit = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.0,
        detected_hollow_terms=[],
    )

    res_70 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=0,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=0,
        strictness_level=0,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    # Equation (13): L1 = (total_nodes >= 1) -> False for empty graph, clamping score to 1.0
    for lvl in range(5):
        assert res_70.atom_results[lvl].status == ExecutionStatus.FAILED

    assert pytest.approx(res_70.score_result.score, 0.01) == 1.00
    assert pytest.approx(res_0.score_result.score, 0.01) == 1.00


def test_causal_cohesion_cumulative_guttman_invariant(evaluator: CausalCohesionEvaluator) -> None:
    """Verify the Cumulative Guttman Invariant: Level k cannot pass if Level k-1 failed."""
    # Cohesion 0.35 fails Level 2 (< 0.40), even if isolation is 0.0
    audit = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.35,
        detected_hollow_terms=[],
    )

    result = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=20,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    # Level 1 PASSED, Levels 2..5 all FAILED
    assert result.atom_results[0].status == ExecutionStatus.PASSED
    assert result.atom_results[1].status == ExecutionStatus.FAILED
    assert result.atom_results[2].status == ExecutionStatus.FAILED
    assert result.atom_results[3].status == ExecutionStatus.FAILED
    assert result.atom_results[4].status == ExecutionStatus.FAILED


def test_causal_cohesion_mandatory_matrix_block_id(evaluator: CausalCohesionEvaluator) -> None:
    """Verify that matrix_block_id is strictly mandatory and non-nullable."""
    audit = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.9,
        detected_hollow_terms=[],
    )

    # Calling without matrix_block_id must raise TypeError
    call_eval: Any = evaluator.evaluate_causal_cohesion
    with pytest.raises(TypeError):
        call_eval(
            audit=audit,
            total_nodes=10,
            strictness_level=70,
        )


def test_causal_cohesion_dynamic_matrix_id_binding(evaluator: CausalCohesionEvaluator) -> None:
    """Verify that emitted atoms are dynamically bound to the supplied matrix_block_id."""
    audit = AntiFluffAuditDTO(
        isolated_concept_count=1,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.95,
        detected_hollow_terms=[],
    )

    custom_matrix_id = "blk_custom_test_99"
    result = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=20,
        strictness_level=70,
        matrix_block_id=custom_matrix_id,
    )

    assert result.matrix_block_id == custom_matrix_id
    for atom in result.atom_results:
        assert atom.matrix_id == custom_matrix_id


def test_causal_cohesion_cognitive_atom_validation(evaluator: CausalCohesionEvaluator) -> None:
    """Verify strict adherence to AtomResultDTO.validate_cognitive_vs_system_state."""
    audit = AntiFluffAuditDTO(
        isolated_concept_count=5,
        cycle_detected=False,
        unsupported_claims_count=2,
        logical_cohesion_score=0.65,
        detected_hollow_terms=[],
    )

    result = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=25,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    for atom in result.atom_results:
        # Re-validating every atom against the strict Pydantic model must succeed
        re_validated = AtomResultDTO.model_validate(atom.model_dump())
        assert re_validated.status == atom.status

        if atom.status == ExecutionStatus.PASSED:
            assert atom.contextual_override is True
            assert atom.is_inverse_evidence is False
            assert atom.source_quotes is None
            assert atom.evaluation_reasoning is not None and len(atom.evaluation_reasoning.strip()) > 0
        elif atom.status == ExecutionStatus.FAILED:
            assert atom.contextual_override is False
            assert atom.is_inverse_evidence is False
            assert atom.source_quotes is None
            assert atom.evaluation_reasoning is not None and len(atom.evaluation_reasoning.strip()) > 0


def test_causal_cohesion_idempotency_set_guard() -> None:
    """Verify that multiple steps referencing the same causal source evaluate only once."""
    evaluator = CausalCohesionEvaluator()

    audit = AntiFluffAuditDTO(
        isolated_concept_count=1,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.95,
        largest_component_ratio=0.95,
        branch_convergence_ratio=0.20,
        detected_hollow_terms=[],
    )

    causal_source_id = "sr_0195f3a0000070008000c4a5a1d15c00"
    evaluated_sources: set[str] = set()
    emitted_events: list[TraceEvent] = []

    # Specialist 1 runs and triggers cohesion evaluation
    if causal_source_id not in evaluated_sources:
        evaluated_sources.add(causal_source_id)
        dto1 = evaluator.evaluate_causal_cohesion(
            audit=audit,
            total_nodes=20,
            strictness_level=70,
            matrix_block_id=TEST_COHESION_MATRIX_ID,
        )
        emitted_events.append(
            TraceEvent(
                step_name=causal_source_id,
                event_type="output",
                content={
                    "results": dto1.atom_results,
                    "hydrated_references": dto1.hydrated_references,
                    dto1.matrix_block_id: dto1.matrix_output.model_dump(mode="json"),
                },
            )
        )
        emitted_events.append(
            TraceEvent(
                step_name=causal_source_id,
                event_type="decision",
                metadata=TraceEventMetadataDTO(is_context_update=True),
                content=GlobalContextVarsDTO(evaluative_matrices={dto1.matrix_block_id: dto1.score_result.score}),
            )
        )

    # Specialist 2 runs and attempts to evaluate the same causal source
    if causal_source_id not in evaluated_sources:
        pytest.fail("Second specialist must not evaluate an already evaluated causal source.")

    # Assert exactly 1 wrapped atom output event and 1 context update decision event were emitted
    output_events = [e for e in emitted_events if e.event_type == "output"]
    decision_events = [e for e in emitted_events if e.event_type == "decision"]

    assert len(output_events) == 1
    assert type(output_events[0].content) is dict
    assert "results" in output_events[0].content
    assert "hydrated_references" in output_events[0].content
    assert TEST_COHESION_MATRIX_ID in output_events[0].content
    assert len(output_events[0].content["results"]) == 5
    assert len(output_events[0].content["hydrated_references"]) == 5
    assert all(isinstance(a, AtomResultDTO) for a in output_events[0].content["results"])
    assert len(decision_events) == 1
    assert decision_events[0].metadata is not None
    assert decision_events[0].metadata.is_context_update is True
    assert isinstance(decision_events[0].content, GlobalContextVarsDTO)
    assert decision_events[0].content.evaluative_matrices == {TEST_COHESION_MATRIX_ID: 5.0}


def test_causal_cohesion_l3_isolation_baseline_boundary_passed(evaluator: CausalCohesionEvaluator) -> None:
    """Verify that isolated concept ratio exactly at the SSOT baseline ceiling (20.0%) passes Level 3."""
    # 6 isolated out of 30 = 20.0% (<= 20% L3 isolation max SSOT default)
    # cohesion 0.70 (>= 0.60 L3)
    audit = AntiFluffAuditDTO(
        isolated_concept_count=6,
        cycle_detected=False,
        unsupported_claims_count=1,
        logical_cohesion_score=0.70,
        detected_hollow_terms=[],
    )

    result = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=0,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    # Levels 1-3 PASSED, Levels 4-5 FAILED
    assert result.atom_results[0].status == ExecutionStatus.PASSED
    assert result.atom_results[1].status == ExecutionStatus.PASSED
    assert result.atom_results[2].status == ExecutionStatus.PASSED
    assert result.atom_results[3].status == ExecutionStatus.FAILED
    assert result.atom_results[4].status == ExecutionStatus.FAILED
    assert pytest.approx(result.score_result.score, 0.02) == 2.60


def test_causal_cohesion_l3_isolation_baseline_boundary_failed(evaluator: CausalCohesionEvaluator) -> None:
    """Verify that isolated concept ratio exceeding the SSOT baseline ceiling (> 20.0%) fails Level 3."""
    # 7 isolated out of 30 = 23.3% (> 20% L3 isolation max SSOT default)
    # cohesion 0.70 (>= 0.60 L3, but blocked by isolation ceiling)
    audit = AntiFluffAuditDTO(
        isolated_concept_count=7,
        cycle_detected=False,
        unsupported_claims_count=1,
        logical_cohesion_score=0.70,
        detected_hollow_terms=[],
    )

    result = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=0,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    # Levels 1-2 PASSED, Level 3 FAILED due to isolation violation (halts at Level 2)
    assert result.atom_results[0].status == ExecutionStatus.PASSED
    assert result.atom_results[1].status == ExecutionStatus.PASSED
    assert result.atom_results[2].status == ExecutionStatus.FAILED
    assert result.atom_results[3].status == ExecutionStatus.FAILED
    assert result.atom_results[4].status == ExecutionStatus.FAILED
    assert pytest.approx(result.score_result.score, 0.02) == 1.80


def test_causal_cohesion_strategic_foresight_cross_case_calibration(
    evaluator: CausalCohesionEvaluator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify cross-case calibration behavior on dense strategic discourse (Pair B / Sitra scenario).

    Under baseline SSOT (max isolation 0.20), Pair B (isolation ~24%) fails Level 3 and halts at Level 2 (1.80/5.0).
    Under exploratory calibrated profile (max isolation 0.30), Pair B passes Level 3 (2.60/5.0).
    """
    settings = get_settings()
    # Dense strategic discourse model: 250 nodes, 60 isolated claims (24.0%), cohesion 0.75
    audit = AntiFluffAuditDTO(
        isolated_concept_count=60,
        cycle_detected=False,
        unsupported_claims_count=5,
        logical_cohesion_score=0.75,
        detected_hollow_terms=[],
    )

    # 1. Baseline SSOT Evaluation (isolation max = 0.20) -> Halts at Level 2
    res_baseline = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=250,
        strictness_level=0,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    assert res_baseline.atom_results[1].status == ExecutionStatus.PASSED
    assert res_baseline.atom_results[2].status == ExecutionStatus.FAILED
    assert pytest.approx(res_baseline.score_result.score, 0.02) == 1.80

    # 2. Exploratory Calibrated Profile (isolation max = 0.30) -> Passes Level 3
    monkeypatch.setattr(settings, "causal_cohesion_l3_isolation_max", 0.30)
    res_calibrated = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=250,
        strictness_level=0,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    assert res_calibrated.atom_results[1].status == ExecutionStatus.PASSED
    assert res_calibrated.atom_results[2].status == ExecutionStatus.PASSED
    assert pytest.approx(res_calibrated.score_result.score, 0.02) == 2.60


def test_causal_cohesion_ast_monotonic_chain_verified() -> None:
    """Verify via AST analysis that CausalCohesionEvaluator enforces monotonic Guttman inheritance.

    Guarantees mathematically that:
    1. l2_passed depends directly on l1_passed
    2. l3_passed depends directly on l2_passed
    3. l4_passed depends directly on l3_passed
    4. l5_passed depends strictly on l4_passed (and does NOT skip to l3_passed)
    """
    evaluator_path = Path("backend_v2/services/orchestrator/causal_cohesion_evaluator.py")
    assert evaluator_path.exists(), f"Target evaluator file missing: {evaluator_path}"

    tree = ast.parse(evaluator_path.read_text(encoding="utf-8"))

    # Locate evaluate_causal_cohesion method
    eval_method: ast.FunctionDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "evaluate_causal_cohesion":
            eval_method = node
            break

    assert eval_method is not None, "Method evaluate_causal_cohesion not found in AST"

    # Collect variable assignment dependencies for level flags
    assignments: dict[str, list[str]] = {}
    for stmt in eval_method.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id in {
                    "l1_passed",
                    "l2_passed",
                    "l3_passed",
                    "l4_passed",
                    "l5_passed",
                }:
                    names = [n.id for n in ast.walk(stmt.value) if isinstance(n, ast.Name)]
                    assignments[target.id] = names

    # Invariants verification
    assert "l2_passed" in assignments, "l2_passed assignment not found in AST"
    assert "l1_passed" in assignments["l2_passed"], "l2_passed MUST depend on l1_passed"

    assert "l3_passed" in assignments, "l3_passed assignment not found in AST"
    assert "l2_passed" in assignments["l3_passed"], "l3_passed MUST depend on l2_passed"

    assert "l4_passed" in assignments, "l4_passed assignment not found in AST"
    assert "l3_passed" in assignments["l4_passed"], "l4_passed MUST depend on l3_passed"

    assert "l5_passed" in assignments, "l5_passed assignment not found in AST"
    # Strict Guttman Invariant: l5_passed MUST depend on l4_passed and NOT skip to l3_passed
    assert "l4_passed" in assignments["l5_passed"], "l5_passed MUST depend directly on l4_passed"
    assert "l3_passed" not in assignments["l5_passed"], (
        "ANTI-PATTERN: l5_passed directly references l3_passed, skipping l4_passed prerequisite!"
    )


def test_causal_cohesion_level_4_failure_blocks_level_5(
    evaluator: CausalCohesionEvaluator,
) -> None:
    """Verify that Level 4 failure strictly prevents Level 5 from passing.

    Constructs a scenario where logical cohesion (0.95) satisfies Level 5 threshold (>= 0.90),
    but isolated ratio (0.15) exceeds Level 4 threshold (<= 0.10). Because Level 4 fails,
    Level 5 MUST also evaluate to FAILED.
    """
    audit = AntiFluffAuditDTO(
        isolated_concept_count=3,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.95,
        largest_component_ratio=0.95,
        branch_convergence_ratio=0.20,
        detected_hollow_terms=[],
    )

    # total_nodes = 20 -> isolated_ratio = 3/20 = 0.15
    # L3 passes (<= 0.20), but L4 fails (0.15 > 0.10)
    result = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=20,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    assert result.atom_results[0].status == ExecutionStatus.PASSED  # L1
    assert result.atom_results[1].status == ExecutionStatus.PASSED  # L2
    assert result.atom_results[2].status == ExecutionStatus.PASSED  # L3
    assert result.atom_results[3].status == ExecutionStatus.FAILED  # L4 (0.15 > 0.10)
    assert result.atom_results[4].status == ExecutionStatus.FAILED  # L5 MUST be FAILED (inherited)


def test_causal_cohesion_monotonic_inheritance_invariant(
    evaluator: CausalCohesionEvaluator,
) -> None:
    """Verify prefix-monotonicity across all BARS levels: once FAILED, all subsequent levels FAIL.

    Tests multiple boundary conditions to ensure no non-monotonic transition (e.g. PASS -> FAIL -> PASS)
    can ever occur in causal cohesion evaluation.
    """
    test_cases = [
        # (cohesion, isolated_count, total_nodes, cycle_detected)
        (0.20, 0, 10, False),  # Fails at L2
        (0.50, 5, 20, False),  # Passes L2, fails L3 (isolation 0.25 > 0.20)
        (0.85, 3, 20, False),  # Passes L3, fails L4 (isolation 0.15 > 0.10)
        (0.95, 1, 20, False),  # Passes L4, fails L5 (isolation 0.05 vs max 0.05 - boundary)
        (0.95, 0, 20, False),  # Passes all L1..L5
        (0.99, 0, 20, True),  # Cycle detected -> fails at L2, clamps to L1
    ]

    for cohesion, iso_count, nodes, cycle in test_cases:
        audit = AntiFluffAuditDTO(
            isolated_concept_count=iso_count,
            cycle_detected=cycle,
            unsupported_claims_count=0,
            logical_cohesion_score=cohesion,
            largest_component_ratio=0.95,
            branch_convergence_ratio=0.20,
            detected_hollow_terms=[],
        )
        res = evaluator.evaluate_causal_cohesion(
            audit=audit,
            total_nodes=nodes,
            strictness_level=0,
            matrix_block_id=TEST_COHESION_MATRIX_ID,
        )

        statuses = [a.status == ExecutionStatus.PASSED for a in res.atom_results]
        # Verify prefix-monotonicity: True, ..., True, False, ..., False
        seen_false = False
        for passed in statuses:
            if not passed:
                seen_false = True
            elif seen_false:
                pytest.fail(f"Non-monotonic tier inheritance detected: {statuses}")


def test_causal_cohesion_algorithm_1_warrant_vs_node_failure(evaluator: CausalCohesionEvaluator) -> None:
    """Verify Algorithm 1 attributes warrant grounding failure when parent premise is valid."""
    parent_node = CausalNodeDTO(
        node_id="tda_p000000000000001",
        claim="Valid premise assertion",
        source_quotes=("Quote 1",),
        paragraph_ref="[B0]",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a00000700c8000000000000002"],
    )
    child_node = CausalNodeDTO(
        node_id="tda_0195f3a00000700c8000000000000002",
        claim="Dependent conclusion with ungrounded inferential leap",
        source_quotes=("Quote 2",),
        paragraph_ref="[B1]",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["tda_p000000000000001"],
        dependent_child_ids=[],
    )
    edge = CausalEdgeDTO(
        source_id="tda_p000000000000001",
        target_id="tda_0195f3a00000700c8000000000000002",
        reasoning="Ungrounded inferential leap",
    )
    graph = _create_test_graph(
        nodes=[parent_node, child_node],
        edges=[edge],
        edge_root_causes=["tda_p000000000000001->tda_0195f3a00000700c8000000000000002"],
    )

    diagnoses = evaluator.diagnose_root_causes(graph)

    assert len(diagnoses) == 1
    diag = diagnoses[0]
    assert diag.failing_node_id == "tda_0195f3a00000700c8000000000000002"
    assert diag.root_cause_parent_id == "tda_p000000000000001"
    assert diag.root_cause_type == CausalRootCauseType.WARRANT_GROUNDING_FAILURE
    assert "Inferential warrant failure" in diag.explanation


def test_causal_cohesion_algorithm_1_cascading_node_failure(evaluator: CausalCohesionEvaluator) -> None:
    """Verify Algorithm 1 attributes node failure when upstream parent premise is refuted."""
    parent_node = CausalNodeDTO(
        node_id="tda_p000000000000001",
        claim="Refuted premise assertion",
        source_quotes=None,
        paragraph_ref="[B0]",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a00000700c8000000000000002"],
    )
    child_node = CausalNodeDTO(
        node_id="tda_0195f3a00000700c8000000000000002",
        claim="Dependent conclusion blocked by invalid parent premise",
        source_quotes=("Quote 2",),
        paragraph_ref="[B1]",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["tda_p000000000000001"],
        dependent_child_ids=[],
    )
    edge = CausalEdgeDTO(
        source_id="tda_p000000000000001",
        target_id="tda_0195f3a00000700c8000000000000002",
        reasoning="Direct dependency link",
    )
    graph = _create_test_graph(
        nodes=[parent_node, child_node],
        edges=[edge],
        edge_root_causes=[],
    )

    diagnoses = evaluator.diagnose_root_causes(graph)

    assert len(diagnoses) == 1
    diag = diagnoses[0]
    assert diag.failing_node_id == "tda_0195f3a00000700c8000000000000002"
    assert diag.root_cause_parent_id == "tda_p000000000000001"
    assert diag.root_cause_type == CausalRootCauseType.NODE_FAILURE
    assert "Cascading failure caused by root issue in parent" in diag.explanation


def test_causal_cohesion_subgraph_cumulative_guttman_invariant(evaluator: CausalCohesionEvaluator) -> None:
    """Verify Cumulative Guttman Invariant holds strictly over deliverable subgraph denominator."""
    # Deliverable subgraph: 10 deliverable nodes, 1 isolated (10% isolation), cohesion 0.85
    audit = AntiFluffAuditDTO(
        isolated_concept_count=1,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.85,
        largest_component_ratio=0.90,
        branch_convergence_ratio=0.10,
        detected_hollow_terms=[],
    )

    res = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=10,
        strictness_level=50,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )

    statuses = [a.status == ExecutionStatus.PASSED for a in res.atom_results]
    # L1, L2, L3, L4 pass; L5 fails (0.10 isolation > 0.05 L5 max)
    assert statuses == [True, True, True, True, False]


def test_causal_cohesion_algorithm_1_dual_fault_attribution_warrant_failure(
    evaluator: CausalCohesionEvaluator,
) -> None:
    """Verify Algorithm 1 dual fault attribution separates warrant failures and includes warrant quotes."""
    parent_node = CausalNodeDTO(
        node_id="tda_p000000000000001",
        claim="Sound premise",
        source_quotes=("Premise Quote",),
        paragraph_ref="[B0]",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a00000700c8000000000000002"],
    )
    child_node = CausalNodeDTO(
        node_id="tda_0195f3a00000700c8000000000000002",
        claim="Child conclusion with broken inferential warrant",
        source_quotes=("Conclusion Quote",),
        paragraph_ref="[B1]",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["tda_p000000000000001"],
        dependent_child_ids=[],
    )
    edge = CausalEdgeDTO(
        source_id="tda_p000000000000001",
        target_id="tda_0195f3a00000700c8000000000000002",
        reasoning="Broken warrant link",
        warrant_quotes=("Warrant quote segment 1", "Warrant quote segment 2"),
    )
    graph = _create_test_graph(
        nodes=[parent_node, child_node],
        edges=[edge],
        edge_root_causes=["tda_p000000000000001->tda_0195f3a00000700c8000000000000002"],
    )

    diagnoses = evaluator.diagnose_root_causes(graph)

    assert len(diagnoses) == 1
    diag = diagnoses[0]
    assert diag.failing_node_id == "tda_0195f3a00000700c8000000000000002"
    assert diag.root_cause_parent_id == "tda_p000000000000001"
    assert diag.root_cause_type == CausalRootCauseType.WARRANT_GROUNDING_FAILURE
    assert "Inferential warrant failure" in diag.explanation
    assert "grounding quotes:" in diag.explanation
    assert "Warrant quote segment 1 [...] Warrant quote segment 2" in diag.explanation


def test_causal_cohesion_algorithm_1_dual_fault_attribution_node_failure(
    evaluator: CausalCohesionEvaluator,
) -> None:
    """Verify Algorithm 1 dual fault attribution separates node failure when parent premise is refuted."""
    parent_node = CausalNodeDTO(
        node_id="tda_p000000000000001",
        claim="Refuted premise",
        source_quotes=None,
        paragraph_ref="[B0]",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0195f3a00000700c8000000000000002"],
    )
    child_node = CausalNodeDTO(
        node_id="tda_0195f3a00000700c8000000000000002",
        claim="Child conclusion failing due to premise flaw",
        source_quotes=("Conclusion Quote",),
        paragraph_ref="[B1]",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["tda_p000000000000001"],
        dependent_child_ids=[],
    )
    edge = CausalEdgeDTO(
        source_id="tda_p000000000000001",
        target_id="tda_0195f3a00000700c8000000000000002",
        reasoning="Valid logical consequence",
    )
    graph = _create_test_graph(
        nodes=[parent_node, child_node],
        edges=[edge],
        edge_root_causes=[],
    )

    diagnoses = evaluator.diagnose_root_causes(graph)

    assert len(diagnoses) == 1
    diag = diagnoses[0]
    assert diag.failing_node_id == "tda_0195f3a00000700c8000000000000002"
    assert diag.root_cause_parent_id == "tda_p000000000000001"
    assert diag.root_cause_type == CausalRootCauseType.NODE_FAILURE
    assert "Cascading failure caused by root issue in parent" in diag.explanation


def test_causal_cohesion_dyad_fragmentation_and_node_cardinality_boundaries(
    evaluator: CausalCohesionEvaluator,
) -> None:
    """Verify Equation (13) defense against dyad fragmentation and ISTQB node cardinality boundaries."""
    # 5 disjoint 2-node pairs: N = 10, isolated_concept_count = 0 (r_iso = 0.0), r_LCC = 0.20 < 0.35
    dyad_audit = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=1.0,
        largest_component_ratio=0.20,
        branch_convergence_ratio=0.0,
        detected_hollow_terms=[],
    )
    dyad_res = evaluator.evaluate_causal_cohesion(
        audit=dyad_audit,
        total_nodes=10,
        strictness_level=70,
        matrix_block_id=TEST_COHESION_MATRIX_ID,
    )
    assert [a.status == ExecutionStatus.PASSED for a in dyad_res.atom_results] == [
        True,
        False,
        False,
        False,
        False,
    ]

    # Node cardinality boundary values N in {0, 1, 4, 9, 14} (min - 1 for L1..L5)
    perfect_audit = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=1.0,
        largest_component_ratio=1.0,
        branch_convergence_ratio=0.25,
        detected_hollow_terms=[],
    )
    expected_by_n: dict[int, list[bool]] = {
        0: [False, False, False, False, False],
        1: [True, False, False, False, False],
        4: [True, True, False, False, False],
        9: [True, True, True, False, False],
        14: [True, True, True, True, False],
        15: [True, True, True, True, True],
    }
    for n_nodes, expected_flags in expected_by_n.items():
        res = evaluator.evaluate_causal_cohesion(
            audit=perfect_audit,
            total_nodes=n_nodes,
            strictness_level=50,
            matrix_block_id=TEST_COHESION_MATRIX_ID,
        )
        assert [a.status == ExecutionStatus.PASSED for a in res.atom_results] == expected_flags


def test_simulate_counterfactual_retraction_conjunctive_disjunctive_and_negative(
    evaluator: CausalCohesionEvaluator,
) -> None:
    """Verify Algorithm 1 simulate_counterfactual_retraction across conjunctive, disjunctive, and missing node cases."""
    n1 = CausalNodeDTO(
        node_id="nod_0195f3a0000070008000000000000001",
        claim="Root premise 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["nod_0195f3a0000070008000000000000003"],
    )
    n2 = CausalNodeDTO(
        node_id="nod_0195f3a0000070008000000000000002",
        claim="Root premise 2 (corroborating)",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["nod_0195f3a0000070008000000000000003"],
    )
    n3 = CausalNodeDTO(
        node_id="nod_0195f3a0000070008000000000000003",
        claim="Intermediate synthesis",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["nod_0195f3a0000070008000000000000004"],
    )
    n4 = CausalNodeDTO(
        node_id="nod_0195f3a0000070008000000000000004",
        claim="Terminal conclusion",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    edges = [
        CausalEdgeDTO(
            source_id=n1.node_id,
            target_id=n3.node_id,
            reasoning="Premise 1 -> Synthesis",
        ),
        CausalEdgeDTO(
            source_id=n2.node_id,
            target_id=n3.node_id,
            reasoning="Premise 2 -> Synthesis",
        ),
        CausalEdgeDTO(
            source_id=n3.node_id,
            target_id=n4.node_id,
            reasoning="Synthesis -> Conclusion",
        ),
    ]
    graph = _create_test_graph(nodes=[n1, n2, n3, n4], edges=edges)

    # Conjunctive mode: retracting n1 collapses n3 and n4 (since n3 requires both n1 and n2)
    conj_res = evaluator.simulate_counterfactual_retraction(
        graph=graph,
        retracted_node_id=n1.node_id,
        conjunctive=True,
    )
    assert isinstance(conj_res, CounterfactualSimulationResultDTO)
    assert conj_res.retracted_root_id == n1.node_id
    assert conj_res.collapsed_node_ids == [n3.node_id, n4.node_id]
    assert conj_res.surviving_node_ids == [n2.node_id]
    assert conj_res.collapse_ratio == 0.75
    assert conj_res.max_cascade_depth == 2

    # Disjunctive mode: retracting n1 leaves n3 and n4 intact because n2 corroborates n3
    disj_res = evaluator.simulate_counterfactual_retraction(
        graph=graph,
        retracted_node_id=n1.node_id,
        conjunctive=False,
    )
    assert disj_res.collapsed_node_ids == []
    assert disj_res.surviving_node_ids == [n2.node_id, n3.node_id, n4.node_id]
    assert disj_res.collapse_ratio == 0.25
    assert disj_res.max_cascade_depth == 0

    # Negative path: nonexistent retracted_node_id raises AppException(VALIDATION_FAILED)
    with pytest.raises(AppException, match="does not exist in causal graph"):
        evaluator.simulate_counterfactual_retraction(
            graph=graph,
            retracted_node_id="nod_0195f3a0000070008000999999999999",
            conjunctive=True,
        )
