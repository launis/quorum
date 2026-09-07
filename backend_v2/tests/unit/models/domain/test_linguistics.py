"""Unit tests for linguistics domain DTOs and extraction logic."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.linguistics import (
    DynamicLinguisticsExtractorDTO,
    LinguisticsPayloadDTO,
    LinguisticsResultDTO,
    PerformativePatternDTO,
)


def test_linguistics_payload_dto_extract_language() -> None:
    """Test extract_language logic with various inputs."""
    dto1 = LinguisticsPayloadDTO(dynamic_inputs={})
    assert dto1.extract_language({"language": "fi-FI"}) == "fi"

    dto2 = LinguisticsPayloadDTO(language="sv-SE", dynamic_inputs={})
    assert dto2.extract_language({}) == "sv"

    dto3 = LinguisticsPayloadDTO(dynamic_inputs={})
    assert dto3.extract_language({}) == "en"


def test_linguistics_payload_dto_get_text_to_scan() -> None:
    """Test text aggregation and user-only prioritization."""
    # Prioritizes chat_log_user_only
    dto_user = LinguisticsPayloadDTO(
        dynamic_inputs={"chat_log": "system info", "chat_log_user_only": "User message only."}
    )
    assert dto_user.get_text_to_scan() == "user message only."

    # Handles nested lists, dicts, numbers
    dto_nested = LinguisticsPayloadDTO(
        dynamic_inputs={
            "str_field": "Hello",
            "num_field": 42,
            "float_field": 3.14,
            "bool_field": True,  # booleans excluded
            "none_field": None,
            "list_field": ["World", ["Deep", 100]],
            "dict_field": {"inner": "Text", "sub_num": 99},
        }
    )
    scanned = dto_nested.get_text_to_scan()
    assert "hello" in scanned
    assert "42" in scanned
    assert "3.14" in scanned
    assert "true" not in scanned
    assert "world" in scanned
    assert "deep" in scanned
    assert "text" in scanned


def test_dynamic_linguistics_extractor_dto() -> None:
    """Test DynamicLinguisticsExtractorDTO validation."""
    dto = DynamicLinguisticsExtractorDTO(detected_phrases=["delve into", "syventyä"])
    assert dto.detected_phrases == ["delve into", "syventyä"]

    # Strict and extra forbid
    with pytest.raises(ValidationError):
        DynamicLinguisticsExtractorDTO.model_validate({"detected_phrases": [], "extra": 123})


def test_performative_pattern_dto() -> None:
    """Test PerformativePatternDTO validation."""
    pattern = PerformativePatternDTO(
        pattern_id="pat_1",
        detected_phrase="delve into",
        category="performative_filler",
    )
    assert pattern.pattern_id == "pat_1"
    assert pattern.detected_phrase == "delve into"
    assert pattern.category == "performative_filler"

    with pytest.raises(ValidationError):
        PerformativePatternDTO(pattern_id="", detected_phrase="delve", category="cat")


def test_linguistics_result_dto() -> None:
    """Test LinguisticsResultDTO aggregation."""
    res = LinguisticsResultDTO(
        performative_patterns=[
            PerformativePatternDTO(
                pattern_id="pat_1",
                detected_phrase="delve",
                category="filler",
            )
        ]
    )
    assert len(res.performative_patterns) == 1
    assert res.performative_patterns[0].detected_phrase == "delve"
