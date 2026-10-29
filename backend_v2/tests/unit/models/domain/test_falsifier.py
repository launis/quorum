"""Unit tests for Falsifier Agent domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.falsifier import (
    FalsifierData,
    FalsifierDTO,
    FalsifierInput,
    FalsifierOutput,
    ReasoningFidelity,
    WaltonStressTest,
)
from backend_v2.models.enums import FidelityLevel


def test_falsifier_input_strict_validation() -> None:
    """Test that FalsifierInput enforces V2CoreBase strict constraints and negative boundaries."""
    item = FalsifierInput(chat_log="User said something")
    assert item.chat_log == "User said something"

    with pytest.raises(ValidationError):
        FalsifierInput.model_validate({"chat_log": "Hello", "extra_field": "not allowed"})

    with pytest.raises(ValidationError):
        FalsifierInput(chat_log="")


def test_walton_stress_test_validation() -> None:
    """Test WaltonStressTest positive instantiation and negative constraints."""
    item = WaltonStressTest(question="Why?", evidence_held=True, observation="Valid")
    assert item.evidence_held is True

    with pytest.raises(ValidationError):
        WaltonStressTest.model_validate(
            {"question": "Why?", "evidence_held": True, "observation": "Valid", "extra_field": "bad"}
        )

    with pytest.raises(ValidationError):
        WaltonStressTest(question="", evidence_held=False, observation="Valid")


def test_reasoning_fidelity_validation_and_bva_bounds() -> None:
    """Test ReasoningFidelity ISTQB boundary values (0.9, 1.0, 3.0, 3.1) and AppException errors."""
    rf_min = ReasoningFidelity(
        fidelity_score=FidelityLevel.WEAK,
        fidelity_numeric=1.0,
        abductive_score=1.0,
        plausibility_score=1.0,
        justification="Minimum bound valid",
        quote="Direct quote",
    )
    assert rf_min.fidelity_numeric == 1.0

    rf_max = ReasoningFidelity(
        fidelity_score=FidelityLevel.HIGH,
        fidelity_numeric=3.0,
        abductive_score=3.0,
        plausibility_score=3.0,
        justification="Maximum bound valid",
    )
    assert rf_max.fidelity_numeric == 3.0

    # BVA min - 0.1 (0.9) on fidelity_numeric
    with pytest.raises(AppException) as exc_min:
        ReasoningFidelity(
            fidelity_score=FidelityLevel.WEAK,
            fidelity_numeric=0.9,
            abductive_score=2.0,
            plausibility_score=1.5,
            justification="Below lower bound",
        )
    assert exc_min.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED
    assert "Score must be between 1.0 and 3.0" in str(exc_min.value)

    # BVA max + 0.1 (3.1) on abductive_score
    with pytest.raises(AppException) as exc_max:
        ReasoningFidelity(
            fidelity_score=FidelityLevel.HIGH,
            fidelity_numeric=2.5,
            abductive_score=3.1,
            plausibility_score=1.5,
            justification="Above upper bound",
        )
    assert exc_max.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED
    assert "Score must be between 1.0 and 3.0" in str(exc_max.value)

    # BVA out-of-bounds on plausibility_score
    with pytest.raises(AppException) as exc_plaus:
        ReasoningFidelity(
            fidelity_score=FidelityLevel.UNCERTAIN,
            fidelity_numeric=2.0,
            abductive_score=2.0,
            plausibility_score=0.5,
            justification="Below lower bound",
        )
    assert exc_plaus.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_falsifier_data_dto_and_output_validation() -> None:
    """Test FalsifierData, FalsifierDTO, and FalsifierOutput positive and negative cases."""
    stress = WaltonStressTest(question="Why?", evidence_held=True, observation="Valid")
    rf = ReasoningFidelity(
        fidelity_score=FidelityLevel.HIGH,
        fidelity_numeric=2.5,
        abductive_score=2.0,
        plausibility_score=1.5,
        justification="Clear logic",
    )

    data = FalsifierData(stress_test_findings=[stress], fidelity_audit=rf)
    assert len(data.stress_test_findings) == 1

    dto = FalsifierDTO(
        thought_process="Step-by-step falsification analysis.",
        conclusion="Claims hold under Walton stress test.",
        confidence_score=0.85,
        falsifier_data=data,
    )
    assert dto.confidence_score == 0.85

    output = FalsifierOutput(
        thought_process="Step-by-step falsification analysis.",
        conclusion="Claims hold under Walton stress test.",
        confidence_score=0.85,
        falsifier_data=data,
    )
    assert output.falsifier_data.fidelity_audit.fidelity_numeric == 2.5

    with pytest.raises(ValidationError):
        FalsifierData(stress_test_findings=[], fidelity_audit=rf)

    with pytest.raises(AppException):
        FalsifierOutput(
            thought_process="null",
            conclusion="Valid conclusion",
            confidence_score=0.85,
            falsifier_data=data,
        )

    with pytest.raises(AppException):
        FalsifierDTO(
            thought_process="Valid thought process",
            conclusion="Valid conclusion",
            confidence_score=1.5,
            falsifier_data=data,
        )
