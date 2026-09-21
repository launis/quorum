"""Unit tests for StepTelemetryEntryDTO."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.step_telemetry import StepTelemetryEntryDTO


def test_step_telemetry_entry_dto_positive() -> None:
    """Verify positive instantiation and attribute typing of StepTelemetryEntryDTO."""
    dto = StepTelemetryEntryDTO(
        model_strategy="fast",
        physical_model="gemini-2.5-flash",
        system_fingerprint="fp_abc123",
        prompt_tokens=100,
        completion_tokens=50,
        cached_tokens=20,
        reasoning_tokens=10,
        cost_usd=0.0005,
        chunk_count=2,
    )
    assert dto.model_strategy == "fast"
    assert dto.physical_model == "gemini-2.5-flash"
    assert dto.system_fingerprint == "fp_abc123"
    assert dto.prompt_tokens == 100
    assert dto.completion_tokens == 50
    assert dto.cached_tokens == 20
    assert dto.reasoning_tokens == 10
    assert dto.cost_usd == 0.0005
    assert dto.chunk_count == 2


def test_step_telemetry_entry_dto_defaults() -> None:
    """Verify default values for optional and numeric fields."""
    dto = StepTelemetryEntryDTO(model_strategy="reasoning")
    assert dto.model_strategy == "reasoning"
    assert dto.physical_model is None
    assert dto.system_fingerprint is None
    assert dto.prompt_tokens == 0
    assert dto.completion_tokens == 0
    assert dto.cached_tokens == 0
    assert dto.reasoning_tokens == 0
    assert dto.cost_usd == 0.0
    assert dto.chunk_count == 0


def test_step_telemetry_entry_dto_negative_tokens() -> None:
    """ISTQB negative test: negative token counts or cost raise ValidationError."""
    with pytest.raises(ValidationError):
        StepTelemetryEntryDTO(model_strategy="fast", prompt_tokens=-1)

    with pytest.raises(ValidationError):
        StepTelemetryEntryDTO(model_strategy="fast", cost_usd=-0.01)


def test_step_telemetry_entry_dto_extra_forbidden() -> None:
    """Verify extra forbidden enforcement."""
    with pytest.raises(ValidationError):
        StepTelemetryEntryDTO(model_strategy="fast", unknown_field=123)  # type: ignore[call-arg]
