"""Unit tests for MatrixReducer three-state logic and reduce_matrix."""

from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel, JsonValue, ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.synthesis import DistilledEvaluation
from backend_v2.models.dtos.atom_evaluation import ReducedAtomDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, ExtractedValueDTO
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
    """Tests reduce_matrix retains all evaluated PASSED, FAILED, N_A, and DLQ atoms and drops PENDING atoms."""
    atom_passed = AtomResultDTO(
        tda_id="tda_11111111111111111111111111111111",
        status=ExecutionStatus.PASSED,
        source_quotes=("Passed quote",),
        evaluation_reasoning="Passed without data",
        depends_on_tda_ids=["tda_00000000000000000000000000000009"],
        is_inverse_evidence=False,
    )

    atom_inverse = AtomResultDTO(
        tda_id="tda_44444444444444444444444444444444",
        status=ExecutionStatus.PASSED,
        source_quotes=None,
        evaluation_reasoning="Inverse evidence hit",
        depends_on_tda_ids=["tda_00000000000000000000000000000009"],
        is_inverse_evidence=True,
    )

    atom_failed = AtomResultDTO(
        tda_id="tda_22222222222222222222222222222222",
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Failed completely",
    )

    atom_pass_with_data = AtomResultDTO(
        tda_id="tda_33333333333333333333333333333333",
        status=ExecutionStatus.PASSED,
        source_quotes=("Data quote",),
        extracted_data=ExtractedValueDTO(value="1M", unit="EUR"),
        evaluation_reasoning="Passed with extracted data",
    )

    atom_unstarted = AtomResultDTO(
        tda_id="tda_00000000000000000000000000000000",
        status=ExecutionStatus.PENDING,
        evaluation_reasoning="Unstarted atom",
    )

    record = MagicMock()
    record.id = "exe_12345678901234567890123456789012"
    record.duration_ms = 100
    record.steps = []
    record.step_states = {}

    class MockOutputModel(BaseModel):
        step_2: dict[str, JsonValue]

    evt_output_dict = MagicMock(event_type="output", content={"step_1": {"extensions": [{"id": "ext1"}]}})
    evt_output_model = MagicMock(event_type="output", content=MockOutputModel(step_2={"extensions": [{"id": "ext2"}]}))
    evt_input = MagicMock(event_type="input", content="some text")
    evt_primitive = MagicMock(event_type="output", content="plain string")
    evt_none = MagicMock(event_type="output", content=None)
    evt_error_items = MagicMock(event_type="output", content={"bad_item": "non_dict_val"})
    evt_atoms = MagicMock(
        event_type="output",
        content={"results": [atom_unstarted, atom_passed, atom_inverse, atom_failed, atom_pass_with_data]},
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

    # Phase 1, Step 1.2: Boolean PASSED, inverse PASSED, FAILED, and PASSED-with-data atoms are all retained
    assert len(reduced.reduced_atoms) == 4

    tda_ids = {atom.tda_id for atom in reduced.reduced_atoms}
    assert "tda_11111111111111111111111111111111" in tda_ids
    assert "tda_44444444444444444444444444444444" in tda_ids
    assert "tda_22222222222222222222222222222222" in tda_ids
    assert "tda_33333333333333333333333333333333" in tda_ids
    assert "tda_00000000000000000000000000000000" not in tda_ids

    passed_bool_atom = next(a for a in reduced.reduced_atoms if a.tda_id == "tda_11111111111111111111111111111111")
    assert passed_bool_atom.source_quotes == ("Passed quote",)
    assert passed_bool_atom.depends_on_tda_ids == ["tda_00000000000000000000000000000009"]
    assert passed_bool_atom.is_inverse_evidence is False

    inverse_atom = next(a for a in reduced.reduced_atoms if a.tda_id == "tda_44444444444444444444444444444444")
    assert inverse_atom.source_quotes is None
    assert inverse_atom.depends_on_tda_ids == ["tda_00000000000000000000000000000009"]
    assert inverse_atom.is_inverse_evidence is True

    passed_data_atom = next(a for a in reduced.reduced_atoms if a.tda_id == "tda_33333333333333333333333333333333")
    assert passed_data_atom.source_quotes == ("Data quote",)
    failed_atom = next(a for a in reduced.reduced_atoms if a.tda_id == "tda_22222222222222222222222222222222")
    assert failed_atom.source_quotes is None
    assert failed_atom.is_inverse_evidence is False

    assert reduced.execution_id == "exe_12345678901234567890123456789012"
    assert reduced.global_metrics["total_atoms"] == 5
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
    """Regression test proving reduce_matrix extracts and retains all evaluated atoms from execution_trace."""
    atom_1 = AtomResultDTO(
        tda_id="tda_11111111111111111111111111111111",
        status=ExecutionStatus.PASSED,
        source_quotes=("Valid quote",),
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
        source_quotes=("Data quote",),
        evaluation_reasoning="Passed with quantitative data",
        extracted_data=ExtractedValueDTO(value="100", unit="EUR"),
    )
    atom_na = AtomResultDTO(
        tda_id="tda_44444444444444444444444444444444",
        status=ExecutionStatus.N_A,
        evaluation_reasoning="Short-circuited due to parent failure",
        depends_on_tda_ids=["tda_22222222222222222222222222222222"],
        short_circuit_reason_tda_ids=["tda_22222222222222222222222222222222"],
    )

    record = MagicMock()
    record.id = "exe_0195f3a0000070068900000000000000"
    record.duration_ms = 250
    empty_state = MagicMock()
    empty_state.scorecard_atoms = {}
    record.step_states = {
        "sr_step_1": empty_state,
        "sr_step_2": empty_state,
    }
    record.steps = []

    evt_step_1 = MagicMock(
        event_type="output",
        content={"results": [atom_1.model_dump(), atom_2.model_dump()]},
    )
    evt_step_2 = MagicMock(
        event_type="output",
        content={"results": [atom_3.model_dump(), atom_na.model_dump()]},
    )
    record.execution_trace = [evt_step_1, evt_step_2]

    reduced = MatrixReducer.reduce_matrix(record)

    assert reduced.global_metrics["total_atoms"] == 4
    assert len(reduced.reduced_atoms) == 4
    reduced_ids = {a.tda_id for a in reduced.reduced_atoms}
    assert "tda_11111111111111111111111111111111" in reduced_ids
    assert "tda_22222222222222222222222222222222" in reduced_ids
    assert "tda_33333333333333333333333333333333" in reduced_ids
    assert "tda_44444444444444444444444444444444" in reduced_ids
    na_reduced = next(a for a in reduced.reduced_atoms if a.tda_id == "tda_44444444444444444444444444444444")
    assert na_reduced.short_circuit_reason_tda_ids == ["tda_22222222222222222222222222222222"]
    assert na_reduced.depends_on_tda_ids == ["tda_22222222222222222222222222222222"]


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
        source_quotes=("Direct list quote",),
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
            payload=[atom_with_meta, duplicate_atom],
        ),
    )
    evt_dto_list = MagicMock(
        event_type="output",
        step_name="step_list",
        content=StepOutputDTO(
            step_id="stp_2",
            block_id="blk_2",
            data_type="matrix",
            payload=[atom_in_list],
        ),
    )
    record.execution_trace = [evt_dto_dict, evt_dto_list]

    reduced = MatrixReducer.reduce_matrix(record)
    assert reduced.global_metrics["total_atoms"] == 2
    assert any(m.matrix_id == "mat_governance" for m in reduced.evaluated_matrices)
    assert len(reduced.reduced_atoms) == 2


def test_reduce_matrix_invalid_atom_raises_app_exception() -> None:
    """Test reduce_matrix raises AppException(ErrorCodes.VALIDATION_FAILED) on malformed atom results."""
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


def test_distilled_evaluation_and_reduced_atom_full_duplex_serialization_parity() -> None:
    """Verify full-duplex serialization and extra='forbid' validation on DistilledEvaluation and ReducedAtomDTO."""
    distilled = DistilledEvaluation(
        atom_id="tda_0195f3a0000070008000000000000001",
        status="FAILED",
        exact_quotes=[],
        semantic_reasoning="1. Premise\n2. Scan\n3. Anti-patterns\n4. Conclusion",
        depends_on_tda_ids=["tda_0195f3a0000070008000000000000000"],
        short_circuit_reason_tda_ids=[],
        is_inverse_evidence=True,
        topological_out_degree=3,
    )
    dumped = distilled.model_dump(mode="json", exclude_none=True)
    rehydrated = DistilledEvaluation.model_validate(dumped)
    assert rehydrated == distilled

    with pytest.raises(ValidationError):
        DistilledEvaluation.model_validate({**dumped, "unpermitted_extra_key": "value"})

    with pytest.raises(ValidationError):
        DistilledEvaluation(topological_out_degree=-1)

    reduced = ReducedAtomDTO(
        tda_id="tda_0195f3a0000070008000000000000001",
        status=ExecutionStatus.N_A,
        reasoning="Short-circuited by root failure",
        depends_on_tda_ids=["tda_0195f3a0000070008000000000000000"],
        short_circuit_reason_tda_ids=["tda_0195f3a0000070008000000000000000"],
        is_inverse_evidence=False,
    )
    reduced_dumped = reduced.model_dump(mode="json", exclude_none=True)
    reduced_rehydrated = ReducedAtomDTO.model_validate(reduced_dumped)
    assert reduced_rehydrated == reduced
    with pytest.raises(ValidationError):
        ReducedAtomDTO.model_validate({**reduced_dumped, "unknown_key": 1})
