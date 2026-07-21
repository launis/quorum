from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.interaction import (
    InteractionAnalysis,
    InteractionAnalysisDTO,
    InteractionInput,
)
from backend_v2.models.enums import InteractionStrategy, RoleClassification


def test_interaction_input_strict_validation() -> None:
    """Test that InteractionInput follows V2CoreBase strict constraints."""
    item = InteractionInput(chat_log="Hello", dynamic_inputs={"key": "val"})
    assert item.chat_log == "Hello"
    assert item.dynamic_inputs["key"] == "val"

    with pytest.raises(ValidationError):
        InteractionInput(chat_log="", dynamic_inputs={})  # min_length=1

        InteractionInput.model_validate({"chat_log": "Hello", "dynamic_inputs": {}, "extra_field": "not allowed"})


def test_interaction_analysis_dto_validation() -> None:
    """Test InteractionAnalysisDTO enums and bounds."""
    dto = InteractionAnalysisDTO(
        role_classification=RoleClassification.ARCHITECT,
        high_dependency=False,
        imperative_command_count=5,
        strategy=InteractionStrategy.CHAIN_OF_THOUGHT,
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.95,
    )
    assert dto.imperative_command_count == 5
    assert dto.strategy == InteractionStrategy.CHAIN_OF_THOUGHT

    # Test bound ge=0
    with pytest.raises(AppException):
        InteractionAnalysisDTO(
            role_classification=RoleClassification.ARCHITECT,
            high_dependency=False,
            imperative_command_count=-1,
            strategy=InteractionStrategy.CHAIN_OF_THOUGHT,
            thought_process="Thinking...",
            conclusion="Conclusion",
            confidence_score=0.95,
        )


def test_interaction_analysis_validation() -> None:
    """Test InteractionAnalysis validation."""
    analysis = InteractionAnalysis(
        role_classification=RoleClassification.NAVIGATOR,
        high_dependency=True,
        imperative_command_count=0,
        strategy=InteractionStrategy.ZERO_SHOT,
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.8,
    )
    assert analysis.role_classification == RoleClassification.NAVIGATOR
    assert analysis.high_dependency is True

    # Extra fields forbidden
    with pytest.raises(ValidationError):
        InteractionAnalysis.model_validate(
            {
                "role_classification": RoleClassification.NAVIGATOR,
                "high_dependency": True,
                "imperative_command_count": 0,
                "strategy": InteractionStrategy.ZERO_SHOT,
                "thought_process": "Thinking...",
                "conclusion": "Conclusion",
                "confidence_score": 0.8,
                "extra_hack": "not allowed",
            }
        )
