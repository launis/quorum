import pytest
from pydantic import ValidationError

from backend_v2.models.domain.interaction import InteractionAnalysisDTO, InteractionInput


def test_interaction_input_strictness() -> None:
    """Test that InteractionInput enforces min_length and dynamic encapsulation."""
    # Valid
    inputs = InteractionInput(chat_log="User said something", dynamic_inputs={"custom": 123})
    assert inputs.chat_log == "User said something"
    assert inputs.dynamic_inputs == {"custom": 123}

    # Fails min_length
    with pytest.raises(ValidationError):
        InteractionInput(chat_log="")

    # Fails extra="forbid"
    with pytest.raises(ValidationError):
        InteractionInput(
            chat_log="Hello",
            extra_field="Not allowed",  # type: ignore
        )


def test_interaction_analysis_dto_strictness() -> None:
    """Test that InteractionAnalysisDTO enforces ge=0 and valid roles."""
    # Valid
    dto = InteractionAnalysisDTO(
        role_classification="Passenger",
        high_dependency=True,
        imperative_command_count=0,
        strategy="Zero-shot",
        thought_process="Thinking",
        conclusion="Conclusion",
        confidence_score=0.9,
    )
    assert dto.imperative_command_count == 0

    # Fails ge=0
    with pytest.raises(ValidationError):
        InteractionAnalysisDTO(
            role_classification="Passenger",
            high_dependency=True,
            imperative_command_count=-1,
            strategy="Zero-shot",
            thought_process="Thinking",
            conclusion="Conclusion",
            confidence_score=0.9,
        )

    # Fails invalid Literal
    with pytest.raises(ValidationError):
        InteractionAnalysisDTO(
            role_classification="Boss",  # type: ignore
            high_dependency=True,
            imperative_command_count=5,
            strategy="Zero-shot",
            thought_process="Thinking",
            conclusion="Conclusion",
            confidence_score=0.9,
        )

    # Fails extra
    with pytest.raises(ValidationError):
        InteractionAnalysisDTO(
            role_classification="Passenger",
            high_dependency=True,
            imperative_command_count=0,
            strategy="Zero-shot",
            thought_process="Thinking",
            conclusion="Conclusion",
            confidence_score=0.9,
            extra="no",  # type: ignore
        )
