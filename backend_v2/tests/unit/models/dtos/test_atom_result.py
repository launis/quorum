"""Unit tests for atom result DTOs and immutability invariants."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.atom_result import (
    AtomResultDTO,
    EvaluatedAtomDTO,
    EvaluationFactsDTO,
)
from backend_v2.models.enums import ExecutionStatus


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
