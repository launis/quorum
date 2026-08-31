"""Unit tests for CompiledPrompt models to verify Pydantic V2 validations and role merging."""

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt, PromptMetadataDTO


def test_compiled_prompt_pydantic_strictness() -> None:
    """Verifies that CompiledPrompt enforces strict type constraints and extra='forbid'."""
    # Valid instantiations
    prompt = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="system", content="Static prompt")],
        dynamic_messages=[LLMMessageDTO(role="user", content="Dynamic instruction")],
    )
    assert len(prompt.static_messages) == 1
    assert len(prompt.dynamic_messages) == 1
    assert isinstance(prompt.metadata, PromptMetadataDTO)

    # Extra fields must raise ValidationError
    with pytest.raises(ValidationError):
        CompiledPrompt(
            static_messages=[LLMMessageDTO(role="system", content="Static")],
            dynamic_messages=[LLMMessageDTO(role="user", content="Dynamic")],
            invalid_extra_field="error",  # type: ignore[call-arg]
        )


def test_compiled_prompt_to_flat_messages_role_merging() -> None:
    """Verifies that to_flat_messages flattens list and merges consecutive messages with identical roles."""
    static_messages = [
        LLMMessageDTO(role="system", content="System mandate"),
        LLMMessageDTO(role="user", content="<source_data>Verbatim content</source_data>"),
    ]
    dynamic_messages = [
        LLMMessageDTO(role="user", content="<execution_parameters>Strictness=85</execution_parameters>"),
        LLMMessageDTO(role="user", content="<PREVIOUS_SCHEMA_ERROR>Syntax error</PREVIOUS_SCHEMA_ERROR>"),
    ]

    prompt = CompiledPrompt(static_messages=static_messages, dynamic_messages=dynamic_messages)

    flat = prompt.to_flat_messages()

    # The system message is untouched
    assert len(flat) == 2
    assert flat[0].role == "system"
    assert flat[0].content == "System mandate"

    # Consecutive user messages are merged into a single user message
    assert flat[1].role == "user"
    expected_content = (
        "<source_data>Verbatim content</source_data>\n\n"
        "<execution_parameters>Strictness=85</execution_parameters>\n\n"
        "<PREVIOUS_SCHEMA_ERROR>Syntax error</PREVIOUS_SCHEMA_ERROR>"
    )
    assert flat[1].content == expected_content

    # Verify to_static_flat and to_dynamic_flat
    static_flat = prompt.to_static_flat()
    assert len(static_flat) == 2
    assert static_flat[0].role == "system"
    assert static_flat[1].role == "user"

    dynamic_flat = prompt.to_dynamic_flat()
    assert len(dynamic_flat) == 1
    assert dynamic_flat[0].role == "user"


def test_compiled_prompt_forbids_system_in_dynamic() -> None:
    """Verifies that system role is strictly prohibited in dynamic_messages."""
    with pytest.raises(AppException) as exc_info:
        CompiledPrompt(
            static_messages=[LLMMessageDTO(role="system", content="Valid system prompt")],
            dynamic_messages=[LLMMessageDTO(role="system", content="Illegal system prompt")],
        )
    assert exc_info.value.status_code == 400
    assert "ARCHITECTURE VIOLATION" in exc_info.value.message


def test_llm_message_dto_missing_required_field() -> None:
    """Verifies that missing required fields in LLMMessageDTO trigger ValidationError."""
    with pytest.raises(ValidationError):
        LLMMessageDTO(content="text")  # type: ignore[call-arg]


def test_llm_message_dto_extra_field_forbidden() -> None:
    """Verifies that extra fields in LLMMessageDTO are forbidden and raise ValidationError."""
    with pytest.raises(ValidationError):
        LLMMessageDTO(role="user", content="text", invalid_extra="value")  # type: ignore[call-arg]


def test_llm_message_dto_strict_types() -> None:
    """Verifies that non-string role types trigger ValidationError in strict mode."""
    with pytest.raises(ValidationError):
        LLMMessageDTO(role=123, content="text")  # type: ignore[arg-type]


def test_llm_message_dto_serialization_null_omission() -> None:
    """Verifies that serialization with exclude_none=True omits null fields completely."""
    msg = LLMMessageDTO(role="user", content="hello")
    dumped = msg.model_dump(mode="json", exclude_none=True)
    assert dumped == {"role": "user", "content": "hello"}
    assert "tool_calls" not in dumped
    assert "tool_call_id" not in dumped
    assert "name" not in dumped


def test_compiled_prompt_merge_flat_roles() -> None:
    """Verifies that CompiledPrompt._merge_flat correctly merges consecutive same-role messages."""
    messages = [
        LLMMessageDTO(role="user", content="First part"),
        LLMMessageDTO(role="user", content="Second part"),
    ]
    merged = CompiledPrompt._merge_flat(messages)
    assert len(merged) == 1
    assert merged[0].role == "user"
    assert merged[0].content == "First part\n\nSecond part"
