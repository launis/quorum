"""Tests for the translation service."""

import pytest

from backend_v2.models.prompts.common import (
    STATIC_LINGUISTIC_PROTOCOL,
    build_linguistic_parameters,
)
from backend_v2.services.translation_service import translate_text


def test_build_linguistic_parameters_default_source() -> None:
    """Verify default source language and English reasoning."""
    result = build_linguistic_parameters(target_locale="fi")

    assert "<source_data_language>Unknown/Original</source_data_language>" in result
    assert "<required_output_language>fi</required_output_language>" in result
    assert "<required_reasoning_language>English</required_reasoning_language>" in result


def test_build_linguistic_parameters_custom_source() -> None:
    """Verify custom source language is injected."""
    result = build_linguistic_parameters(target_locale="sv", source_language="de")

    assert "<source_data_language>de</source_data_language>" in result
    assert "<required_output_language>sv</required_output_language>" in result
    assert "<required_reasoning_language>English</required_reasoning_language>" in result


def test_static_linguistic_protocol_structure() -> None:
    """Verify the static protocol covers linguistic mandate and isolation rules."""
    assert "<linguistic_mandate>" in STATIC_LINGUISTIC_PROTOCOL
    assert "reasoning_trace" in STATIC_LINGUISTIC_PROTOCOL
    assert "English" in STATIC_LINGUISTIC_PROTOCOL
    assert STATIC_LINGUISTIC_PROTOCOL.startswith("<linguistic_mandate>")


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
