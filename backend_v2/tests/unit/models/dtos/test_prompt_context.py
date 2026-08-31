"""Tests for PromptContextDTO."""

from backend_v2.models.dtos.prompt_context import PromptContextDTO
from backend_v2.models.llm import LLMMessageDTO


def test_prompt_context_dto_instantiation() -> None:
    """Test that PromptContextDTO can be instantiated correctly."""
    dto = PromptContextDTO(
        static_messages=[LLMMessageDTO(role="system", content="test")],
        dynamic_messages=[LLMMessageDTO(role="user", content="test2")],
        metadata={"key": "value"},
    )

    assert len(dto.static_messages) == 1
    assert dto.static_messages[0].role == "system"
    assert dto.static_messages[0].content == "test"
    assert len(dto.dynamic_messages) == 1
    assert dto.dynamic_messages[0].role == "user"
    assert dto.dynamic_messages[0].content == "test2"
    assert dto.metadata["key"] == "value"


def test_prompt_context_dto_defaults() -> None:
    """Test that PromptContextDTO has correct defaults."""
    dto = PromptContextDTO()

    assert dto.static_messages == []
    assert dto.dynamic_messages == []
    assert dto.metadata == {}
