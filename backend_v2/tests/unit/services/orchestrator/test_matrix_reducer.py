"""Unit tests for MatrixReducer three-state logic and reduce_matrix."""

from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
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
    # Build mock atoms
    atom_passed = MagicMock()
    atom_passed.status = "PASS"
    atom_passed.extracted_facts = {}
    atom_passed.exact_quotes = []
    atom_passed.semantic_reasoning = "Passed without data"

    atom_failed = MagicMock()
    atom_failed.status = "FAIL"
    atom_failed.extracted_facts = {}
    atom_failed.exact_quotes = []
    atom_failed.semantic_reasoning = "Failed completely"

    atom_pass_with_data = MagicMock()
    atom_pass_with_data.status = "PASS"
    atom_pass_with_data.extracted_facts = {"revenue": "1M EUR"}
    atom_pass_with_data.exact_quotes = []
    atom_pass_with_data.semantic_reasoning = "Passed with extracted data"

    # Build mock step state
    step_state = MagicMock()
    step_state.scorecard_atoms = {
        "tda_11111111111111111111111111111111": atom_passed,
        "tda_22222222222222222222222222222222": atom_failed,
        "tda_33333333333333333333333333333333": atom_pass_with_data,
    }

    # Build mock ExecutionRecord
    record = MagicMock()
    record.id = "exe_12345678901234567890123456789012"
    record.duration_ms = 100
    record.step_states = {"step_1": step_state}

    reduced = MatrixReducer.reduce_matrix(record)

    # PASS without extracted_facts should be dropped to save token space
    # FAIL and PASS-with-data should be kept
    assert len(reduced.reduced_atoms) == 2

    tda_ids = {atom.tda_id for atom in reduced.reduced_atoms}
    assert "tda_22222222222222222222222222222222" in tda_ids
    assert "tda_33333333333333333333333333333333" in tda_ids
    assert "tda_11111111111111111111111111111111" not in tda_ids

    assert reduced.execution_id == "exe_12345678901234567890123456789012"
    assert reduced.global_metrics["total_atoms"] == 3
    assert reduced.global_metrics["duration_ms"] == 100
