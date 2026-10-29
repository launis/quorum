"""Tests for PromptContextDTO."""

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

from backend_v2.models.dtos.prompt_context import PromptContextDTO
from backend_v2.models.llm import LLMMessageDTO


class LLMMessageDTOFactory(ModelFactory[LLMMessageDTO]):
    """Polyfactory for LLMMessageDTO."""

    __model__ = LLMMessageDTO
    role = "user"
    content = "factory message"


class PromptContextDTOFactory(ModelFactory[PromptContextDTO]):
    """Polyfactory for PromptContextDTO."""

    __model__ = PromptContextDTO

    @classmethod
    def static_messages(cls) -> list[LLMMessageDTO]:
        """Build default static_messages list.

        Returns:
            List containing a single static system LLMMessageDTO.
        """
        return [LLMMessageDTOFactory.build(role="system", content="static prefix")]

    @classmethod
    def dynamic_messages(cls) -> list[LLMMessageDTO]:
        """Build default dynamic_messages list.

        Returns:
            List containing a single dynamic user LLMMessageDTO.
        """
        return [LLMMessageDTOFactory.build(role="user", content="dynamic tail")]

    @classmethod
    def metadata(cls) -> dict[str, int | str]:
        """Build default JSON-compatible metadata dictionary.

        Returns:
            Dictionary with sample token proxy metadata.
        """
        return {"token_proxy_score": 42}


def test_prompt_context_dto_instantiation() -> None:
    """Test that PromptContextDTO can be instantiated correctly via Polyfactory and direct kwargs."""
    factory_dto = PromptContextDTOFactory.build()
    assert len(factory_dto.static_messages) == 1
    assert factory_dto.static_messages[0].role == "system"
    assert len(factory_dto.dynamic_messages) == 1
    assert factory_dto.dynamic_messages[0].role == "user"
    assert factory_dto.metadata["token_proxy_score"] == 42

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
    """Test that PromptContextDTO has correct empty defaults (ISTQB 0-element boundary)."""
    dto = PromptContextDTO.model_validate({})

    assert dto.static_messages == []
    assert dto.dynamic_messages == []
    assert dto.metadata == {}


def test_prompt_context_dto_rejects_extra_fields() -> None:
    """Negative test: PromptContextDTO enforces extra='forbid' on unrecognized keys."""
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        PromptContextDTO.model_validate(
            {
                "static_messages": [],
                "dynamic_messages": [],
                "metadata": {},
                "unauthorized_field": "forbidden",
            }
        )


def test_prompt_context_dto_rejects_invalid_field_types() -> None:
    """Negative test: PromptContextDTO enforces strict=True against invalid field and element types."""
    with pytest.raises(ValidationError):
        PromptContextDTO.model_validate({"static_messages": "not-a-list"})

    with pytest.raises(ValidationError):
        PromptContextDTO.model_validate({"dynamic_messages": ["raw-string-instead-of-dto"]})

    with pytest.raises(ValidationError):
        PromptContextDTO.model_validate({"metadata": ["not-a-dict"]})


def test_prompt_context_dto_rejects_invalid_nested_message_role_boundary() -> None:
    """Negative test: PromptContextDTO rejects nested LLMMessageDTO violating min_length=1 role boundary."""
    with pytest.raises(ValidationError):
        PromptContextDTO.model_validate(
            {
                "static_messages": [{"role": "", "content": "empty role boundary violation"}],
            }
        )

    with pytest.raises(ValidationError):
        PromptContextDTO.model_validate(
            {
                "dynamic_messages": [{"role": "user"}],
            }
        )


def test_prompt_context_dto_enforces_frozen_immutability() -> None:
    """Negative test: PromptContextDTO enforces frozen=True against in-place attribute mutation."""
    dto = PromptContextDTOFactory.build()

    with pytest.raises(ValidationError, match="Instance is frozen"):
        dto.__setattr__("static_messages", [])

    with pytest.raises(ValidationError, match="Instance is frozen"):
        dto.__setattr__("dynamic_messages", [])

    with pytest.raises(ValidationError, match="Instance is frozen"):
        dto.__setattr__("metadata", {})
