from unittest.mock import AsyncMock
"""Tests for the translation service."""

import pytest

from backend_v2.models.prompts.global_mandates import LANGUAGE_MANDATE
from backend_v2.services.translation_service import build_linguistic_context, translate_text


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


def test_build_linguistic_context_md_structure() -> None:
    """Verify proper XML header wrapping and mandate inclusion."""
    result = build_linguistic_context(target_locale="en", include_mandate=True)

    assert result.startswith("<linguistic_context>")
    assert LANGUAGE_MANDATE in result


@pytest.mark.anyio
async def test_translate_text_early_returns() -> None:
    """Verify translate_text early exit conditions return original text."""
    assert await translate_text("", "fi", object()) == ""
    assert await translate_text("Hello", "en", object()) == "Hello"
    assert await translate_text("Hello", "fi", None) == "Hello"


@pytest.mark.anyio
async def test_translate_text_exception_fallback() -> None:
    """Verify translate_text handles execution failures gracefully."""
    dummy_client = object()
    result = await translate_text("Sitra", "fi", dummy_client)
    assert result == "Sitra"
