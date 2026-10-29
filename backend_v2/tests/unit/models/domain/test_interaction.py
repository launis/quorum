"""Unit tests for Interaction Agent domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.interaction import (
    InteractionAnalysis,
    InteractionAnalysisDTO,
    InteractionInput,
)
from backend_v2.models.enums import InteractionStrategy, RoleClassification


def test_interaction_input_strict_validation() -> None:
    """Verify that InteractionInput enforces V2CoreBase strict and boundary constraints."""
    item = InteractionInput(chat_log="Hello", dynamic_inputs={"key": "val"})
    assert item.chat_log == "Hello"
    assert item.dynamic_inputs["key"] == "val"
    assert item.last_reasoning_trace is None

    # Negative 1: Boundary value min_length=1 violated (empty string)
    with pytest.raises(ValidationError):
        InteractionInput(chat_log="", dynamic_inputs={})

    # Negative 2: Extra fields forbidden by ConfigDict(extra="forbid")
    with pytest.raises(ValidationError):
        InteractionInput.model_validate({"chat_log": "Hello", "dynamic_inputs": {}, "extra_field": "not allowed"})


def test_interaction_analysis_dto_validation() -> None:
    """Verify InteractionAnalysisDTO enum coercion and non-negative command count bounds."""
    dto = InteractionAnalysisDTO(
        role_classification=RoleClassification.ARCHITECT,
        high_dependency=False,
        imperative_command_count=0,
        strategy=InteractionStrategy.CHAIN_OF_THOUGHT,
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.95,
    )
    assert dto.imperative_command_count == 0
    assert dto.strategy == InteractionStrategy.CHAIN_OF_THOUGHT

    # Negative 1: Boundary value imperative_command_count = -1 (min - 1) raises AppException
    with pytest.raises(AppException) as exc_info:
        InteractionAnalysisDTO(
            role_classification=RoleClassification.ARCHITECT,
            high_dependency=False,
            imperative_command_count=-1,
            strategy=InteractionStrategy.CHAIN_OF_THOUGHT,
            thought_process="Thinking...",
            conclusion="Conclusion",
            confidence_score=0.95,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # Negative 2: Invalid confidence_score > 1.0 (max + 0.01) raises AppException
    with pytest.raises(AppException) as exc_bounds:
        InteractionAnalysisDTO(
            role_classification=RoleClassification.ARCHITECT,
            high_dependency=False,
            imperative_command_count=1,
            strategy=InteractionStrategy.CHAIN_OF_THOUGHT,
            thought_process="Thinking...",
            conclusion="Conclusion",
            confidence_score=1.01,
        )
    assert exc_bounds.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_interaction_analysis_validation() -> None:
    """Verify InteractionAnalysis domain model validation and negative boundary enforcement."""
    analysis = InteractionAnalysis(
        role_classification=RoleClassification.NAVIGATOR,
        high_dependency=True,
        imperative_command_count=5,
        strategy=InteractionStrategy.ZERO_SHOT,
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.8,
    )
    assert analysis.role_classification == RoleClassification.NAVIGATOR
    assert analysis.high_dependency is True
    assert analysis.imperative_command_count == 5

    # Negative 1: Negative command count raises AppException
    with pytest.raises(AppException) as exc_info:
        InteractionAnalysis(
            role_classification=RoleClassification.NAVIGATOR,
            high_dependency=True,
            imperative_command_count=-1,
            strategy=InteractionStrategy.ZERO_SHOT,
            thought_process="Thinking...",
            conclusion="Conclusion",
            confidence_score=0.8,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # Negative 2: Hallucinated empty thought_process raises AppException
    with pytest.raises(AppException) as exc_hallucination:
        InteractionAnalysis(
            role_classification=RoleClassification.NAVIGATOR,
            high_dependency=True,
            imperative_command_count=0,
            strategy=InteractionStrategy.ZERO_SHOT,
            thought_process="null",
            conclusion="Conclusion",
            confidence_score=0.8,
        )
    assert exc_hallucination.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # Negative 3: Extra fields forbidden
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
