"""Execution prompt context definition."""

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO


class PromptContextDTO(BaseDTO):
    """Execution prompt context containing exact compilation boundaries."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    static_messages: Annotated[
        list[dict[str, Any]],
        Field(
            description="Globally identical content across all chunks (base system prompt + source document).",
            default_factory=list,
        ),
    ]
    dynamic_messages: Annotated[
        list[dict[str, Any]],
        Field(
            description="Per-chunk/per-retry content (rubrics, atoms, execution params, healing errors).",
            default_factory=list,
        ),
    ]
    metadata: Annotated[
        dict[str, Any],
        Field(description="Arbitrary execution metadata (e.g., token proxy scores).", default_factory=dict),
    ]
