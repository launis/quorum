"""Unit tests for text normalization utilities."""

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.utils.normalization import normalize_evaluation_input


def test_normalize_evaluation_input_strips_markdown() -> None:
    """Verify that Markdown formatting symbols are stripped successfully."""
    raw = "# Heading 1\nThis is **bold** and *italic* text with `inline code`."
    expected = "Heading 1\nThis is bold and italic text with inline code."
    assert normalize_evaluation_input(raw) == expected


def test_normalize_evaluation_input_collapses_whitespace() -> None:
    """Verify that multiple consecutive spaces and tabs are collapsed to a single space."""
    raw = "Hello   world!  This \t\t has   spaces."
    expected = "Hello world! This has spaces."
    assert normalize_evaluation_input(raw) == expected


def test_normalize_evaluation_input_collapses_empty_lines() -> None:
    """Verify that multiple consecutive empty lines are collapsed to a single empty line."""
    raw = "Paragraph 1\n\n\n\nParagraph 2\n\n\nParagraph 3"
    expected = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    assert normalize_evaluation_input(raw) == expected


def test_normalize_evaluation_input_strips_line_padding() -> None:
    """Verify that leading and trailing whitespace on each line is stripped."""
    raw = "   Line 1 with spaces   \n   Line 2 with spaces   "
    expected = "Line 1 with spaces\nLine 2 with spaces"
    assert normalize_evaluation_input(raw) == expected


def test_normalize_evaluation_input_handles_empty_and_whitespace_strings() -> None:
    """Verify that empty and whitespace-only strings return an empty string."""
    assert normalize_evaluation_input("") == ""
    assert normalize_evaluation_input("   \n\t  \n  ") == ""


def test_normalize_evaluation_input_unicode_and_quotes() -> None:
    """Verify that Unicode normalization, zero-width characters, and quotes/dashes are handled."""
    raw_nfd = "a\u0308"
    assert normalize_evaluation_input(raw_nfd) == "\u00e4"

    raw_zw = "Hello\u200bWorld\u200c!\ufeff\u00ad"
    assert normalize_evaluation_input(raw_zw) == "HelloWorld!"

    raw_quotes = "\u201cSmart double\u201d and \u2018smart single\u2019 quotes \u2014 en\u2013dash."
    expected = "\"Smart double\" and 'smart single' quotes - en-dash."
    assert normalize_evaluation_input(raw_quotes) == expected


def test_normalize_evaluation_input_rejects_null_bytes_with_app_exception() -> None:
    """Verify that embedded null bytes raise AppException with INTERNAL_SERVER_ERROR."""
    with pytest.raises(AppException) as exc_info:
        normalize_evaluation_input("Payload with\x00null byte")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details == {"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}


def test_normalize_evaluation_input_rejects_unpaired_surrogates_with_app_exception() -> None:
    """Verify that unpaired UTF-16 surrogates raise AppException with INTERNAL_SERVER_ERROR."""
    with pytest.raises(AppException) as exc_info:
        normalize_evaluation_input("Invalid surrogate \ud800 in text")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details == {"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
