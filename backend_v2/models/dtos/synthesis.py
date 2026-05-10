"""Synthesis LLM payload models.

Strict Pydantic V2 definitions for the SSOT.
"""

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase


class SynthesisSectionDTO(V2CoreBase):
    layout_id: str = Field(..., description="The EXACT layout ID provided in the section instructions")
    synthesized_markdown: str = Field(..., description="The synthesized markdown content for this section")


class XaiHighlightItem(V2CoreBase):
    extension_type: str = Field(
        ..., description="Category of the insight (e.g. 'falsification', 'coaching', 'remediation', 'risk_flag')"
    )
    content: str = Field(..., description="The synthesized, deduplicated insight or tip. Max 2 sentences.")


class SynthesisRowExplanationDTO(V2CoreBase):
    matrix_id: str = Field(..., description="The ID of the matrix")
    row_explanation: str = Field(..., description="The ultra-short synthesized explanation")


class MatrixExplanationsResult(V2CoreBase):
    explanations: list[SynthesisRowExplanationDTO] = Field(
        ...,
        description=(
            "A mandatory list containing EXACTLY ONE explanation for EACH matrix_id provided in the source_data."
        ),
    )


class SynthesisOutputDTO(V2CoreBase):
    """Structured output expected from the Synthesis LLM."""

    synthesized_markdown: str = Field(..., description="The fully synthesized and deduplicated markdown content.")
    cited_sources: list[str] = Field(default_factory=list, description="List of references or citations found.")
    section_syntheses: list[SynthesisSectionDTO] = Field(
        default_factory=list, description="List of synthesized sections, mapped by their Layout ID."
    )
    xai_highlights: list[XaiHighlightItem] = Field(
        default_factory=list, description="Top 3 deduplicated items per extension category across all steps."
    )
