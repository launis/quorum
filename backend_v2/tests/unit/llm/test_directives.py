"""Unit tests for backend_v2/llm/directives.py."""

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.directives import (
    STUDIO_DISCOVER_SLOP_PHRASES,
    STUDIO_TRANSLATE_SLOP_PHRASES,
)


def _validate_directive_sequence(directives: list[str]) -> list[str]:
    """Validate that a directive list contains only non-empty English plain-text instructions.

    Args:
        directives: Sequence of prompt directive strings to validate.

    Returns:
        Validated list of directive strings.

    Raises:
        AppException: With VALIDATION_FAILED if directives are empty, contain blank lines,
            embed raw XML wrapper tags, or include non-English/Finnish tokens.
    """
    if not directives:
        raise AppException(
            message="Directive sequence must not be empty.",
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    banned_tokens = ("käännöskukkasia", "<system_directive>", "<role>", "<objective>")
    for item in directives:
        cleaned = item.strip()
        if not cleaned:
            raise AppException(
                message="Directive item must not be empty or whitespace-only.",
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        if not cleaned.isascii():
            raise AppException(
                message="Directive item must contain strictly ASCII English text.",
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        for token in banned_tokens:
            if token in cleaned:
                raise AppException(
                    message=f"Forbidden token '{token}' detected in directive.",
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
    return directives


def test_discover_slop_phrases_positive_contract() -> None:
    """Positive: verify STUDIO_DISCOVER_SLOP_PHRASES contains expected English discovery instructions."""
    validated = _validate_directive_sequence(STUDIO_DISCOVER_SLOP_PHRASES)
    assert len(validated) == 2
    assert "Return a list of heavily overused phrases (1-4 words max per phrase)." in validated
    assert "Output must strictly be in the requested target language." in validated


def test_translate_slop_phrases_positive_contract() -> None:
    """Positive: verify STUDIO_TRANSLATE_SLOP_PHRASES contains English calque and deduplication instructions."""
    validated = _validate_directive_sequence(STUDIO_TRANSLATE_SLOP_PHRASES)
    assert len(validated) == 2
    assert (
        "Translate them intentionally literally as 'translation flowers' (calques in the requested target language)."
        in validated
    )
    assert "Do NOT return words that are already in the existing_words list." in validated


def test_directives_negative_non_english_and_xml_partition() -> None:
    """Negative (ISTQB Partition): verify non-English Finnish terms and raw XML tags are absent and rejected."""
    all_directives = STUDIO_DISCOVER_SLOP_PHRASES + STUDIO_TRANSLATE_SLOP_PHRASES
    for phrase in all_directives:
        assert "käännöskukkasia" not in phrase
        assert "<" not in phrase and ">" not in phrase
        assert phrase.isascii()

    with pytest.raises(AppException) as exc_info:
        _validate_directive_sequence(["Translate as käännöskukkasia."])
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_info_xml:
        _validate_directive_sequence(["<system_directive>Return phrases.</system_directive>"])
    assert exc_info_xml.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_directives_negative_empty_boundary_partition() -> None:
    """Negative (ISTQB Boundary Value Analysis): verify empty list and whitespace-only directive raise AppException."""
    with pytest.raises(AppException) as exc_empty:
        _validate_directive_sequence([])
    assert exc_empty.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_blank:
        _validate_directive_sequence(["   "])
    assert exc_blank.value.error_code == ErrorCodes.VALIDATION_FAILED.value
