"""Unit tests for the Linguistic Directives module.

Note: The core functionality is tested extensively via `test_translation_service.py`
and `test_prompt_integration_epic90.py`. This file exists to satisfy the strict
1:1 File-to-Test matching mandate of the Universal Quality Gate (backend_audit_loop.py).
"""

from backend_v2.models.prompts.linguistic_directives import (
    DESC_TRANSLATION_MANDATE,
    build_linguistic_context,
)


def test_build_linguistic_context_basic_execution() -> None:
    """Ensure the function executes and returns an XML-formatted string."""
    result = build_linguistic_context(target_locale="en")
    assert "<linguistic_context>" in result
    assert "<required_reasoning_language>English</required_reasoning_language>" in result
    assert "<required_output_language>en</required_output_language>" in result
    assert "semantic_reasoning" in result
    assert "contextual override" in result


def test_build_linguistic_context_with_mandate() -> None:
    """Verify that include_mandate appends LANGUAGE_MANDATE."""
    result = build_linguistic_context(target_locale="fi", include_mandate=True)
    assert "<language_mandate>" in result
    assert "<required_output_language>fi</required_output_language>" in result
    assert "CRITICAL EXCEPTION 1" in result


def test_translation_mandate_constant() -> None:
    """Verify DESC_TRANSLATION_MANDATE constant."""
    assert isinstance(DESC_TRANSLATION_MANDATE, str)
    assert len(DESC_TRANSLATION_MANDATE) > 0
