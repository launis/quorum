"""Unit tests for MatrixReducer three-state logic and reduce_matrix."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.atom_result import AtomResultDTO, ExtractedValueDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer


def test_reduce_exists() -> None:
    """Tests EXISTS aggregation: ANY(Passed) -> Passed, ALL(Failed) -> Failed, else DLQ."""
    assert MatrixReducer.reduce_exists([]) == "DLQ"
    assert MatrixReducer.reduce_exists(["DLQ", "DLQ"]) == "DLQ"
    assert MatrixReducer.reduce_exists(["FAILED", "PASSED"]) == "PASSED"
    assert MatrixReducer.reduce_exists(["FAILED", "FAILED"]) == "FAILED"


def test_reduce_all_must_comply() -> None:
    """Tests ALL_MUST_COMPLY: ANY(Failed) -> Failed, ANY(DLQ) -> DLQ, ALL(Passed) -> Passed."""
    assert MatrixReducer.reduce_all_must_comply([]) == "DLQ"
    assert MatrixReducer.reduce_all_must_comply(["PASSED", "PASSED"]) == "PASSED"
    assert MatrixReducer.reduce_all_must_comply(["PASSED", "FAILED"]) == "FAILED"
    assert MatrixReducer.reduce_all_must_comply(["PASSED", "DLQ"]) == "DLQ"


def test_reduce_dispatcher() -> None:
    """Tests the reduce dispatcher routes to correct strategy."""
    exists_assertion = MagicMock()
    exists_assertion.aggregation_mode = "EXISTS"

    all_assertion = MagicMock()
    all_assertion.aggregation_mode = "ALL_MUST_COMPLY"

    unknown_assertion = MagicMock()
    unknown_assertion.aggregation_mode = "UNKNOWN"

    assert MatrixReducer.reduce(exists_assertion, ["PASSED", "FAILED"]) == "PASSED"
    assert MatrixReducer.reduce(all_assertion, ["PASSED", "FAILED"]) == "FAILED"

    with pytest.raises(AppException) as exc:
        MatrixReducer.reduce(unknown_assertion, ["PASSED"])

    assert exc.value.status_code == 500


def test_reduce_matrix() -> None:
    """Tests reduce_matrix filters PASS atoms without data and keeps FAIL/data atoms.

    Uses MagicMock to simulate ExecutionRecord → step_states → scorecard_atoms,
    mirroring the real ScorecardAtomDTO interface.
    """
    # Build typed atoms
    atom_passed = AtomResultDTO(
        tda_id="tda_11111111111111111111111111111111",
        status=ExecutionStatus.PASSED,
        source_quote="Passed quote",
        evaluation_reasoning="Passed without data",
    )

    atom_failed = AtomResultDTO(
        tda_id="tda_22222222222222222222222222222222",
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Failed completely",
    )

    atom_pass_with_data = AtomResultDTO(
        tda_id="tda_33333333333333333333333333333333",
        status=ExecutionStatus.PASSED,
        source_quote="Data quote",
        extracted_data=ExtractedValueDTO(value="1M", unit="EUR"),
        evaluation_reasoning="Passed with extracted data",
    )

    atom_unstarted = AtomResultDTO(
        tda_id="tda_00000000000000000000000000000000",
        status=ExecutionStatus.PENDING,
        evaluation_reasoning="Unstarted atom",
    )

    # Build mock ExecutionRecord
    record = MagicMock()
    record.id = "exe_12345678901234567890123456789012"
    record.duration_ms = 100
    record.steps = []
    record.step_states = {}

    # Populate execution_trace with various event types
    class MockOutputModel(BaseModel):
        step_2: dict[str, Any]

    evt_output_dict = MagicMock(event_type="output", content={"step_1": {"extensions": [{"id": "ext1"}]}})
    evt_output_model = MagicMock(event_type="output", content=MockOutputModel(step_2={"extensions": [{"id": "ext2"}]}))
    evt_input = MagicMock(event_type="input", content="some text")
    evt_primitive = MagicMock(event_type="output", content="plain string")
    evt_none = MagicMock(event_type="output", content=None)
    evt_error_items = MagicMock(event_type="output", content={"bad_item": "non_dict_val"})
    evt_atoms = MagicMock(
        event_type="output",
        content={"results": [atom_unstarted, atom_passed, atom_failed, atom_pass_with_data]},
    )
    record.execution_trace = [
        evt_output_dict,
        evt_output_model,
        evt_input,
        evt_primitive,
        evt_none,
        evt_error_items,
        evt_atoms,
    ]

    reduced = MatrixReducer.reduce_matrix(record)

    # PASS without extracted_facts should be dropped to save token space
    # FAIL and PASS-with-data should be kept
    assert len(reduced.reduced_atoms) == 2

    tda_ids = {atom.tda_id for atom in reduced.reduced_atoms}
    assert "tda_22222222222222222222222222222222" in tda_ids
    assert "tda_33333333333333333333333333333333" in tda_ids
    assert "tda_11111111111111111111111111111111" not in tda_ids
    assert "tda_00000000000000000000000000000000" not in tda_ids

    # Verify source_quote extraction
    passed_data_atom = next(a for a in reduced.reduced_atoms if a.tda_id == "tda_33333333333333333333333333333333")
    assert passed_data_atom.source_quote == "Data quote"
    failed_atom = next(a for a in reduced.reduced_atoms if a.tda_id == "tda_22222222222222222222222222222222")
    assert failed_atom.source_quote is None

    assert reduced.execution_id == "exe_12345678901234567890123456789012"
    assert reduced.global_metrics["total_atoms"] == 4
    assert reduced.global_metrics["duration_ms"] == 100
    assert len(reduced.raw_extensions) == 2


def test_reduce_matrix_empty_step_states() -> None:
    """Tests that reduce_matrix handles empty step_states gracefully."""
    record = MagicMock()
    record.id = "exe_empty0000000000000000000000000"
    record.duration_ms = 50
    record.steps = []
    record.step_states = {}
    record.execution_trace = []

    reduced = MatrixReducer.reduce_matrix(record)

    assert len(reduced.reduced_atoms) == 0
    assert reduced.global_metrics["total_atoms"] == 0
    assert reduced.global_metrics["duration_ms"] == 50


def test_reduce_matrix_from_execution_trace_runtime_parity() -> None:
    """Regression test proving failure when reduce_matrix runs during real DAG execution.

    During real runtime, record.step_states has empty scorecard_atoms={}.
    The evaluated atoms exist exclusively as AtomResultDTOs inside record.execution_trace output events.
    """
    from backend_v2.models.dtos.atom_result import AtomResultDTO, ExtractedValueDTO
    from backend_v2.models.enums import ExecutionStatus

    atom_1 = AtomResultDTO(
        tda_id="tda_11111111111111111111111111111111",
        status=ExecutionStatus.PASSED,
        source_quote="Valid quote",
        evaluation_reasoning="Passed reasoning",
    )
    atom_2 = AtomResultDTO(
        tda_id="tda_22222222222222222222222222222222",
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Failed reasoning",
    )
    atom_3 = AtomResultDTO(
        tda_id="tda_33333333333333333333333333333333",
        status=ExecutionStatus.PASSED,
        source_quote="Data quote",
        evaluation_reasoning="Passed with quantitative data",
        extracted_data=ExtractedValueDTO(value="100", unit="EUR"),
    )

    record = MagicMock()
    record.id = "exe_c8df6e711ca54b6900000000000000"
    record.duration_ms = 250
    # In real DAG execution, step_states has empty scorecard_atoms
    empty_state = MagicMock()
    empty_state.scorecard_atoms = {}
    record.step_states = {
        "sr_step_1": empty_state,
        "sr_step_2": empty_state,
    }
    record.steps = []

    # Real execution trace containing output events with results
    evt_step_1 = MagicMock(
        event_type="output",
        content={"results": [atom_1.model_dump(), atom_2.model_dump()]},
    )
    evt_step_2 = MagicMock(
        event_type="output",
        content={"results": [atom_3.model_dump()]},
    )
    record.execution_trace = [evt_step_1, evt_step_2]

    reduced = MatrixReducer.reduce_matrix(record)

    # Must extract all 3 atoms from execution trace and reduce them
    assert reduced.global_metrics["total_atoms"] == 3
    assert len(reduced.reduced_atoms) == 2  # atom_2 (FAILED) and atom_3 (PASSED with data)
    reduced_ids = {a.tda_id for a in reduced.reduced_atoms}
    assert "tda_22222222222222222222222222222222" in reduced_ids
    assert "tda_33333333333333333333333333333333" in reduced_ids


def test_reduce_matrix_from_step_output_dto_in_execution_trace() -> None:
    """Test reduce_matrix extracting atoms from StepOutputDTO instances in trace."""
    from backend_v2.models.state import StepOutputDTO

    atom_with_meta = AtomResultDTO(
        tda_id="tda_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Failed with metadata",
        matrix_id="mat_governance",
        extensions={"domain": "compliance"},
    )
    duplicate_atom = AtomResultDTO(
        tda_id="tda_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Duplicate atom",
    )
    atom_in_list = AtomResultDTO(
        tda_id="tda_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        status=ExecutionStatus.PASSED,
        source_quote="Direct list quote",
        extracted_data=ExtractedValueDTO(value="42", unit="pts"),
        evaluation_reasoning="Passed in direct list payload",
    )

    record = MagicMock()
    record.id = "exe_11111111111111111111111111111111"
    record.duration_ms = 300
    record.step_states = {}
    record.steps = []

    evt_dto_dict = MagicMock(
        event_type="output",
        step_name="step_gov",
        content=StepOutputDTO(
            step_id="stp_1",
            block_id="blk_1",
            data_type="matrix",
            payload={"results": [atom_with_meta.model_dump(), duplicate_atom.model_dump()]},
        ),
    )
    evt_dto_list = MagicMock(
        event_type="output",
        step_name="step_list",
        content=StepOutputDTO(
            step_id="stp_2",
            block_id="blk_2",
            data_type="matrix",
            payload=[atom_in_list.model_dump()],
        ),
    )
    record.execution_trace = [evt_dto_dict, evt_dto_list]

    reduced = MatrixReducer.reduce_matrix(record)
    assert reduced.global_metrics["total_atoms"] == 2
    assert any(m["matrix_id"] == "mat_governance" for m in reduced.evaluated_matrices)
    assert len(reduced.reduced_atoms) == 2


def test_reduce_matrix_invalid_atom_raises_app_exception() -> None:
    """Test reduce_matrix raises AppException(ErrorCodes.VALIDATION_FAILED) on malformed atom results."""
    from backend_v2.exceptions import AppException

    record = MagicMock()
    record.id = "exe_22222222222222222222222222222222"
    record.duration_ms = 100
    record.step_states = {}
    record.steps = []

    evt_corrupted = MagicMock(
        event_type="output",
        content={"results": [{"invalid_atom_structure": 123}]},
    )
    record.execution_trace = [evt_corrupted]

    with pytest.raises(AppException) as exc_info:
        MatrixReducer.reduce_matrix(record)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"

