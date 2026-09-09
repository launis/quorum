from __future__ import annotations

"""Ingress Data Transfer Objects for Cognitive Quorum V2.

Defines strict models for conversational boundary extraction, turn anchoring,
and multi-channel payload validation.
"""

from typing import Annotated, Literal

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO

__all__ = [
    "ChatTurnAnchorDTO",
    "ChatTurnAnchorsResponseDTO",
]


class ChatTurnAnchorDTO(BaseDTO):
    """Boundary anchor marking the exact verbatim start and end of a conversational turn.

    Attributes:
        speaker: Conversational role indicator ('user' or 'ai').
        start_phrase: The first 5-8 words of the turn verbatim to anchor position in physical text.
        end_phrase: The last 5-8 words of the turn verbatim to anchor position in physical text.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    speaker: Annotated[Literal["user", "ai"], Field(description="Turn speaker")]
    start_phrase: Annotated[str, Field(min_length=3, description="First 5-8 words of the turn verbatim")]
    end_phrase: Annotated[str, Field(min_length=3, description="Last 5-8 words of the turn verbatim")]


class ChatTurnAnchorsResponseDTO(BaseDTO):
    """Structured response containing turn boundary anchors.

    Attributes:
        turns: Sequentially ordered list of detected turn boundary anchors.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    turns: Annotated[list[ChatTurnAnchorDTO], Field(min_length=1, description="List of detected turn anchors")]
