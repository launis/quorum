"""Ingress Data Transfer Objects for Cognitive Quorum V2.

Defines strict models for conversational boundary extraction, turn anchoring,
and multi-channel payload validation.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.inputs import IngressInputValue
from backend_v2.models.dtos.base import BaseDTO

__all__ = [
    "ChatTurnAnchorDTO",
    "ChatTurnAnchorsResponseDTO",
    "PdfBlockSignatureDTO",
    "PdfCellCoordinatesDTO",
    "PdfTextBlockDTO",
    "RawTurnDTO",
    "ResolvedIngressDTO",
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

    turns: Annotated[list[ChatTurnAnchorDTO], Field(default_factory=list, description="List of detected turn anchors")]


class ResolvedIngressDTO(BaseDTO):
    """Immutable resolved workflow inputs and source identity manifest.

    Attributes:
        resolved_inputs: Resolved inputs mapped strictly to target ExpectedInput keys or dynamic slots.
        source_identity_manifest: Human-readable source identity manifest mapping slot keys to original source names.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    resolved_inputs: Annotated[
        dict[str, IngressInputValue],
        Field(description="Resolved inputs mapped strictly to target ExpectedInput keys or dynamic slots."),
    ]
    source_identity_manifest: Annotated[
        dict[str, str],
        Field(description="Human-readable source identity manifest mapping slot keys to original source names."),
    ]


class PdfCellCoordinatesDTO(V2CoreBase):
    """Coordinates for a table cell in a PDF.

    Attributes:
        x0: Left horizontal coordinate.
        y0: Top vertical coordinate.
        x1: Right horizontal coordinate.
        y1: Bottom vertical coordinate.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    x0: Annotated[float, Field(description="Left horizontal coordinate")]
    y0: Annotated[float, Field(description="Top vertical coordinate")]
    x1: Annotated[float, Field(description="Right horizontal coordinate")]
    y1: Annotated[float, Field(description="Bottom vertical coordinate")]


class PdfTextBlockDTO(V2CoreBase):
    """Text block extracted from PDF page.

    Attributes:
        x0: Left horizontal coordinate.
        y0: Top vertical coordinate.
        x1: Right horizontal coordinate.
        y1: Bottom vertical coordinate.
        text: Extracted block text content.
        block_no: Sequential block number on page.
        block_type: Block type flag from PyMuPDF.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    x0: Annotated[float, Field(description="Left horizontal coordinate")]
    y0: Annotated[float, Field(description="Top vertical coordinate")]
    x1: Annotated[float, Field(description="Right horizontal coordinate")]
    y1: Annotated[float, Field(description="Bottom vertical coordinate")]
    text: Annotated[str, Field(description="Extracted block text content")]
    block_no: Annotated[int, Field(description="Sequential block number on page")]
    block_type: Annotated[int, Field(description="Block type flag from PyMuPDF")]


class RawTurnDTO(V2CoreBase):
    """Intermediate extracted conversational turn.

    Attributes:
        role: Speaker role: user or ai.
        content: Turn message content.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    role: Annotated[str, Field(description="Speaker role: user or ai")]
    content: Annotated[str, Field(description="Turn message content")]


class PdfBlockSignatureDTO(V2CoreBase):
    """Coordinate-level signature for text block deduplication.

    Attributes:
        page_idx: Zero-indexed page number.
        x0: Rounded left horizontal coordinate.
        y0: Rounded top vertical coordinate.
        x1: Rounded right horizontal coordinate.
        y1: Rounded bottom vertical coordinate.
        text: Sanitized text content.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    page_idx: Annotated[int, Field(description="Zero-indexed page number")]
    x0: Annotated[float, Field(description="Rounded left horizontal coordinate")]
    y0: Annotated[float, Field(description="Rounded top vertical coordinate")]
    x1: Annotated[float, Field(description="Rounded right horizontal coordinate")]
    y1: Annotated[float, Field(description="Rounded bottom vertical coordinate")]
    text: Annotated[str, Field(description="Sanitized text content")]
