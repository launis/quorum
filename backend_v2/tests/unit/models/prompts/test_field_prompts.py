"""Unit tests for field_prompts.py."""

from backend_v2.models.prompts.field_prompts import DESC_CONTEXTUAL_OVERRIDE, DESC_EXACT_QUOTES


def test_field_prompts_constants():
    """Verify that field_prompts constants are valid strings."""
    assert isinstance(DESC_EXACT_QUOTES, str)
    assert isinstance(DESC_CONTEXTUAL_OVERRIDE, str)
    assert len(DESC_EXACT_QUOTES) > 0
    assert len(DESC_CONTEXTUAL_OVERRIDE) > 0


def test_escape_hatch_present_in_exact_quotes():
    """Verify that the Escape Hatch is present in DESC_EXACT_QUOTES."""
    assert "return an empty list []" in DESC_EXACT_QUOTES
