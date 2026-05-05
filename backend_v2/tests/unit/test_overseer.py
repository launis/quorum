"""Unit tests for Overseer Agent Domain Models."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.overseer import (
    EthicalObservation,
    FactCheckRFI,
    OverseerData,
    OverseerDTO,
    OverseerInput,
    OverseerOutput,
)


def test_fact_check_rfi_valid() -> None:
    """Test FactCheckRFI with valid data and auto-verification."""
    rfi = FactCheckRFI(
        claim="The earth is round.",
        verification_result="Verified",
        source_or_reasoning="Science.",
    )
    assert rfi.claim == "The earth is round."
    assert rfi.is_verified is True
    assert rfi.verification_result == "Verified"

    rfi_debunked = FactCheckRFI(
        claim="The earth is flat.",
        verification_result="Debunked",
        source_or_reasoning="Science.",
    )
    assert rfi_debunked.is_verified is False


def test_fact_check_rfi_empty_strings_fail() -> None:
    """Test FactCheckRFI fails with empty strings (min_length=1)."""
    with pytest.raises(ValidationError):
        FactCheckRFI(
            claim="",
            verification_result="Verified",
            source_or_reasoning="Science.",
        )


def test_ethical_observation_valid() -> None:
    """Test EthicalObservation valid data and auto-critical."""
    obs = EthicalObservation(
        issue_type="Bias",
        severity="Critical",
        description="Highly biased output.",
    )
    assert obs.is_critical is True
    assert obs.severity == "Critical"

    obs_warn = EthicalObservation(
        issue_type="Tone",
        severity="Warning",
        description="Slightly aggressive tone.",
    )
    assert obs_warn.is_critical is False


def test_ethical_observation_empty_strings_fail() -> None:
    """Test EthicalObservation fails with empty strings."""
    with pytest.raises(ValidationError):
        EthicalObservation(
            issue_type="",
            severity="Warning",
            description="Empty issue type.",
        )


def test_overseer_data_empty_ethics_fail() -> None:
    """Test OverseerData fails if ethical_issues is empty (min_length=1)."""
    with pytest.raises(ValidationError):
        OverseerData(
            fact_checks=[],
            ethical_issues=[],
        )


def test_overseer_data_valid() -> None:
    """Test OverseerData with valid data."""
    obs = EthicalObservation(
        issue_type="Bias",
        severity="Warning",
        description="A minor bias.",
    )
    data = OverseerData(
        fact_checks=[],
        ethical_issues=[obs],
    )
    assert len(data.ethical_issues) == 1


def test_overseer_input_valid() -> None:
    """Test OverseerInput valid data."""
    inp = OverseerInput(
        chat_log="User: Hello\nAgent: Hi",
    )
    assert inp.chat_log == "User: Hello\nAgent: Hi"


def test_overseer_input_empty_chat_log_fails() -> None:
    """Test OverseerInput fails with empty chat log."""
    with pytest.raises(ValidationError):
        OverseerInput(chat_log="")


def test_overseer_input_extra_allowed() -> None:
    """Test OverseerInput allows extra fields."""
    inp = OverseerInput.model_validate({"chat_log": "Log", "unknown_field": "Allowed"})
    assert inp.chat_log == "Log"


def test_overseer_dto_and_output() -> None:
    """Test DTOs are instantiated properly."""
    obs = EthicalObservation(
        issue_type="Bias",
        severity="Warning",
        description="A minor bias.",
    )
    data = OverseerData(
        fact_checks=[],
        ethical_issues=[obs],
    )

    dto = OverseerDTO(
        thought_process="Thinking about ethics.",
        conclusion="The text is moderately fine.",
        confidence_score=0.85,
        overseer_data=data,
    )
    assert dto.confidence_score == 0.85

    output = OverseerOutput(
        thought_process="Thinking about ethics.",
        conclusion="The text is moderately fine.",
        confidence_score=0.85,
        overseer_data=data,
    )
    assert output.conclusion == "The text is moderately fine."
