from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer


def test_reduce_exists() -> None:
    assert MatrixReducer.reduce_exists([]) == "DLQ"
    assert MatrixReducer.reduce_exists(["DLQ", "DLQ"]) == "DLQ"
    assert MatrixReducer.reduce_exists(["FAILED", "PASSED"]) == "PASSED"
    assert MatrixReducer.reduce_exists(["FAILED", "FAILED"]) == "FAILED"


def test_reduce_all_must_comply() -> None:
    assert MatrixReducer.reduce_all_must_comply([]) == "DLQ"
    assert MatrixReducer.reduce_all_must_comply(["PASSED", "PASSED"]) == "PASSED"
    assert MatrixReducer.reduce_all_must_comply(["PASSED", "FAILED"]) == "FAILED"
    assert MatrixReducer.reduce_all_must_comply(["PASSED", "DLQ"]) == "DLQ"


def test_reduce_dispatcher() -> None:
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
    from backend_v2.models.dtos.report.atoms import AtomResultDTO
    from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO
    from backend_v2.models.dtos.report.root import ReportDataDto
    from backend_v2.models.enums import ExecutionStatus

    metrics = ExecutionMetricsDTO(
        total_atoms=3,
        evaluated=3,
        short_circuited_na=0,
        duration_ms=100,
    )

    atom_passed = AtomResultDTO(
        tda_id="tda_11111111111111111111111111111111",
        status=ExecutionStatus.PASSED,
        extracted_data=None,
        source_quote="dummy quote",
        contextual_override=False,
        evaluation_reasoning="Passed without data",
        error_details=None,
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    atom_failed = AtomResultDTO(
        tda_id="tda_22222222222222222222222222222222",
        status=ExecutionStatus.FAILED,
        extracted_data=None,
        source_quote="dummy quote",
        contextual_override=False,
        evaluation_reasoning="Failed completely",
        error_details=None,
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    from backend_v2.models.dtos.report.atoms import HydratedAtomDTO
    from backend_v2.models.enums import SDUIComponentType

    report = ReportDataDto(
        execution_id="exe_12345678901234567890123456789012",
        workflow_id="wor_12345678901234567890123456789012",
        global_metrics=metrics,
        global_synthesis=None,
        results=[atom_passed, atom_failed],
        hydrated_references={
            "tda_11111111111111111111111111111111": HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD, resolved_claim="Claim 1", source_quote=None
            ),
            "tda_22222222222222222222222222222222": HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD, resolved_claim="Claim 2", source_quote=None
            ),
        },
    )

    reduced = MatrixReducer.reduce_matrix(report)

    # PASSED without extracted_data should be dropped to save token space
    assert len(reduced.reduced_atoms) == 1
    assert reduced.reduced_atoms[0].tda_id == "tda_22222222222222222222222222222222"
    assert reduced.reduced_atoms[0].status == "FAILED"
    assert reduced.execution_id == "exe_12345678901234567890123456789012"
