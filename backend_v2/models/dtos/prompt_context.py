"""Execution prompt context definition."""

from typing import Annotated

from pydantic import ConfigDict, Field, JsonValue

from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.llm import LLMMessageDTO

__all__ = ["PromptContextDTO"]


class PromptContextDTO(BaseDTO):
    """Execution prompt context containing exact compilation boundaries.

    Attributes:
        static_messages: Globally identical content across all chunks (base system prompt + source document).
        dynamic_messages: Per-chunk/per-retry content (rubrics, atoms, execution params, healing errors).
        metadata: Arbitrary execution metadata (e.g., token proxy scores).
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    static_messages: Annotated[
        list[LLMMessageDTO],
        Field(
            description="Globally identical content across all chunks (base system prompt + source document).",
            default_factory=list,
        ),
    ]
    dynamic_messages: Annotated[
        list[LLMMessageDTO],
        Field(
            description="Per-chunk/per-retry content (rubrics, atoms, execution params, healing errors).",
            default_factory=list,
        ),
    ]
    metadata: Annotated[
        dict[str, JsonValue],
        Field(description="Arbitrary execution metadata (e.g., token proxy scores).", default_factory=dict),
    ]
