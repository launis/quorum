"""Tests for the centralized linguistic directive module."""

from backend_v2.llm.linguistic import LANGUAGE_MANDATE, build_linguistic_context


def test_build_linguistic_context_default_source() -> None:
    """Verify default source language and English reasoning."""
    result = build_linguistic_context(target_locale="fi")

    assert "<source_data_language>Unknown/Original</source_data_language>" in result
    assert "<required_output_language>fi</required_output_language>" in result
    assert "<required_reasoning_language>English</required_reasoning_language>" in result


def test_build_linguistic_context_custom_source() -> None:
    """Verify custom source language is injected."""
    result = build_linguistic_context(target_locale="sv", source_language="de")

    assert "<source_data_language>de</source_data_language>" in result
    assert "<required_output_language>sv</required_output_language>" in result
    assert "<required_reasoning_language>English</required_reasoning_language>" in result


def test_language_mandate_contains_critical_fields() -> None:
    """Verify the mandate covers all user-facing XAI extension fields."""
    assert "justification" in LANGUAGE_MANDATE
    assert "coaching" in LANGUAGE_MANDATE
    assert "falsification" in LANGUAGE_MANDATE
    assert "remediation_steps" in LANGUAGE_MANDATE
    assert "evaluation_notes" in LANGUAGE_MANDATE
    assert "reasoning_trace" in LANGUAGE_MANDATE
    assert "English" in LANGUAGE_MANDATE


def test_build_linguistic_context_xml_structure() -> None:
    """Verify proper XML wrapping."""
    result = build_linguistic_context(target_locale="en")

    assert result.startswith("<linguistic_context>")
    assert result.endswith("</linguistic_context>")
