"""Synthesis LLM payload models.

Strict Pydantic V2 definitions for the SSOT. Contains structured inputs and
outputs of the reporting synthesis pipeline.
"""

from typing import Annotated

from pydantic import ConfigDict, Field, TypeAdapter

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import LaxRoleClassification
from backend_v2.models.view.sdui import (
    AlertBlock,
    BulletListBlock,
    ParagraphBlock,
    SduiQuoteCard,
    SduiWarningCard,
)

LlmSduiBlock = Annotated[
    ParagraphBlock | BulletListBlock | AlertBlock | SduiQuoteCard | SduiWarningCard,
    Field(discriminator="block_type"),
]


class SynthesisSectionDTO(V2CoreBase):
    """DTO representing a single synthesized section within a larger layout structure.

    Attributes:
        layout_id: The EXACT layout ID provided in the section instructions.
        content_blocks: Structured SDUI content blocks for this section.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    layout_id: Annotated[str, Field(description="The EXACT layout ID provided in the section instructions")]
    content_blocks: Annotated[
        list[LlmSduiBlock],
        Field(..., min_length=1, description="Structured SDUI content blocks for this section"),
    ]


class XaiHighlightItem(V2CoreBase):
    """DTO representing a highly contextual, structured XAI highlight or tip.

    Attributes:
        extension_type: Category of the insight matching explicit system XaiExtensionType options.
        content: The synthesized, deduplicated insight or tip. Max 2 sentences.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    extension_type: Annotated[
        str,
        Field(description="Category of the insight matching explicit system XaiExtensionType options."),
    ]
    content: Annotated[
        str,
        Field(description="The synthesized, deduplicated insight or tip. Max 2 sentences."),
    ]


class MatrixExplanationContextDTO(V2CoreBase):
    """DTO representing the evaluated state of a matrix for synthesis explanation.

    Attributes:
        real_matrix_id: The original PromptBlock ID.
        matrix_id: The alias for the LLM.
        matrix_label: The localized matrix title.
        score: The normalized score.
        justification: The structured justification text including quotes.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    real_matrix_id: Annotated[str, Field(description="The original PromptBlock ID")]
    matrix_id: Annotated[str, Field(description="The alias for the LLM")]
    matrix_label: Annotated[str, Field(description="The localized matrix title")]
    score: Annotated[float | None, Field(description="The normalized score", default=None)]
    justification: Annotated[str, Field(description="The structured justification text including quotes")]


MatrixExplanationContextList = TypeAdapter(list[MatrixExplanationContextDTO])


class SynthesisDistillationDTO(V2CoreBase):
    """Strongly typed distillation payload emitted by synthesis_distiller_hook.

    Attributes:
        distilled_inputs: Complete concatenated and formatted source inputs.
        historical_context: Optional historical context from prior executions.
        title_map: Mapping of block/step IDs to localized display titles.
        matrices_to_explain: Evaluated matrix contexts requiring qualitative explanation.
        source_alias_map: Mapping of raw IDs to semantic aliases.
        output_profile_id: Optional presentation output profile identifier.
        target_locale: Target localization language code.
        alias_registry: Full alias registry mapping.
        max_extensions: Maximum qualitative behavioral extensions allowed.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    distilled_inputs: Annotated[str, Field(description="Complete concatenated and formatted source inputs")]
    historical_context: Annotated[
        str | None, Field(default=None, description="Optional historical context from prior executions")
    ] = None
    title_map: Annotated[
        dict[str, str], Field(default_factory=dict, description="Mapping of block/step IDs to localized display titles")
    ] = Field(default_factory=dict)
    matrices_to_explain: Annotated[
        list[MatrixExplanationContextDTO],
        Field(default_factory=list, description="Evaluated matrix contexts requiring qualitative explanation"),
    ] = Field(default_factory=list)
    source_alias_map: Annotated[
        dict[str, str], Field(default_factory=dict, description="Mapping of raw IDs to semantic aliases")
    ] = Field(default_factory=dict)
    output_profile_id: Annotated[
        str | None, Field(default=None, description="Optional presentation output profile identifier")
    ] = None
    target_locale: Annotated[str, Field(default="en", description="Target localization language code")] = "en"
    alias_registry: Annotated[
        dict[str, str], Field(default_factory=dict, description="Full alias registry mapping")
    ] = Field(default_factory=dict)
    max_extensions: Annotated[
        int, Field(default=5, description="Maximum qualitative behavioral extensions allowed")
    ] = 5


class SynthesisRowExplanationDTO(V2CoreBase):
    """DTO providing a short context explanation for a specific matrix mapping row.

    Attributes:
        matrix_id: The ID of the matrix.
        row_explanation: The ultra-short synthesized explanation.
        curated_quotes: Curated verbatim quotes by the LLM.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    matrix_id: Annotated[str, Field(description="The ID of the matrix")]
    row_explanation: Annotated[
        str,
        Field(description="The ultra-short synthesized explanation."),
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

    model_config = ConfigDict(strict=True, extra="forbid")

    explanations: Annotated[
        list[SynthesisRowExplanationDTO],
        Field(
            description=(
                "A mandatory list containing EXACTLY ONE explanation for EACH matrix_id provided in the source_data."
            ),
        ),
    ]


class ExecutiveSummarySectionResult(V2CoreBase):
    """Structured output expected from the dedicated Executive Summary LLM task.

    Attributes:
        user_role: Extracted targeted user role for the output.
        user_role_justification: LLM justification for role mapping.
        cited_sources: List of references or citations found.
        executive_summary: High-level synthesized summary content blocks.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    user_role: Annotated[
        LaxRoleClassification | None,
        Field(
            default=None,
            description="Deprecated user role.",
        ),
    ] = None
    user_role_justification: Annotated[
        str | None,
        Field(
            default=None,
            description="Deprecated user role justification.",
        ),
    ] = None
    cited_sources: Annotated[
        list[str],
        Field(default_factory=list, description="List of references or citations found."),
    ] = Field(default_factory=list)
    executive_summary: Annotated[
        list[LlmSduiBlock],
        Field(
            ...,
            min_length=1,
            description="Structured SDUI content blocks representing the executive summary narrative.",
        ),
    ]


class MatrixSectionSynthesesResult(V2CoreBase):
    """Structured output expected from the layout section synthesis LLM task.

    Attributes:
        sections: List of synthesized sections mapped to layout IDs.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    sections: Annotated[
        list[SynthesisSectionDTO],
        Field(
            default_factory=list,
            description="List of synthesized sections. You MUST generate one item here for EVERY <section_instruction> provided in the system prompt!",
        ),
    ] = Field(default_factory=list)


class XaiHighlightsResult(V2CoreBase):
    """Structured output expected from the dedicated XAI Highlights curation LLM task.

    Attributes:
        xai_highlights: The deduplicated insight items per extension category.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    xai_highlights: Annotated[
        list[XaiHighlightItem],
        Field(
            default_factory=list,
            description="List of synthesized XAI highlights deduced from the evaluation phase.",
        ),
    ] = Field(default_factory=list)


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

    model_config = ConfigDict(strict=True, extra="forbid")

    user_role: Annotated[
        str | None,
        Field(
            default=None,
            description="Deprecated user role.",
        ),
    ] = None
    user_role_justification: Annotated[
        str | None,
        Field(
            default=None,
            description="Deprecated user role justification.",
        ),
    ] = None

    cited_sources: Annotated[
        list[str],
        Field(default_factory=list, description="List of references or citations found."),
    ] = Field(default_factory=list)
    section_syntheses: Annotated[
        list[SynthesisSectionDTO],
        Field(
            default_factory=list,
            description="List of synthesized sections. You MUST generate one item here for EVERY <section_instruction> provided in the system prompt!",
        ),
    ] = Field(default_factory=list)
    xai_highlights: Annotated[
        list[XaiHighlightItem],
        Field(
            default_factory=list,
            description="List of synthesized XAI highlights deduced from the evaluation phase.",
        ),
    ] = Field(default_factory=list)
