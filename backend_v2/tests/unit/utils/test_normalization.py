"""Unit tests for text normalization utilities."""

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


def test_normalize_evaluation_input_handles_empty_or_none() -> None:
    """Verify that empty inputs are handled safely without throwing exceptions."""
    assert normalize_evaluation_input("") == ""
    assert normalize_evaluation_input(None) == ""  # type: ignore[arg-type]
