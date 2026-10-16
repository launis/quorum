"""Reproduction test for Causal Cohesion State Projection bug.

Verifies that emitting causal cohesion evaluation events on causal_source_step_id
does not corrupt StateProjector snapshot with bare AtomResultDTO or trigger
'Legacy flat trace detected' AppException on downstream snapshot reads.
"""

from __future__ import annotations

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO, CausalNodeDTO
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer


def test_state_projector_atom_result_dto_does_not_corrupt_snapshot() -> None:
    """Verifies that TraceEvents containing AtomResultDTO do not crash StateProjector.snapshot."""
    projector = StateProjector()

    step_id = "sr_c4a5a1d15c00438a"

    # 1. Causal Discovery step emits its graph output
    node = CausalNodeDTO(
        node_id="nod_1",
        claim="Claim 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    graph = CausalGraphPayloadDTO(
        nodes=[node],
        edges=[],
        root_cause_node_ids=[],
        isolated_node_ids=[],
    )
    graph_event = TraceEvent(
        step_name=step_id,
        event_type="output",
        content=StepOutputContentDTO(data={"graph": graph.model_dump(mode="json")}),
    )
    projector.apply_delta(graph_event)

    # Snapshot is valid so far
    initial_snapshot = projector.snapshot
    assert len(initial_snapshot) == 1
    assert initial_snapshot[0].step_id == step_id

    # 2. Causal Cohesion evaluator emits atom results with step_name=causal_source_step_id
    atom = AtomResultDTO(
        tda_id="tda_c0a1e50000000001",
        matrix_id="blk_c0a1e50000000001",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Topological causal cohesion score 0.93 satisfies Level 1 threshold.",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_event = TraceEvent(
        step_name=step_id,
        event_type="output",
        content=atom,
    )
    projector.apply_delta(atom_event)

    # 3. Downstream step accesses projector.snapshot
    snapshot_after_atom = projector.snapshot
    assert len(snapshot_after_atom) >= 1
    # Verify snapshot items are strictly StepOutputDTO
    for dto in snapshot_after_atom:
        assert dto.step_id == step_id


def test_state_projector_atom_result_dto_preserves_graph_and_accumulates_results() -> None:
    """Verifies that multiple AtomResultDTOs accumulate into results while preserving graph key."""
    projector = StateProjector()
    step_id = "sr_c4a5a1d15c00438a"

    # Step emits initial graph
    node = CausalNodeDTO(
        node_id="nod_1",
        claim="Claim 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    projector.apply_delta(
        TraceEvent(
            step_name=step_id,
            event_type="output",
            content=CausalGraphPayloadDTO(
                nodes=[node],
                edges=[],
                root_cause_node_ids=[],
                isolated_node_ids=[],
            ),
        )
    )

    atom_1 = AtomResultDTO(
        tda_id="tda_1",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 1",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_2 = AtomResultDTO(
        tda_id="tda_2",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 2",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    projector.apply_delta(TraceEvent(step_name=step_id, event_type="output", content=atom_1))
    projector.apply_delta(TraceEvent(step_name=step_id, event_type="output", content=atom_2))

    snapshot = projector.snapshot
    assert len(snapshot) == 2
    by_block = {dto.block_id: dto for dto in snapshot}
    assert "graph" in by_block
    assert "results" in by_block
    results_payload = by_block["results"].payload
    assert isinstance(results_payload, list)
    assert len(results_payload) == 2
    assert results_payload[0] == atom_1
    assert results_payload[1] == atom_2


def test_state_projector_atom_result_list_aggregates_into_results() -> None:
    """Verifies that passing a list of AtomResultDTOs aggregates correctly into StepOutputContentDTO."""
    projector = StateProjector()
    step_id = "sr_specialist_batch"

    atom_1 = AtomResultDTO(
        tda_id="tda_b1",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Batch 1",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_2 = AtomResultDTO(
        tda_id="tda_b2",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.FAILED,
        contextual_override=False,
        is_inverse_evidence=False,
        evaluation_reasoning="Batch 2",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    projector.apply_delta(
        TraceEvent(
            step_name=step_id,
            event_type="output",
            content=[atom_1, atom_2],
        )
    )

    snapshot = projector.snapshot
    assert len(snapshot) == 1
    dto = snapshot[0]
    assert dto.step_id == step_id
    assert dto.block_id == "results"
    assert isinstance(dto.payload, list)
    assert len(dto.payload) == 2
    assert dto.payload[0] == atom_1
    assert dto.payload[1] == atom_2


def test_state_projector_unsupported_content_type_fails_fast() -> None:
    """Negative Test: Unsupported arbitrary content in output event triggers Fail-Fast AppException."""
    from backend_v2.exceptions import ErrorCodes

    projector = StateProjector()

    event = TraceEvent(
        step_name="stp_invalid",
        event_type="output",
        content="unstructured_flat_string_payload",
    )

    with pytest.raises(AppException) as exc_info:
        projector.apply_delta(event)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Legacy flat trace detected" in exc_info.value.message


def test_state_projector_results_dict_preserves_graph_and_accumulates_results() -> None:
    """Verifies that TraceEvents containing {'results': [atoms]} preserve graph and populate results block."""
    projector = StateProjector()
    step_id = "sr_c4a5a1d15c00438a"

    # Step emits initial graph
    node = CausalNodeDTO(
        node_id="nod_1",
        claim="Claim 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    projector.apply_delta(
        TraceEvent(
            step_name=step_id,
            event_type="output",
            content=CausalGraphPayloadDTO(
                nodes=[node],
                edges=[],
                root_cause_node_ids=[],
                isolated_node_ids=[],
            ),
        )
    )

    atom_1 = AtomResultDTO(
        tda_id="tda_1",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 1",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_2 = AtomResultDTO(
        tda_id="tda_2",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 2",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    projector.apply_delta(
        TraceEvent(
            step_name=step_id,
            event_type="output",
            content={"results": [atom_1, atom_2]},
        )
    )

    snapshot = projector.snapshot
    assert len(snapshot) == 2
    by_block = {dto.block_id: dto for dto in snapshot}
    assert "graph" in by_block
    assert "results" in by_block
    results_payload = by_block["results"].payload
    assert isinstance(results_payload, list)
    assert len(results_payload) == 2
    assert results_payload[0] == atom_1
    assert results_payload[1] == atom_2


def test_state_projector_results_dict_with_raw_dicts_deserializes_and_accumulates() -> None:
    """Verifies that replaying a JSON trace with raw atom dicts inside {'results': [...]} deserializes cleanly."""
    projector = StateProjector()
    step_id = "sr_c4a5a1d15c00438a"

    # Step emits initial graph
    node = CausalNodeDTO(
        node_id="nod_1",
        claim="Claim 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    projector.apply_delta(
        TraceEvent(
            step_name=step_id,
            event_type="output",
            content=CausalGraphPayloadDTO(
                nodes=[node],
                edges=[],
                root_cause_node_ids=[],
                isolated_node_ids=[],
            ),
        )
    )

    atom_1 = AtomResultDTO(
        tda_id="tda_1",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 1",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_2 = AtomResultDTO(
        tda_id="tda_2",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.FAILED,
        contextual_override=False,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 2",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    # Content serialized from JSON trace as raw dictionaries
    raw_content = {
        "results": [
            atom_1.model_dump(mode="json"),
            atom_2.model_dump(mode="json"),
        ]
    }
    projector.apply_delta(
        TraceEvent(
            step_name=step_id,
            event_type="output",
            content=raw_content,
        )
    )

    snapshot = projector.snapshot
    assert len(snapshot) == 2
    by_block = {dto.block_id: dto for dto in snapshot}
    assert "graph" in by_block
    assert "results" in by_block
    results_payload = by_block["results"].payload
    assert isinstance(results_payload, list)
    assert len(results_payload) == 2
    assert results_payload[0] == atom_1
    assert results_payload[1] == atom_2


def test_matrix_reducer_extracts_causal_cohesion_when_wrapped_in_results() -> None:
    """Verifies that MatrixReducer extracts evaluated matrices and atoms when wrapped in {'results': [...]}."""
    step_id = "sr_c4a5a1d15c00438a"

    atom_1 = AtomResultDTO(
        tda_id="tda_1",
        matrix_id="blk_cohesion_bars",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 1",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_2 = AtomResultDTO(
        tda_id="tda_2",
        matrix_id="blk_cohesion_bars",
        status=ExecutionStatus.FAILED,
        contextual_override=False,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 2",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    events = [
        TraceEvent(
            step_name=step_id,
            event_type="output",
            content={"results": [atom_1, atom_2]},
        )
    ]
    record = ExecutionRecord(
        id="exe_0000000000000001",
        workflow_id="wf_0000000000000001",
        target_locale="en",
        execution_trace=events,
    )

    reduced = MatrixReducer.reduce_matrix(record)
    assert "blk_cohesion_bars" in [m.matrix_id for m in reduced.evaluated_matrices]
    assert reduced.global_metrics["total_atoms"] == 2
    assert reduced.global_metrics["evaluated"] == 2
    assert len(reduced.reduced_atoms) == 1
    assert reduced.reduced_atoms[0].tda_id == "tda_2"


def test_causal_cohesion_trace_event_must_provide_hydrated_references_for_report_dto() -> None:
    """Verifies that causal cohesion evaluation trace events provide hydrated_references required by ReportDataDTO.

    When DAGExecutor evaluates causal cohesion on an upstream causal source, the emitted output
    TraceEvent must include 'hydrated_references' mapping all 5 BARS atom IDs (tda_c0a1e5...) to
    HydratedAtomDTO instances. Omitting hydrated_references causes ReportDataDTO referential integrity
    validation to crash with:
    'Referential Integrity Error: Missing keys in hydrated_references: {...}'
    """
    from datetime import datetime, timezone

    from backend_v2.models.core_base import I18nText
    from backend_v2.models.dtos.atom_result import HydratedAtomDTO
    from backend_v2.models.dtos.causal_discovery import AntiFluffAuditDTO
    from backend_v2.models.dtos.report_data import ReportDataDTO
    from backend_v2.services.orchestrator.causal_cohesion_evaluator import (
        CAUSAL_COHESION_TDA_IDS,
        CausalCohesionEvaluator,
    )

    evaluator = CausalCohesionEvaluator()
    audit = AntiFluffAuditDTO(
        logical_cohesion_score=0.85,
        cycle_detected=False,
        isolated_concept_count=1,
        unsupported_claims_count=0,
    )
    eval_dto = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=10,
        strictness_level=0,
        matrix_block_id="blk_c0a1e50000000001",
    )

    # Invariant: eval_dto must expose hydrated_references for all 5 BARS atoms
    assert eval_dto.hydrated_references is not None, "CausalCohesionEvaluationDTO must provide hydrated_references"
    assert len(eval_dto.hydrated_references) == len(CAUSAL_COHESION_TDA_IDS)
    for tda_id in CAUSAL_COHESION_TDA_IDS:
        assert tda_id in eval_dto.hydrated_references
        assert isinstance(eval_dto.hydrated_references[tda_id], HydratedAtomDTO)

    # Invariant: TraceEvent content must bundle hydrated_references alongside results
    step_id = "sr_c4a5a1d15c00438a"
    event = TraceEvent(
        step_name=step_id,
        event_type="output",
        content={
            "results": eval_dto.atom_results,
            "hydrated_references": eval_dto.hydrated_references,
        },
    )

    projector = StateProjector()
    projector.apply_delta(event)
    snapshot = projector.snapshot

    by_block = {dto.block_id: dto for dto in snapshot}
    assert "results" in by_block
    assert "hydrated_references" in by_block

    v2_results: list[AtomResultDTO] = by_block["results"].payload
    v2_hydrated_refs: dict[str, HydratedAtomDTO] = by_block["hydrated_references"].payload

    # Invariant: ReportDataDTO referential integrity check must pass without exception
    i18n = I18nText(translations={"en": "Test", "fi": "Testi"})
    report_dto = ReportDataDTO(
        strictness_level=0,
        scoring_strategy="UNIFIED",
        scoring_engine_name="UNIFIED",
        user_name="Test User",
        workflow_id="wf_0000000000000001",
        execution_id="exe_0000000000000001",
        profile_id="prf_0000000000000001",
        profile_name=i18n,
        profile_description=i18n,
        available_profiles={"prf_0000000000000001": i18n},
        created_at=datetime.now(timezone.utc),
        local_time_str="2026-10-15 20:35:48",
        custom_preface_md=None,
        org_name="Test Org",
        global_score=3.0,
        has_warning=False,
        inner_sdui_blocks=[],
        visible_metadata=[],
        cost_estimate=0.01,
        total_tokens=100,
        prompt_tokens=80,
        completion_tokens=20,
        reasoning_tokens=0,
        mcp_tool_audit=[],
        results=v2_results,
        hydrated_references=v2_hydrated_refs,
    )
    assert len(report_dto.results) == 5
    assert len(report_dto.hydrated_references) == 5
