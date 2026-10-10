"""Unit tests for export evidence formatting functions.

Tests clean_citation_brackets, format_text_observations, and format_ai_reasoning
across boundary cases, empty collections, multi-item lists, and multi-line strings.
"""

from __future__ import annotations

from backend_v2.services.export_evidence_formatter import (
    clean_citation_brackets,
    format_ai_reasoning,
    format_text_observations,
)

# ============================================================================
# clean_citation_brackets Tests
# ============================================================================


def test_clean_citation_brackets_empty_and_whitespace() -> None:
    """Assert empty or whitespace strings return empty string."""
    assert clean_citation_brackets("") == ""
    assert clean_citation_brackets("   ") == ""
    assert clean_citation_brackets("\t\n") == ""


def test_clean_citation_brackets_bracketed() -> None:
    """Assert surrounding square brackets are stripped."""
    assert clean_citation_brackets("[ISO-27001 Section 4.2]") == "ISO-27001 Section 4.2"
    assert clean_citation_brackets("  [Engineering Handbook 2026]  ") == "Engineering Handbook 2026"


def test_clean_citation_brackets_quoted() -> None:
    """Assert surrounding quotation marks are stripped."""
    assert clean_citation_brackets('"Weekly sprint cadence"') == "Weekly sprint cadence"
    assert clean_citation_brackets("'Quarterly audit findings'") == "Quarterly audit findings"


def test_clean_citation_brackets_unmatched_brackets_preserved() -> None:
    """Assert unbalanced brackets or internal brackets are safely preserved."""
    assert clean_citation_brackets("[Unmatched bracket") == "[Unmatched bracket"
    assert clean_citation_brackets("Section 4 [Appendix B]") == "Section 4 [Appendix B]"


def test_clean_citation_brackets_whitespace_collapsing() -> None:
    """Assert multiple spaces or tabs are collapsed into single space."""
    assert clean_citation_brackets("Source   with   multiple    spaces") == "Source with multiple spaces"


# ============================================================================
# format_text_observations Tests
# ============================================================================


def test_format_text_observations_none_and_empty() -> None:
    """Assert None, empty string, or empty list return empty string."""
    assert format_text_observations(None) == ""
    assert format_text_observations("") == ""
    assert format_text_observations("   ") == ""
    assert format_text_observations([]) == ""
    assert format_text_observations(["", "  ", "\t"]) == ""


def test_format_text_observations_single_quote() -> None:
    """Assert single string or single item list returns stripped string."""
    assert format_text_observations("Exact evidence text.") == "Exact evidence text."
    assert format_text_observations("  Leading and trailing.  ") == "Leading and trailing."
    assert format_text_observations(["Single item in list."]) == "Single item in list."


def test_format_text_observations_multi_quote_list() -> None:
    """Assert multi-quote collections are formatted as numbered lines."""
    quotes = [
        "First evidence observation.",
        "Second corroborated finding.",
        "Third verified metric.",
    ]
    formatted = format_text_observations(quotes)
    expected = "[1] First evidence observation.\n[2] Second corroborated finding.\n[3] Third verified metric."
    assert formatted == expected


def test_format_text_observations_filters_empty_items() -> None:
    """Assert empty items in quote list are filtered out prior to numbering."""
    quotes = [
        "First observation.",
        "",
        "   ",
        "Second observation.",
    ]
    formatted = format_text_observations(quotes)
    expected = "[1] First observation.\n[2] Second observation."
    assert formatted == expected


# ============================================================================
# format_ai_reasoning Tests
# ============================================================================


def test_format_ai_reasoning_none_and_empty() -> None:
    """Assert None or empty reasoning returns empty string."""
    assert format_ai_reasoning(None) == ""
    assert format_ai_reasoning("") == ""
    assert format_ai_reasoning("   \n\t") == ""


def test_format_ai_reasoning_clean_string() -> None:
    """Assert simple reasoning string is trimmed."""
    raw = "  The process meets level 2 maturity requirements.  "
    assert format_ai_reasoning(raw) == "The process meets level 2 maturity requirements."


def test_format_ai_reasoning_crlf_normalization() -> None:
    """Assert CRLF linebreaks are normalized to LF."""
    raw = "Paragraph 1\r\n\r\nParagraph 2\r\nParagraph 3"
    expected = "Paragraph 1\n\nParagraph 2\nParagraph 3"
    assert format_ai_reasoning(raw) == expected


def test_format_ai_reasoning_collapses_excessive_newlines() -> None:
    """Assert 3+ consecutive newlines are collapsed to double newlines."""
    raw = "Paragraph 1\n\n\n\n\nParagraph 2"
    expected = "Paragraph 1\n\nParagraph 2"
    assert format_ai_reasoning(raw) == expected
