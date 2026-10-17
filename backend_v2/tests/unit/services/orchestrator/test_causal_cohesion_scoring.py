"""Unit tests for deterministic causal reasoning and argument cohesion BARS evaluation.

Tests all 5 BARS levels, the Cumulative Guttman Invariant, zero-node Novice floor
grounding, cyclic defect grounding, dynamic matrix ID binding, strict typing,
cognitive atom validation, and DAGExecutor fusion idempotency.
"""

from __future__ import annotations

from typing import Any

import pytest

from backend_v2.core.hook_registry import GlobalContextVarsDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
)
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.causal_cohesion_evaluator import (
    CAUSAL_COHESION_TDA_IDS,
    CausalCohesionEvaluationDTO,
    CausalCohesionEvaluator,
)
from backend_v2.settings import get_settings


@pytest.fixture
def evaluator() -> CausalCohesionEvaluator:
    """Fixture providing a pure CausalCohesionEvaluator instance.

    Returns:
        CausalCohesionEvaluator instance.
    """
    return CausalCohesionEvaluator()


def test_causal_cohesion_level_5_full_mastery(evaluator: CausalCohesionEvaluator) -> None:
    """Verify high cohesion argument graph achieves BARS Level 5 full mastery."""
    settings = get_settings()
    audit = AntiFluffAuditDTO(
        isolated_concept_count=2,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.92,
        detected_hollow_terms=[],
    )

    result = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=50,
        strictness_level=70,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )

    assert isinstance(result, CausalCohesionEvaluationDTO)
    assert result.matrix_block_id == settings.causal_cohesion_matrix_block_id
    assert len(result.atom_results) == 5

    # All 5 levels must be PASSED
    for level, atom in enumerate(result.atom_results, 1):
        assert atom.status == ExecutionStatus.PASSED
        assert atom.tda_id == CAUSAL_COHESION_TDA_IDS[level - 1]
        assert atom.matrix_id == settings.causal_cohesion_matrix_block_id
        assert atom.contextual_override is True
        assert atom.source_quote is None
        assert atom.evaluation_reasoning is not None and len(atom.evaluation_reasoning.strip()) > 0

    assert pytest.approx(result.score_result.score, 0.01) == 5.00
    assert len(result.hydrated_references) == 5
    for tda_id in CAUSAL_COHESION_TDA_IDS:
        assert tda_id in result.hydrated_references
        assert result.hydrated_references[tda_id].sdui_component == "boolean_card"
    assert result.matrix_output.raw_score == result.score_result.score
    assert result.matrix_output.level_breakdown is not None
    assert len(result.matrix_output.level_breakdown) == 5


def test_causal_cohesion_level_4_strong_cohesion(evaluator: CausalCohesionEvaluator) -> None:
    """Verify strong cohesion meeting Level 4 threshold but failing Level 5."""
    settings = get_settings()
    # 3 isolated out of 40 = 7.5% (<= 10% L4 isolation max, but > 5% L5 isolation max)
    # cohesion 0.84 (>= 0.80 L4, < 0.90 L5)
    audit = AntiFluffAuditDTO(
        isolated_concept_count=3,
        cycle_detected=False,
        unsupported_claims_count=1,
        logical_cohesion_score=0.84,
        detected_hollow_terms=[],
    )

    res_70 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=40,
        strictness_level=70,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )
    res_50 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=40,
        strictness_level=50,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=40,
        strictness_level=0,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
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
    settings = get_settings()
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )
    res_50 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=50,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=0,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
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
    settings = get_settings()
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )
    res_50 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=25,
        strictness_level=50,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=25,
        strictness_level=0,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
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
    settings = get_settings()
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=30,
        strictness_level=0,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )

    # Level 1 PASSED (Novice floor), Levels 2-5 FAILED (Guttman invariant)
    assert res_70.atom_results[0].status == ExecutionStatus.PASSED
    for lvl in range(1, 5):
        assert res_70.atom_results[lvl].status == ExecutionStatus.FAILED

    assert pytest.approx(res_70.score_result.score, 0.01) == 1.07
    assert pytest.approx(res_0.score_result.score, 0.01) == 1.27


def test_causal_cohesion_zero_node_grounding(evaluator: CausalCohesionEvaluator) -> None:
    """Verify that an empty graph grounds safely to BARS 1.0 without ZeroDivisionError."""
    settings = get_settings()
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )
    res_0 = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=0,
        strictness_level=0,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )

    # Level 1 PASSED, Levels 2-5 FAILED
    assert res_70.atom_results[0].status == ExecutionStatus.PASSED
    for lvl in range(1, 5):
        assert res_70.atom_results[lvl].status == ExecutionStatus.FAILED

    assert pytest.approx(res_70.score_result.score, 0.01) == 1.07
    assert pytest.approx(res_0.score_result.score, 0.01) == 1.27


def test_causal_cohesion_cumulative_guttman_invariant(evaluator: CausalCohesionEvaluator) -> None:
    """Verify the Cumulative Guttman Invariant: Level k cannot pass if Level k-1 failed."""
    settings = get_settings()
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
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
    settings = get_settings()
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )

    for atom in result.atom_results:
        # Re-validating every atom against the strict Pydantic model must succeed
        re_validated = AtomResultDTO.model_validate(atom.model_dump())
        assert re_validated.status == atom.status

        if atom.status == ExecutionStatus.PASSED:
            assert atom.contextual_override is True
            assert atom.is_inverse_evidence is False
            assert atom.source_quote is None
            assert atom.evaluation_reasoning is not None and len(atom.evaluation_reasoning.strip()) > 0
        elif atom.status == ExecutionStatus.FAILED:
            assert atom.contextual_override is False
            assert atom.is_inverse_evidence is False
            assert atom.source_quote is None
            assert atom.evaluation_reasoning is not None and len(atom.evaluation_reasoning.strip()) > 0


def test_causal_cohesion_idempotency_set_guard() -> None:
    """Verify that multiple steps referencing the same causal source evaluate only once."""
    settings = get_settings()
    evaluator = CausalCohesionEvaluator()

    audit = AntiFluffAuditDTO(
        isolated_concept_count=1,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.95,
        detected_hollow_terms=[],
    )

    causal_source_id = "sr_c4a5a1d15c00438a"
    evaluated_sources: set[str] = set()
    emitted_events: list[TraceEvent] = []

    # Specialist 1 runs and triggers cohesion evaluation
    if causal_source_id not in evaluated_sources:
        evaluated_sources.add(causal_source_id)
        dto1 = evaluator.evaluate_causal_cohesion(
            audit=audit,
            total_nodes=20,
            strictness_level=70,
            matrix_block_id=settings.causal_cohesion_matrix_block_id,
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
    assert settings.causal_cohesion_matrix_block_id in output_events[0].content
    assert len(output_events[0].content["results"]) == 5
    assert len(output_events[0].content["hydrated_references"]) == 5
    assert all(isinstance(a, AtomResultDTO) for a in output_events[0].content["results"])
    assert len(decision_events) == 1
    assert decision_events[0].metadata is not None
    assert decision_events[0].metadata.is_context_update is True
    assert isinstance(decision_events[0].content, GlobalContextVarsDTO)
    assert decision_events[0].content.evaluative_matrices == {settings.causal_cohesion_matrix_block_id: 5.0}


def test_causal_cohesion_l3_isolation_baseline_boundary_passed(evaluator: CausalCohesionEvaluator) -> None:
    """Verify that isolated concept ratio exactly at the SSOT baseline ceiling (20.0%) passes Level 3."""
    settings = get_settings()
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
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
    settings = get_settings()
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
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
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )
    assert res_calibrated.atom_results[1].status == ExecutionStatus.PASSED
    assert res_calibrated.atom_results[2].status == ExecutionStatus.PASSED
    assert pytest.approx(res_calibrated.score_result.score, 0.02) == 2.60
