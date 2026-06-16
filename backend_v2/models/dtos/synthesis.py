"""Synthesis LLM payload models.

Strict Pydantic V2 definitions for the SSOT. Contains structured inputs and
outputs of the reporting synthesis pipeline.
"""

from typing import Annotated

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.view.sdui import AnySduiBlock


class SynthesisSectionDTO(V2CoreBase):
    """DTO representing a single synthesized section within a larger layout structure.

    Attributes:
        layout_id: The EXACT layout ID provided in the section instructions.
        content_blocks: Structured SDUI content blocks for this section.
    """

    layout_id: Annotated[str, Field(description="The EXACT layout ID provided in the section instructions")]
    content_blocks: Annotated[
        list[AnySduiBlock], Field(default_factory=list, description="Structured SDUI content blocks for this section")
    ]


class XaiHighlightItem(V2CoreBase):
    """DTO representing a highly contextual, structured XAI highlight or tip.

    Attributes:
        extension_type: Category of the insight matching explicit system XaiExtensionType options.
        content: The synthesized, deduplicated insight or tip. Max 2 sentences.
    """

    extension_type: Annotated[
        str,
        Field(description="Category of the insight matching explicit system XaiExtensionType options."),
    ]
    content: Annotated[str, Field(description="The synthesized, deduplicated insight or tip. Max 2 sentences.")]


class SynthesisRowExplanationDTO(V2CoreBase):
    """DTO providing a short context explanation for a specific matrix mapping row.

    Attributes:
        matrix_id: The ID of the matrix.
        row_explanation: The ultra-short synthesized explanation.
    """

    matrix_id: Annotated[str, Field(description="The ID of the matrix")]
    row_explanation: Annotated[str, Field(description="The ultra-short synthesized explanation")]


class MatrixExplanationsResult(V2CoreBase):
    """Container for the batch of generated row explanations.

    Attributes:
        explanations: List containing EXACTLY ONE explanation for EACH matrix_id provided.
    """

    explanations: Annotated[
        list[SynthesisRowExplanationDTO],
        Field(
            description=(
                "A mandatory list containing EXACTLY ONE explanation for EACH matrix_id provided in the source_data."
            ),
        ),
    ]


class SynthesisOutputDTO(V2CoreBase):
    """Structured output expected from the Synthesis LLM.

    Attributes:
        content_blocks: The fully synthesized structured SDUI content blocks.
        cited_sources: List of references or citations found.
        section_syntheses: List of synthesized sections, mapped by their Layout ID.
        xai_highlights: The deduplicated insight items per extension category.
    """

    content_blocks: Annotated[
        list[AnySduiBlock],
        Field(default_factory=list, description="The fully synthesized structured SDUI content blocks."),
    ]
    cited_sources: Annotated[
        list[str], Field(default_factory=list, description="List of references or citations found.")
    ]
    section_syntheses: Annotated[
        list[SynthesisSectionDTO],
        Field(default_factory=list, description="List of synthesized sections, mapped by their Layout ID."),
    ]
    xai_highlights: Annotated[
        list[XaiHighlightItem],
        Field(
            default_factory=list,
            description="The deduplicated insight items per extension category, up to the requested maximum count.",
        ),
    ]
