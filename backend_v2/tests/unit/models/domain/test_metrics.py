"""Unit tests for Metrics Domain Models.

Validates that TextMetricsDTO, BehavioralMetricsDTO, ProfilerMetricsDTO, and MetricsPayloadDTO
enforce strict validation, boundary limits, and Fail-Fast AppException behavior.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.metrics import (
    BehavioralMetricsDTO,
    MetricsPayloadDTO,
    ProfilerMetricsDTO,
    TextMetricsDTO,
)


def test_metrics_payload_dto_from_dict() -> None:
    """Test that a raw dictionary payload wraps properly into root."""
    raw = {"word_count": 100, "sentence_count": 10}
    dto = MetricsPayloadDTO.model_validate(raw)
    assert dto.root == raw


def test_metrics_payload_dto_direct_instantiation() -> None:
    """Test direct instantiation of MetricsPayloadDTO."""
    dto = MetricsPayloadDTO(root={"key": "val"})
    assert dto.root == {"key": "val"}


def test_metrics_payload_dto_from_instance() -> None:
    """Test validation of an existing MetricsPayloadDTO instance."""
    original = MetricsPayloadDTO(root={"key": "val"})
    validated = MetricsPayloadDTO.model_validate(original)
    assert validated.root == {"key": "val"}


def test_text_metrics_dto_valid_defaults() -> None:
    """Test that TextMetricsDTO instantiates with non-negative defaults."""
    dto = TextMetricsDTO()
    assert dto.word_count == 0
    assert dto.sentence_count == 0
    assert dto.avg_sentence_length == 0.0
    assert dto.lexical_diversity == 0.0
    assert dto.capitalization_ratio == 0.0
    assert dto.control_ratio == 0.0


def test_text_metrics_dto_boundary_values() -> None:
    """Test TextMetricsDTO accepts positive and exact zero boundary values."""
    dto = TextMetricsDTO(
        word_count=0,
        sentence_count=1,
        avg_sentence_length=1.5,
        lexical_diversity=0.8,
        capitalization_ratio=0.1,
        control_ratio=0.5,
    )
    assert dto.word_count == 0
    assert dto.sentence_count == 1
    assert dto.avg_sentence_length == 1.5


def test_text_metrics_dto_negative_word_count_fails_fast() -> None:
    """Test TextMetricsDTO raises AppException on negative boundary value."""
    with pytest.raises(AppException) as exc_info:
        TextMetricsDTO(word_count=-1)

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Text metric must be >= 0" in exc_info.value.message


def test_text_metrics_dto_negative_float_fails_fast() -> None:
    """Test TextMetricsDTO raises AppException on negative float boundary value."""
    with pytest.raises(AppException) as exc_info:
        TextMetricsDTO(lexical_diversity=-0.01)

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_behavioral_metrics_dto_valid() -> None:
    """Test BehavioralMetricsDTO instantiates properly with valid values."""
    dto = BehavioralMetricsDTO(
        say_do_gap=0.2,
        automation_bias=0.1,
        illusion_of_competence=0.0,
        imperative_command_count=3,
    )
    assert dto.say_do_gap == 0.2
    assert dto.imperative_command_count == 3


def test_behavioral_metrics_dto_negative_fails_fast() -> None:
    """Test BehavioralMetricsDTO raises AppException on negative values."""
    with pytest.raises(AppException) as exc_info:
        BehavioralMetricsDTO(automation_bias=-0.5)

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Behavioral metric must be >= 0" in exc_info.value.message


def test_behavioral_metrics_dto_negative_count_fails_fast() -> None:
    """Test BehavioralMetricsDTO raises AppException on negative integer count."""
    with pytest.raises(AppException) as exc_info:
        BehavioralMetricsDTO(imperative_command_count=-1)

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_profiler_metrics_dto_valid() -> None:
    """Test ProfilerMetricsDTO instantiates with combined metrics."""
    dto = ProfilerMetricsDTO(
        word_count=150,
        sentence_count=10,
        avg_sentence_length=15.0,
        lexical_diversity=0.75,
        capitalization_ratio=0.05,
        control_ratio=0.8,
        say_do_gap=0.1,
        automation_bias=0.2,
        illusion_of_competence=0.0,
        imperative_command_count=2,
    )
    assert dto.word_count == 150
    assert dto.control_ratio == 0.8


def test_profiler_metrics_dto_negative_fails_fast() -> None:
    """Test ProfilerMetricsDTO raises AppException on negative metric."""
    with pytest.raises(AppException) as exc_info:
        ProfilerMetricsDTO(control_ratio=-0.1)

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Profiler metric must be >= 0" in exc_info.value.message


def test_metrics_extra_fields_forbidden() -> None:
    """Test that all metrics models reject unknown extra fields."""
    with pytest.raises(ValidationError):
        TextMetricsDTO.model_validate({"word_count": 10, "unknown_field": 123})

    with pytest.raises(ValidationError):
        BehavioralMetricsDTO.model_validate({"say_do_gap": 0.5, "extra": "forbidden"})

    with pytest.raises(ValidationError):
        ProfilerMetricsDTO.model_validate({"word_count": 10, "extra": "forbidden"})
