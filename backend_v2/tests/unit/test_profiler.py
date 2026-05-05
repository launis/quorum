"""Unit tests for Profiler Agent Domain Models."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.profiler import (
    BehavioralMetrics,
    ProfilerDTO,
    ProfilerInput,
    ProfilerMetrics,
    ProfilerOutput,
    TextMetrics,
)


def test_profiler_input_valid() -> None:
    inp = ProfilerInput(chat_log="Hello")
    assert inp.chat_log == "Hello"


def test_profiler_input_empty_chat_log_fails() -> None:
    with pytest.raises(ValidationError):
        ProfilerInput(chat_log="")


def test_profiler_input_extra_allowed() -> None:
    inp = ProfilerInput.model_validate({"chat_log": "Hello", "extra": "Allowed"})
    assert inp.chat_log == "Hello"


def test_text_metrics_valid() -> None:
    tm = TextMetrics(
        word_count=10,
        sentence_count=2,
        avg_sentence_length=5.0,
        lexical_diversity=0.8,
        capitalization_ratio=0.1,
        control_ratio=0.5,
    )
    assert tm.word_count == 10


def test_text_metrics_negative_fails() -> None:
    with pytest.raises(ValidationError):
        TextMetrics(
            word_count=-1,
            sentence_count=2,
            avg_sentence_length=5.0,
            lexical_diversity=0.8,
            capitalization_ratio=0.1,
            control_ratio=0.5,
        )


def test_behavioral_metrics_valid() -> None:
    bm = BehavioralMetrics(
        say_do_gap=0.1,
        automation_bias=0.2,
        illusion_of_competence=0.3,
        imperative_command_count=5,
    )
    assert bm.imperative_command_count == 5


def test_behavioral_metrics_negative_fails() -> None:
    with pytest.raises(ValidationError):
        BehavioralMetrics(
            say_do_gap=-0.1,
            automation_bias=0.2,
            illusion_of_competence=0.3,
            imperative_command_count=5,
        )


def test_profiler_metrics_valid() -> None:
    pm = ProfilerMetrics(
        word_count=10,
        sentence_count=2,
        avg_sentence_length=5.0,
        lexical_diversity=0.8,
        capitalization_ratio=0.1,
        control_ratio=0.5,
        say_do_gap=0.1,
        automation_bias=0.2,
        illusion_of_competence=0.3,
        imperative_command_count=5,
    )
    assert pm.word_count == 10
    assert pm.say_do_gap == 0.1


def test_profiler_dto_valid() -> None:
    dto = ProfilerDTO(
        thought_process="Thinking",
        conclusion="Done",
        confidence_score=0.9,
        author_intent="Intent",
        cognitive_biases=["Bias"],
        emotional_tone="Happy",
    )
    assert dto.author_intent == "Intent"


def test_profiler_dto_empty_strings_fails() -> None:
    with pytest.raises(ValidationError):
        ProfilerDTO(
            thought_process="Thinking",
            conclusion="Done",
            confidence_score=0.9,
            author_intent="",
            cognitive_biases=["Bias"],
            emotional_tone="Happy",
        )
    with pytest.raises(ValidationError):
        ProfilerDTO(
            thought_process="Thinking",
            conclusion="Done",
            confidence_score=0.9,
            author_intent="Intent",
            cognitive_biases=[],
            emotional_tone="Happy",
        )


def test_profiler_output_valid() -> None:
    out = ProfilerOutput(
        thought_process="Thinking",
        conclusion="Done",
        confidence_score=0.9,
        author_intent="Intent",
        cognitive_biases=["Bias"],
        emotional_tone="Happy",
    )
    assert out.conclusion == "Done"
