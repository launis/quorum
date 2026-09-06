"""Unit tests for the Linguistic Directives module.

Note: The core functionality is tested extensively via `test_translation_service.py`
and `test_prompt_integration_epic90.py`. This file exists to satisfy the strict
1:1 File-to-Test matching mandate of the Universal Quality Gate (backend_audit_loop.py).
"""

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


def test_static_linguistic_protocol_structure() -> None:
    """Verify STATIC_LINGUISTIC_PROTOCOL structure and isolation rules."""
    assert "<linguistic_mandate>" in STATIC_LINGUISTIC_PROTOCOL
    assert "reasoning_trace" in STATIC_LINGUISTIC_PROTOCOL
    assert "English" in STATIC_LINGUISTIC_PROTOCOL


def test_translation_mandate_constant() -> None:
    """Verify DESC_TRANSLATION_MANDATE constant."""
    assert isinstance(DESC_TRANSLATION_MANDATE, str)
    assert len(DESC_TRANSLATION_MANDATE) > 0
