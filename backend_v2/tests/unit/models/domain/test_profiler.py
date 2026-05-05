import pytest
from pydantic import ValidationError

from backend_v2.models.domain.profiler import (
    ProfilerInput,
    ProfilerMetrics,
    TextMetrics,
    BehavioralMetrics,
    ProfilerOutput,
)


def test_profiler_input_requires_chatlog() -> None:
    """Test that ProfilerInput requires chat_log."""
    data = {"profiler_metrics": None}
    with pytest.raises(ValidationError):
        ProfilerInput.model_validate(data)


def test_profiler_input_forbids_extra() -> None:
    """Test that ProfilerInput forbids extra fields via V2CoreBase."""
    data = {"chat_log": "Valid log.", "extra_field": "Should fail"}
    with pytest.raises(ValidationError):
        ProfilerInput.model_validate(data)


def test_text_metrics_validates_constraints() -> None:
    """Test TextMetrics field constraints (e.g. ge=0.0)."""
    data = {
        "word_count": -1,
        "sentence_count": 0,
        "avg_sentence_length": 0.0,
        "lexical_diversity": 0.0,
        "capitalization_ratio": 0.0,
    }
    with pytest.raises(ValidationError):
        TextMetrics.model_validate(data)


def test_profiler_metrics_combines_and_forbids_extra() -> None:
    """Test ProfilerMetrics combines TextMetrics and BehavioralMetrics and forbids extra."""
    data = {
        "word_count": 100,
        "sentence_count": 10,
        "avg_sentence_length": 10.0,
        "lexical_diversity": 0.5,
        "capitalization_ratio": 0.1,
        "say_do_gap": 0.0,
        "automation_bias": 0.0,
        "illusion_of_competence": 0.0,
        "imperative_command_count": 5,
        "unknown_metric": 123,
    }
    with pytest.raises(ValidationError):
        ProfilerMetrics.model_validate(data)


def test_profiler_output_frozen_and_strict() -> None:
    """Test that ProfilerOutput rejects unknown fields and is frozen."""
    data = {
        "author_intent": "Seeking help",
        "cognitive_biases": ["Confirmation Bias"],
        "emotional_tone": "Frustrated",
        "reasoning_trace": "Analysis complete.",
        "calculation_log": [],
        "rogue_field": "Should fail",
    }
    with pytest.raises(ValidationError):
        ProfilerOutput.model_validate(data)
