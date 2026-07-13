"""Tests for the new Epic 91.5 ReportDataDto and its validators."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.report.atoms import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.report.metrics import ExecutionMetricsDTO
from backend_v2.models.dtos.report.root import ReportDataDto
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType


def test_atom_result_null_hypothesis_healing() -> None:
    """Test that if contextual_override is True, source_quote is stripped."""
    data = {
        "tda_id": "tda_123",
        "status": ExecutionStatus.PASSED,
        "source_quote": "hallucinated quote",
        "contextual_override": True,
        "evaluation_reasoning": "Reasoning is here.",
    }

    dto = AtomResultDTO.model_validate(data)
    assert dto.source_quote is None
    assert dto.contextual_override is True


def test_atom_result_missing_reasoning_fails() -> None:
    """Test that PASSED status requires reasoning."""
    data = {
        "tda_id": "tda_123",
        "status": ExecutionStatus.PASSED,
        "source_quote": "Valid quote",
        "contextual_override": False,
    }

    with pytest.raises(ValidationError) as exc:
        AtomResultDTO.model_validate(data)

    assert "Reasoning is mandatory for cognitive status" in str(exc.value)


def test_report_data_referential_integrity_fails() -> None:
    """Test that O(1) set logic fails if tda_id is missing from hydrated_references."""
    atom_res = AtomResultDTO(
        tda_id="tda_MISSING",
        status=ExecutionStatus.PASSED,
        source_quote="quote",
        evaluation_reasoning="reasoning",
        extracted_data=None,
        contextual_override=False,
        error_details=None,
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    metrics = ExecutionMetricsDTO(total_atoms=1, evaluated=1, short_circuited_na=0, duration_ms=100)

    with pytest.raises(ValidationError) as exc:
        ReportDataDto(
            execution_id="exe_1",
            workflow_id="wf_1",
            global_metrics=metrics,
            results=[atom_res],
            hydrated_references={},  # tda_MISSING is not here
            global_synthesis=None,
        )

    assert "Referential Integrity Error: Missing keys in hydrated_references" in str(exc.value)


def test_report_data_referential_integrity_success() -> None:
    """Test that referential integrity succeeds when all tda_ids are present."""
    atom_res = AtomResultDTO(
        tda_id="tda_123",
        status=ExecutionStatus.PASSED,
        source_quote="quote",
        evaluation_reasoning="reasoning",
        extracted_data=None,
        contextual_override=False,
        error_details=None,
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    hydrated = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD, resolved_claim="Claim", source_quote="quote"
    )

    metrics = ExecutionMetricsDTO(total_atoms=1, evaluated=1, short_circuited_na=0, duration_ms=100)

    dto = ReportDataDto(
        execution_id="exe_1",
        workflow_id="wf_1",
        global_metrics=metrics,
        results=[atom_res],
        hydrated_references={"tda_123": hydrated},
        global_synthesis=None,
    )

    assert len(dto.results) == 1
