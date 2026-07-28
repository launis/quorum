"""Synthesis LLM payload models.

Strict Pydantic V2 definitions for the SSOT. Contains structured inputs and
outputs of the reporting synthesis pipeline.
"""

from typing import Annotated, Any

from pydantic import Field, model_validator

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
        list[AnySduiBlock], Field(..., description="Structured SDUI content blocks for this section")
    ]

    @model_validator(mode="before")
    @classmethod
    def _sanitize_null_collections(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("content_blocks") is None:
                data["content_blocks"] = []
            blocks = data.get("content_blocks")
            if isinstance(blocks, list):
                for b in blocks:
                    if isinstance(b, dict):
                        if "type" in b and "block_type" not in b:
                            b["block_type"] = b.pop("type")
        return data


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
    content: Annotated[
        str,
        Field(
            description="The synthesized, deduplicated insight or tip. Max 2 sentences. MUST BE TRANSLATED TO <required_output_language>!"
        ),
    ]


class SynthesisRowExplanationDTO(V2CoreBase):
    """DTO providing a short context explanation for a specific matrix mapping row.

    Attributes:
        matrix_id: The ID of the matrix.
        row_explanation: The ultra-short synthesized explanation.
        curated_quotes: Curated verbatim quotes by the LLM.
    """

    matrix_id: Annotated[str, Field(description="The ID of the matrix")]
    row_explanation: Annotated[
        str,
        Field(description="The ultra-short synthesized explanation. MUST BE TRANSLATED TO <required_output_language>!"),
    ]
    curated_quotes: Annotated[
        list[str],
        Field(default_factory=list, description="Curated verbatim quotes by the LLM"),
    ]


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
        user_role: Extracted targeted user role for the output.
        user_role_justification: LLM justification for role mapping.
        executive_summary: High-level synthesized summary.
        urgency_level: Estimated urgency level.
    """

    user_role: Annotated[str | None, Field(default="Yleinen yleisö", description="Extracted targeted user role for the output. If unknown, default to a generic role.")]
    user_role_justification: Annotated[str | None, Field(default="Inferred from general context.", description="LLM justification for role mapping.")]
    executive_summary: Annotated[str | None, Field(default="Executive summary.", description="High-level synthesized summary")]
    urgency_level: Annotated[int | None, Field(default=1)]

    content_blocks: Annotated[
        list[AnySduiBlock],
        Field(default_factory=list, description="The fully synthesized structured SDUI content blocks."),
    ]
    cited_sources: Annotated[
        list[str], Field(default_factory=list, description="List of references or citations found.")
    ]
    section_syntheses: Annotated[
        list[SynthesisSectionDTO],
        Field(
            default_factory=list,
            description="List of synthesized sections. You MUST generate one item here for EVERY <section_instruction> provided in the system prompt!",
        ),
    ]
    xai_highlights: Annotated[
        list[XaiHighlightItem],
        Field(
            default_factory=list,
            description="The deduplicated insight items per extension category, up to the requested maximum count.",
        ),
    ]

    @model_validator(mode="before")
    @classmethod
    def _sanitize_sdui_blocks(cls, data: Any) -> Any:
        if isinstance(data, dict):
            blocks = data.get("content_blocks")
            if isinstance(blocks, list):
                for b in blocks:
                    if isinstance(b, dict):
                        if "type" in b and "block_type" not in b:
                            b["block_type"] = b.pop("type")
        return data
