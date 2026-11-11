"""Unit tests for the Linguistic Directives module.

Verifies static linguistic protocol constants, dynamic XML parameter block
construction, whitespace/case boundary normalization, and invalid input handling.
"""

from __future__ import annotations

import pytest

from backend_v2.models.prompts.common.linguistic_directives import (
    DESC_TRANSLATION_MANDATE,
    STATIC_LINGUISTIC_PROTOCOL,
    build_linguistic_parameters,
)


def test_build_linguistic_parameters_basic_execution() -> None:
    """Ensure the function executes and returns an XML-formatted parameter string."""
    result = build_linguistic_parameters(target_locale="en")
    assert "<linguistic_parameters>" in result
    assert "<required_reasoning_language>English</required_reasoning_language>" in result
    assert "<required_output_language>en</required_output_language>" in result
    assert "<source_data_language>Unknown/Original</source_data_language>" in result


def test_build_linguistic_parameters_with_custom_source() -> None:
    """Verify that source_language is correctly injected into parameters."""
    result = build_linguistic_parameters(target_locale="fi", source_language="sv")
    assert "<linguistic_parameters>" in result
    assert "<required_output_language>fi</required_output_language>" in result
    assert "<source_data_language>sv</source_data_language>" in result


def test_build_linguistic_parameters_boundary_whitespace_and_case() -> None:
    """Verify boundary whitespace stripping and lowercase normalization on target_locale."""
    result = build_linguistic_parameters(
        target_locale="  FI  ",
        source_language="  Finnish / Suomi  ",
    )
    assert "<required_output_language>fi</required_output_language>" in result
    assert "<source_data_language>Finnish / Suomi</source_data_language>" in result


def test_build_linguistic_parameters_invalid_target_locale_error() -> None:
    """Verify negative type boundary when target_locale is invalid."""
    with pytest.raises(AttributeError):
        build_linguistic_parameters(target_locale=None)


def test_build_linguistic_parameters_invalid_source_language_error() -> None:
    """Verify negative type boundary when source_language is invalid."""
    with pytest.raises(AttributeError):
        build_linguistic_parameters(target_locale="en", source_language=123)


def test_static_linguistic_protocol_structure() -> None:
    """Verify STATIC_LINGUISTIC_PROTOCOL structure and isolation rules."""
    assert "<linguistic_mandate>" in STATIC_LINGUISTIC_PROTOCOL
    assert "reasoning_trace" in STATIC_LINGUISTIC_PROTOCOL
    assert "English" in STATIC_LINGUISTIC_PROTOCOL


def test_translation_mandate_constant() -> None:
    """Verify DESC_TRANSLATION_MANDATE constant."""
    assert isinstance(DESC_TRANSLATION_MANDATE, str)
    assert len(DESC_TRANSLATION_MANDATE) > 0
