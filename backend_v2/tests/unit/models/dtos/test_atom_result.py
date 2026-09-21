"""Unit tests for atom result DTOs and immutability invariants."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.atom_result import (
    AtomResultDTO,
    ErrorDetailsDTO,
    EvaluatedAtomDTO,
    EvaluationFactsDTO,
    ExecutionMetricsDTO,
    ExtensionMetricsDTO,
    ExtractedValueDTO,
    HydratedAtomDTO,
)
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType


def test_atom_result_rejects_failed_with_contextual_override() -> None:
    """Test contract: FAILED atom with contextual_override=True raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="atm_test_1",
            status=ExecutionStatus.FAILED,
            evaluation_reasoning="Assertion failed because criteria were not met.",
            contextual_override=True,
        )
    assert "contextual_override cannot be True when status is FAILED" in str(exc_info.value)


def test_atom_result_rejects_failed_without_reasoning() -> None:
    """Test contract: FAILED atom without reasoning raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="atm_test_fail_no_reason",
            status=ExecutionStatus.FAILED,
            evaluation_reasoning="",
        )
    assert "Reasoning is mandatory for cognitive status FAILED" in str(exc_info.value)


def test_atom_result_rejects_failed_with_inverse_evidence() -> None:
    """Test contract: FAILED atom with is_inverse_evidence=True raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="atm_test_fail_inv",
            status=ExecutionStatus.FAILED,
            evaluation_reasoning="Failed evidence.",
            is_inverse_evidence=True,
        )
    assert "is_inverse_evidence cannot be True when status is FAILED" in str(exc_info.value)


def test_atom_result_rejects_failed_with_source_quote() -> None:
    """Test contract: FAILED atom with source_quote raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="atm_test_2",
            status=ExecutionStatus.FAILED,
            evaluation_reasoning="Assertion failed.",
            source_quote="Some quote",
        )
    assert "source_quote must be None when status is FAILED" in str(exc_info.value)


def test_atom_result_rejects_passed_without_reasoning() -> None:
    """Test contract: PASSED atom without reasoning raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="atm_test_pass_no_reason",
            status=ExecutionStatus.PASSED,
            source_quote="Valid quote",
        )
    assert "Reasoning is mandatory for cognitive status PASSED" in str(exc_info.value)


def test_atom_result_rejects_passed_without_quote_or_override() -> None:
    """Test contract: PASSED atom without quote or override raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="atm_test_pass_no_quote",
            status=ExecutionStatus.PASSED,
            evaluation_reasoning="Passed without evidence.",
        )
    assert "source_quote is mandatory unless contextual_override or is_inverse_evidence is True" in str(exc_info.value)


def test_atom_result_rejects_passed_with_override_and_quote() -> None:
    """Test contract: PASSED atom with contextual_override and source_quote raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="atm_test_3",
            status=ExecutionStatus.PASSED,
            evaluation_reasoning="Passed via cognitive override.",
            contextual_override=True,
            source_quote="Quote should not be present",
        )
    assert "source_quote must be None when contextual_override or is_inverse_evidence is True" in str(exc_info.value)


def test_atom_result_passed_with_valid_quote() -> None:
    """Positive test: PASSED atom with valid source quote and reasoning succeeds."""
    res = AtomResultDTO(
        tda_id="atm_test_4",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="The deliverable clearly states the value.",
        source_quote="Exact quotation from text",
    )
    assert res.status == ExecutionStatus.PASSED
    assert res.source_quote == "Exact quotation from text"


def test_atom_result_passed_with_inverse_evidence() -> None:
    """Positive test: PASSED atom with is_inverse_evidence and no quote succeeds."""
    res = AtomResultDTO(
        tda_id="atm_test_inv_pass",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Confirmed absence of violation.",
        is_inverse_evidence=True,
        source_quote=None,
    )
    assert res.status == ExecutionStatus.PASSED
    assert res.is_inverse_evidence is True
    assert res.source_quote is None


def test_atom_result_system_error_validation() -> None:
    """Test contract: SYSTEM_ERROR requires error_details; valid error_details succeeds."""
    with pytest.raises(ValidationError) as exc_info:
        AtomResultDTO(
            tda_id="atm_test_err_none",
            status=ExecutionStatus.SYSTEM_ERROR,
        )
    assert "Error details are mandatory when status is SYSTEM_ERROR" in str(exc_info.value)

    res = AtomResultDTO(
        tda_id="atm_test_err_ok",
        status=ExecutionStatus.SYSTEM_ERROR,
        error_details=ErrorDetailsDTO(error_code="LLM_TIMEOUT", message="Gateway timeout"),
    )
    assert res.status == ExecutionStatus.SYSTEM_ERROR
    assert res.error_details is not None
    assert res.error_details.error_code == "LLM_TIMEOUT"


def test_atom_result_extra_fields_forbidden() -> None:
    """Test contract: AtomResultDTO rejects extra unexpected fields."""
    with pytest.raises(ValidationError):
        AtomResultDTO(
            tda_id="atm_extra",
            status=ExecutionStatus.PASSED,
            evaluation_reasoning="Reasoning",
            source_quote="Quote",
            extra_forbidden_field="crash",  # type: ignore[call-arg]
        )


def test_evaluated_atom_dto_immutability() -> None:
    """Test contract: EvaluatedAtomDTO is strictly frozen and rejects attribute mutation."""
    atom = EvaluatedAtomDTO(
        tda_id="atm_eval_1",
        status="PASSED",
        score=1.0,
        human_override=None,
    )
    assert atom.tda_id == "atm_eval_1"
    with pytest.raises((ValidationError, TypeError)):
        atom.human_override = "FAILED"  # type: ignore[misc]


def test_evaluation_facts_dto_immutability() -> None:
    """Test contract: EvaluationFactsDTO is strictly frozen and maps facts."""
    facts_dto = EvaluationFactsDTO(facts={"cond1": True, "cond2": "PASSED"})
    assert facts_dto.facts["cond1"] is True
    with pytest.raises((ValidationError, TypeError)):
        facts_dto.facts = {"new": False}  # type: ignore[misc]


def test_error_details_dto() -> None:
    """Test contract: ErrorDetailsDTO construction, frozen immutability, and extra fields forbidden."""
    err = ErrorDetailsDTO(error_code="PARSE_ERROR", message="Invalid JSON")
    assert err.error_code == "PARSE_ERROR"
    assert err.message == "Invalid JSON"
    with pytest.raises((ValidationError, TypeError)):
        err.message = "Updated"  # type: ignore[misc]

    with pytest.raises(ValidationError):
        ErrorDetailsDTO(error_code="ERR", message="msg", extra_field=123)  # type: ignore[call-arg]


def test_hydrated_atom_dto() -> None:
    """Test contract: HydratedAtomDTO construction and extra field rejection."""
    atom = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Carbon emissions must be zero.",
        source_quote="Zero emissions target.",
    )
    assert atom.sdui_component == SDUIComponentType.BOOLEAN_CARD
    assert atom.resolved_claim == "Carbon emissions must be zero."

    with pytest.raises(ValidationError):
        HydratedAtomDTO(
            sdui_component=SDUIComponentType.BOOLEAN_CARD,
            resolved_claim="Claim",
            unsupported_extra=True,  # type: ignore[call-arg]
        )


def test_extracted_value_dto() -> None:
    """Test contract: ExtractedValueDTO supports float, int, str, bool and forbids extra fields."""
    val_num = ExtractedValueDTO(value=42.5, unit="EUR")
    assert val_num.value == 42.5
    assert val_num.unit == "EUR"

    val_bool = ExtractedValueDTO(value=True)
    assert val_bool.value is True
    assert val_bool.unit is None

    with pytest.raises(ValidationError):
        ExtractedValueDTO(value=10, extra_prop="disallowed")  # type: ignore[call-arg]


def test_execution_metrics_dto() -> None:
    """Test contract: ExecutionMetricsDTO field bounds (ge=0) and forbidden extra fields."""
    metrics = ExecutionMetricsDTO(
        total_atoms=10,
        evaluated=8,
        short_circuited_na=2,
        duration_ms=1500,
    )
    assert metrics.total_atoms == 10
    assert metrics.duration_ms == 1500

    with pytest.raises(ValidationError):
        ExecutionMetricsDTO(
            total_atoms=-1,
            evaluated=0,
            short_circuited_na=0,
        )

    with pytest.raises(ValidationError):
        ExecutionMetricsDTO(
            total_atoms=5,
            evaluated=5,
            short_circuited_na=0,
            duration_ms=-10,
        )


def test_extension_metrics_dto() -> None:
    """Test contract: ExtensionMetricsDTO construction and bounds checks."""
    ext = ExtensionMetricsDTO(
        authenticity_score=0.85,
        performative_phrases_count=3.0,
        variance_score=0.12,
        alignment_verdict="ALIGNED",
        jargon_density=0.45,
        total_word_count=1200,
    )
    assert ext.authenticity_score == 0.85
    assert ext.total_word_count == 1200

    with pytest.raises(ValidationError):
        ExtensionMetricsDTO(total_word_count=-5)

    with pytest.raises(ValidationError):
        ExtensionMetricsDTO(extra_field=True)  # type: ignore[call-arg]
