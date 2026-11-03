"""Unit tests for Two-Tier Length Budget Enforcer."""

import logging

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.length_budget_enforcer import enforce_sentence_boundary_budget


def test_enforce_budget_below_limit_passthrough() -> None:
    """Inputs well below character budget must be returned unchanged."""
    text = "This is a concise executive summary observation. It has multiple sentences."
    result = enforce_sentence_boundary_budget(text, max_chars=200)
    assert result == text


def test_enforce_budget_exact_limit_passthrough() -> None:
    """Inputs matching exact character limit must pass through without mutation."""
    text = "Exact boundary."
    result = enforce_sentence_boundary_budget(text, max_chars=len(text))
    assert result == text


def test_enforce_budget_exceeding_clean_sentence_trim() -> None:
    """Inputs exceeding limit with punctuation in 60-100% window must be trimmed cleanly at sentence end."""
    sentence1 = "Strategic leadership requires disciplined cognitive reflection."
    sentence2 = "Operational efficiency must balance long-term organizational agility."
    sentence3 = "Excessive third sentence that pushes the character budget beyond allowable limits."
    full_text = f"{sentence1} {sentence2} {sentence3}"

    # Budget allows sentence 1 and sentence 2, but not sentence 3
    budget = len(sentence1) + 1 + len(sentence2) + 15
    result = enforce_sentence_boundary_budget(full_text, max_chars=budget)

    assert result == f"{sentence1} {sentence2}"
    assert result.endswith(".")
    assert len(result) <= budget


def test_enforce_budget_punctuation_in_50_to_60_percent_window_succeeds_without_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Inputs with a sentence boundary in the [50%, 60%) window (130 of 250 chars) succeed without warning."""
    first_sentence = "A" * 129 + "."
    assert len(first_sentence) == 130
    second_sentence = " " + ("B" * 140) + "."
    full_text = first_sentence + second_sentence

    with caplog.at_level(logging.WARNING):
        result = enforce_sentence_boundary_budget(full_text, max_chars=250)

    assert result == first_sentence
    assert caplog.records == []


def test_enforce_budget_no_punctuation_in_window_preserves_first_sentence(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """When no boundary exists in 50-100% window, first complete sentence (<50%) is preserved with warning."""
    first = "Initial critical insight."
    long_tail = " A" + " massive continuous narrative clause without any internal period" * 5
    full_text = first + long_tail
    budget = 100

    with caplog.at_level(logging.WARNING):
        result = enforce_sentence_boundary_budget(full_text, max_chars=budget)
    assert result == first
    assert "No sentence boundary in 50-100% window of budget 100" in caplog.text


def test_enforce_budget_single_unbroken_sentence_word_boundary_trim() -> None:
    """A single unbroken sentence exceeding budget is trimmed at the last word boundary with a period."""
    unbroken = "This is an unbroken sentence that goes on and on and on without any terminal punctuation anywhere"
    budget = 40

    result = enforce_sentence_boundary_budget(unbroken, max_chars=budget)
    assert len(result) <= budget
    assert result.endswith(".")
    assert not result.endswith("  .")


def test_enforce_budget_empty_or_whitespace_raises() -> None:
    """Empty or whitespace-only inputs must raise AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        enforce_sentence_boundary_budget("", max_chars=100)
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_info2:
        enforce_sentence_boundary_budget("   \n\t  ", max_chars=100)
    assert exc_info2.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_enforce_budget_invalid_max_chars_raises() -> None:
    """Non-positive max_chars must raise AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        enforce_sentence_boundary_budget("Valid text.", max_chars=0)
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_info2:
        enforce_sentence_boundary_budget("Valid text.", max_chars=-10)
    assert exc_info2.value.error_code == ErrorCodes.VALIDATION_FAILED.value
