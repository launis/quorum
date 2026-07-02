"""Unit tests for CompiledPrompt models to verify Pydantic V2 validations and role merging."""

import pytest
from pydantic import ValidationError

from backend_v2.models.prompt import CompiledPrompt


def test_compiled_prompt_pydantic_strictness() -> None:
    """Verifies that CompiledPrompt enforces strict type constraints and extra='forbid'."""
    # Valid instantiations
    prompt = CompiledPrompt(
        static_messages=[{"role": "system", "content": "Static prompt"}],
        dynamic_messages=[{"role": "user", "content": "Dynamic instruction"}],
    )
    assert len(prompt.static_messages) == 1
    assert len(prompt.dynamic_messages) == 1

    # Extra fields must raise ValidationError
    with pytest.raises(ValidationError):
        CompiledPrompt(
            static_messages=[{"role": "system", "content": "Static"}],
            dynamic_messages=[{"role": "user", "content": "Dynamic"}],
            invalid_extra_field="error",  # type: ignore[call-arg]
        )


def test_compiled_prompt_to_flat_messages_role_merging() -> None:
    """Verifies that to_flat_messages flattens list and merges consecutive messages with identical roles."""
    static_messages = [
        {"role": "system", "content": "System mandate"},
        {"role": "user", "content": "<source_data>Verbatim content</source_data>"},
    ]
    dynamic_messages = [
        {"role": "user", "content": "<execution_parameters>Strictness=85</execution_parameters>"},
        {"role": "user", "content": "<PREVIOUS_SCHEMA_ERROR>Syntax error</PREVIOUS_SCHEMA_ERROR>"},
    ]

    prompt = CompiledPrompt(static_messages=static_messages, dynamic_messages=dynamic_messages)

    flat = prompt.to_flat_messages()

    # The system message is untouched
    assert len(flat) == 2
    assert flat[0]["role"] == "system"
    assert flat[0]["content"] == "System mandate"

    # Consecutive user messages are merged into a single user message
    assert flat[1]["role"] == "user"
    expected_content = (
        "<source_data>Verbatim content</source_data>\n\n"
        "<execution_parameters>Strictness=85</execution_parameters>\n\n"
        "<PREVIOUS_SCHEMA_ERROR>Syntax error</PREVIOUS_SCHEMA_ERROR>"
    )
    assert flat[1]["content"] == expected_content
