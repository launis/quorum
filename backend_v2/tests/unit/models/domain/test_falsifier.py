import pytest
from pydantic import ValidationError

from backend_v2.models.domain.falsifier import (
    FalsifierData,
    FalsifierInput,
    ReasoningFidelity,
    WaltonStressTest,
)
from backend_v2.models.enums import FidelityLevel


def test_falsifier_input_strict_validation() -> None:
    """Test that FalsifierInput follows V2CoreBase strict constraints."""
    item = FalsifierInput(chat_log="User said something")
    assert item.chat_log == "User said something"
    
    with pytest.raises(ValidationError):
        FalsifierInput(chat_log="Hello", extra_field="not allowed")


def test_walton_stress_test_validation() -> None:
    """Test WaltonStressTest constraints."""
    item = WaltonStressTest(question="Why?", evidence_held=True, observation="Valid")
    assert item.evidence_held is True
    
    with pytest.raises(ValidationError):
        WaltonStressTest(question="Why?", evidence_held=True, observation="Valid", extra_field="bad")


def test_reasoning_fidelity_validation() -> None:
    """Test ReasoningFidelity bounds and enum."""
    rf = ReasoningFidelity(
        fidelity_score=FidelityLevel.HIGH,
        fidelity_numeric=2.5,
        abductive_score=2.0,
        plausibility_score=1.5,
        justification="Clear logic",
        quote="Direct quote"
    )
    assert rf.fidelity_numeric == 2.5
    
    # Test bounds (le=3.0)
    with pytest.raises(ValidationError):
        ReasoningFidelity(
            fidelity_score=FidelityLevel.HIGH,
            fidelity_numeric=4.0, # out of bounds
            abductive_score=2.0,
            plausibility_score=1.5,
            justification="Clear logic",
            quote="Direct quote"
        )


def test_falsifier_data_validation() -> None:
    """Test FalsifierData constraints."""
    stress = WaltonStressTest(question="Why?", evidence_held=True, observation="Valid")
    rf = ReasoningFidelity(
        fidelity_score=FidelityLevel.HIGH,
        fidelity_numeric=2.5,
        abductive_score=2.0,
        plausibility_score=1.5,
        justification="Clear logic"
    )
    
    data = FalsifierData(stress_test_findings=[stress], fidelity_audit=rf)
    assert len(data.stress_test_findings) == 1
    
    with pytest.raises(ValidationError):
        FalsifierData(stress_test_findings=[], fidelity_audit=rf) # min_length=1
