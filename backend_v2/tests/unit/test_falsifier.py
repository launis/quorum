import pytest
from pydantic import ValidationError

from backend_v2.models.domain.falsifier import (
    FalsifierData,
    FalsifierDTO,
    FalsifierInput,
    FalsifierOutput,
    ReasoningFidelity,
    WaltonStressTest,
)
from backend_v2.models.enums import FidelityLevel


def test_falsifier_input_success() -> None:
    """Test valid FalsifierInput."""
    data = FalsifierInput(chat_log="User logic")
    assert data.chat_log == "User logic"


def test_falsifier_input_validation() -> None:
    """Test min_length validation on FalsifierInput."""
    with pytest.raises(ValidationError):
        FalsifierInput(chat_log="")


def test_walton_stress_test_success() -> None:
    """Test valid WaltonStressTest."""
    test = WaltonStressTest(question="Is it true?", evidence_held=False, observation="No evidence")
    assert test.question == "Is it true?"


def test_walton_stress_test_validation() -> None:
    """Test min_length validation on WaltonStressTest."""
    with pytest.raises(ValidationError):
        WaltonStressTest(question="", evidence_held=False, observation="Obs")
    with pytest.raises(ValidationError):
        WaltonStressTest(question="Q", evidence_held=False, observation="")


def test_reasoning_fidelity_success() -> None:
    """Test valid ReasoningFidelity."""
    fidelity = ReasoningFidelity(
        fidelity_score=FidelityLevel.HIGH,
        fidelity_numeric=3.0,
        abductive_score=2.5,
        plausibility_score=2.0,
        justification="Valid justification",
        quote="Direct quote",
    )
    assert fidelity.fidelity_numeric == 3.0


def test_reasoning_fidelity_validation() -> None:
    """Test boundaries and min_length on ReasoningFidelity."""
    # Min length failures
    with pytest.raises(ValidationError):
        ReasoningFidelity(
            fidelity_score=FidelityLevel.HIGH,
            fidelity_numeric=3.0,
            abductive_score=2.5,
            plausibility_score=2.0,
            justification="",
            quote="Quote",
        )
    with pytest.raises(ValidationError):
        ReasoningFidelity(
            fidelity_score=FidelityLevel.HIGH,
            fidelity_numeric=3.0,
            abductive_score=2.5,
            plausibility_score=2.0,
            justification="Just",
            quote="",
        )

    # Score boundaries (>3.0)
    with pytest.raises(ValidationError):
        ReasoningFidelity(
            fidelity_score=FidelityLevel.HIGH,
            fidelity_numeric=3.5,
            abductive_score=2.5,
            plausibility_score=2.0,
            justification="J",
        )
    with pytest.raises(ValidationError):
        ReasoningFidelity(
            fidelity_score=FidelityLevel.HIGH,
            fidelity_numeric=3.0,
            abductive_score=0.5,
            plausibility_score=2.0,
            justification="J",
        )


def test_falsifier_data_success() -> None:
    """Test valid FalsifierData and DTOs."""
    test = WaltonStressTest(question="Q", evidence_held=True, observation="O")
    fidelity = ReasoningFidelity(
        fidelity_score=FidelityLevel.WEAK,
        fidelity_numeric=1.0,
        abductive_score=1.0,
        plausibility_score=1.0,
        justification="J",
    )
    data = FalsifierData(stress_test_findings=[test], fidelity_audit=fidelity)
    assert len(data.stress_test_findings) == 1

    dto = FalsifierDTO(
        falsifier_data=data,
        thought_process="T",
        conclusion="C",
        confidence_score=0.9,
    )
    assert dto.confidence_score == 0.9

    out = FalsifierOutput(
        falsifier_data=data,
        thought_process="T",
        conclusion="C",
        confidence_score=0.9,
        reasoning_token="trace",
    )
    assert out.reasoning_token == "trace"


def test_falsifier_data_validation() -> None:
    """Test list length validation on FalsifierData."""
    fidelity = ReasoningFidelity(
        fidelity_score=FidelityLevel.WEAK,
        fidelity_numeric=1.0,
        abductive_score=1.0,
        plausibility_score=1.0,
        justification="J",
    )
    with pytest.raises(ValidationError):
        FalsifierData(stress_test_findings=[], fidelity_audit=fidelity)
