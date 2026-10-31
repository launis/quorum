"""Synthesis LLM payload models.

Strict Pydantic V2 definitions for the SSOT. Contains structured inputs and
outputs of the reporting synthesis pipeline.
"""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, TypeAdapter

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO, CausalTdaFusionResultDTO
from backend_v2.models.enums import ExecutionStatus, LaxRoleClassification
from backend_v2.models.view.sdui import (
    AlertBlock,
    BulletListBlock,
    ParagraphBlock,
    SduiQuoteCard,
    SduiWarningCard,
)

__all__ = [
    "CausalSynthesisBriefDTO",
    "ExecutiveSummarySectionResult",
    "LlmSduiBlock",
    "MatrixExplanationContextDTO",
    "MatrixExplanationContextList",
    "MatrixExplanationsResult",
    "MatrixFailureDeficitDTO",
    "MatrixSectionSynthesesResult",
    "SynthesisDistillationDTO",
    "SynthesisOutputDTO",
    "SynthesisRowExplanationDTO",
    "SynthesisSectionDTO",
    "XaiHighlightItem",
    "XaiHighlightsResult",
]

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

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

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

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    extension_type: Annotated[
        str,
        Field(description="Category of the insight matching explicit system XaiExtensionType options."),
    ]
    content: Annotated[
        str,
        Field(description="The synthesized, deduplicated insight or tip. Max 2 sentences."),
    ]


class MatrixFailureDeficitDTO(V2CoreBase):
    """Structured failure or short-circuited deficit entry for a matrix criterion.

    Attributes:
        claim: Localized claim label for the unmet or short-circuited criterion.
        status: Evaluation status of the deficit (FAILED or N_A).
        scale_score: Numerical scale score tier of the unmet criterion.
        evaluation_reasoning: Cognitive evaluation reasoning explaining the failure.
        is_inverse_evidence: True if assertion evaluates absence of negative evidence.
        short_circuited_by_claims: Transitively resolved upstream blocker claims and reasoning for N_A deficits.
        anti_patterns: Known anti-pattern descriptions associated with this assertion.
        contrastive_rejected: Contrastive rejected exemplar demonstrating boundary failure.
        contrastive_acceptable: Contrastive acceptable exemplar satisfying the assertion.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    claim: Annotated[str, Field(description="Localized claim label for the unmet or short-circuited criterion.")]
    status: Annotated[Literal["FAILED", "N_A"], Field(description="Evaluation status of the deficit (FAILED or N_A).")]
    scale_score: Annotated[int, Field(description="Numerical scale score tier of the unmet criterion.")]
    evaluation_reasoning: Annotated[
        str | None,
        Field(default=None, description="Cognitive evaluation reasoning explaining the failure."),
    ] = None
    is_inverse_evidence: Annotated[
        bool,
        Field(default=False, description="True if assertion evaluates absence of negative evidence."),
    ] = False
    short_circuited_by_claims: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Transitively resolved upstream blocker claims and reasoning for N_A deficits.",
        ),
    ]
    anti_patterns: Annotated[
        list[str],
        Field(default_factory=list, description="Known anti-pattern descriptions associated with this assertion."),
    ]
    contrastive_rejected: Annotated[
        str | None,
        Field(default=None, description="Contrastive rejected exemplar demonstrating boundary failure."),
    ] = None
    contrastive_acceptable: Annotated[
        str | None,
        Field(default=None, description="Contrastive acceptable exemplar satisfying the assertion."),
    ] = None


class CausalSynthesisBriefDTO(V2CoreBase):
    """Structured causal and Toulmin falsification synthesis brief for prompt tail injection.

    Attributes:
        intact_propositions: Count of intact (PASSED) propositions in the causal graph.
        total_propositions: Total number of propositions in the causal graph.
        logical_cohesion_score: Overall structural cohesion score in [0.0, 1.0].
        cycle_detected: Flag indicating whether circular reasoning was detected.
        root_cause_fault_chains: Resolved human-readable fault chains (root_cause_claim -> failing_node_claim).
        toulmin_rebuttals: Resolved 3-way Toulmin falsifications (rebuttal_claim -> invalidated_warrant -> falsified_claim).
        prescriptive_remediations: Resolved prescriptive remediation actions targeting failing claims.
        post_hoc_fidelity_penalties: Post-hoc fidelity and fair-scoring penalty deductions across causal chains.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    intact_propositions: Annotated[
        int,
        Field(ge=0, default=0, description="Count of intact (PASSED) propositions in the causal graph."),
    ] = 0
    total_propositions: Annotated[
        int,
        Field(ge=0, default=0, description="Total number of propositions in the causal graph."),
    ] = 0
    logical_cohesion_score: Annotated[
        float | None,
        Field(default=None, description="Overall structural cohesion score in [0.0, 1.0]."),
    ] = None
    cycle_detected: Annotated[
        bool,
        Field(default=False, description="Flag indicating whether circular reasoning was detected."),
    ] = False
    root_cause_fault_chains: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Resolved human-readable fault chains (root_cause_claim -> failing_node_claim).",
        ),
    ]
    toulmin_rebuttals: Annotated[
        list[str],
        Field(
            default_factory=list,
            description=(
                "Resolved 3-way Toulmin falsifications (rebuttal_claim -> invalidated_warrant -> falsified_claim)."
            ),
        ),
    ]
    prescriptive_remediations: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Resolved prescriptive remediation actions targeting failing claims.",
        ),
    ]
    post_hoc_fidelity_penalties: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Post-hoc fidelity and fair-scoring penalty deductions across causal chains.",
        ),
    ]

    @staticmethod
    def _resolve_node_label(
        raw_claim: str,
        node_id: str,
        fallback_label: str,
        node_claim_by_id: dict[str, str],
    ) -> str:
        """Resolve a human-readable proposition label from a claim or node ID map.

        Args:
            raw_claim: Direct claim string from the diagnosis item.
            node_id: Node identifier to look up in the graph map.
            fallback_label: Deterministic label returned when neither claim nor map entry exists.
            node_claim_by_id: Mapping of graph node IDs to stripped claim strings.

        Returns:
            Resolved non-empty label string.
        """
        stripped = raw_claim.strip()
        if stripped:
            return stripped
        if node_id in node_claim_by_id:
            return node_claim_by_id[node_id]
        return fallback_label

    @classmethod
    def _from_fusion_result(cls, causal_payload: CausalTdaFusionResultDTO) -> Self:
        """Construct a CausalSynthesisBriefDTO from a full CausalTdaFusionResultDTO.

        Args:
            causal_payload: Evaluated CausalTdaFusionResultDTO instance.

        Returns:
            Populated CausalSynthesisBriefDTO instance.
        """
        node_claim_by_id: dict[str, str] = {
            n.node_id: n.claim.strip() for n in causal_payload.graph.nodes if n.claim.strip()
        }
        intact = sum(1 for n in causal_payload.graph.nodes if n.status == ExecutionStatus.PASSED)
        total = len(causal_payload.graph.nodes)

        fault_chains: list[str] = []
        penalties: list[str] = []
        for diag in causal_payload.root_cause_diagnoses:
            root_label = cls._resolve_node_label(
                diag.root_cause_claim,
                diag.root_cause_parent_id,
                diag.root_cause_parent_id,
                node_claim_by_id,
            )
            failing_label = cls._resolve_node_label(
                diag.failing_node_claim,
                diag.failing_node_id,
                diag.failing_node_id,
                node_claim_by_id,
            )
            fault_chains.append(f"{root_label} -> {failing_label} ({diag.warrant_relation}): {diag.explanation}")
            if diag.penalty_points > 0.0:
                penalties.append(f"{failing_label}: -{diag.penalty_points:.2f} ({diag.root_cause_type})")

        rebuttals: list[str] = [
            f"{cls._resolve_node_label('', item.rebuttal_id, 'Rebuttal', node_claim_by_id)} -> "
            f"{cls._resolve_node_label('', item.invalidated_warrant_id, 'Invalidated Warrant', node_claim_by_id)} -> "
            f"{item.claim_statement} (confidence: {item.rebuttal_confidence:.2f})"
            for item in causal_payload.falsified_claims
        ]
        remediations: list[str] = [
            f"{cls._resolve_node_label('', rem.target_node_id, rem.target_node_id, node_claim_by_id)}: "
            f"{rem.required_action} (impact: +{rem.potential_score_impact:.2f})"
            for rem in causal_payload.prescriptive_remediations
        ]

        fs = causal_payload.fair_scoring
        if fs.raw_penalty_points > 0.0 or fs.deduplicated_penalty_points > 0.0:
            penalties.append(
                f"Fair Scoring Summary: raw=-{fs.raw_penalty_points:.2f}, "
                f"deduplicated=-{fs.deduplicated_penalty_points:.2f}, "
                f"dampened_savings=+{fs.dampened_savings_points:.2f} "
                f"(independent_errors={fs.independent_error_count}, "
                f"cascading_faults={fs.cascading_fault_count})"
            )

        return cls(
            intact_propositions=intact,
            total_propositions=total,
            logical_cohesion_score=causal_payload.anti_fluff_audit.logical_cohesion_score,
            cycle_detected=causal_payload.graph.cycle_detected,
            root_cause_fault_chains=fault_chains,
            toulmin_rebuttals=rebuttals,
            prescriptive_remediations=remediations,
            post_hoc_fidelity_penalties=penalties,
        )

    @classmethod
    def _from_graph_payload(cls, causal_payload: CausalGraphPayloadDTO) -> Self:
        """Construct a CausalSynthesisBriefDTO from a standalone CausalGraphPayloadDTO.

        Args:
            causal_payload: Evaluated CausalGraphPayloadDTO instance.

        Returns:
            Populated CausalSynthesisBriefDTO instance.
        """
        node_claim_by_id = {n.node_id: n.claim.strip() for n in causal_payload.nodes if n.claim.strip()}
        intact = sum(1 for n in causal_payload.nodes if n.status == ExecutionStatus.PASSED)
        root_chains: list[str] = [
            f"Root Cause Proposition: {cls._resolve_node_label('', root_id, root_id, node_claim_by_id)}"
            for root_id in causal_payload.root_cause_node_ids
        ]
        return cls(
            intact_propositions=intact,
            total_propositions=len(causal_payload.nodes),
            logical_cohesion_score=None,
            cycle_detected=causal_payload.cycle_detected,
            root_cause_fault_chains=root_chains,
            toulmin_rebuttals=[],
            prescriptive_remediations=[],
            post_hoc_fidelity_penalties=[],
        )

    @classmethod
    def from_causal_payload(
        cls,
        causal_payload: CausalTdaFusionResultDTO | CausalGraphPayloadDTO,
    ) -> Self:
        """Construct a CausalSynthesisBriefDTO from a causal fusion result or causal graph payload.

        Args:
            causal_payload: Evaluated CausalTdaFusionResultDTO or CausalGraphPayloadDTO instance.

        Returns:
            Populated CausalSynthesisBriefDTO with human-readable claims, Toulmin rebuttals, and penalties.
        """
        match causal_payload:
            case CausalTdaFusionResultDTO():
                return cls._from_fusion_result(causal_payload)
            case CausalGraphPayloadDTO():
                return cls._from_graph_payload(causal_payload)

    def format_for_prompt(self) -> str:
        """Serialize the causal synthesis brief into a deterministic markdown block for prompt tail injection.

        Returns:
            Formatted markdown string summarizing causal fault chains, Toulmin rebuttals, and penalties.
        """
        lines: list[str] = []
        if self.logical_cohesion_score is not None:
            lines.append(f"Intact Propositions: {self.intact_propositions}/{self.total_propositions}")
            lines.append(f"Logical Cohesion: {self.logical_cohesion_score:.2f}")
        else:
            lines.append(f"Total Propositions: {self.total_propositions}")
            lines.append(f"Cycle Detected: {self.cycle_detected}")

        if self.root_cause_fault_chains:
            lines.append("Root Cause Fault Chains:")
            for chain in self.root_cause_fault_chains:
                lines.append(f"- {chain}")

        if self.toulmin_rebuttals:
            lines.append("Toulmin Falsified Claims (Rebuttal -> Invalidated Warrant -> Falsified Claim):")
            for rebuttal in self.toulmin_rebuttals:
                lines.append(f"- {rebuttal}")

        if self.prescriptive_remediations:
            lines.append("Prescriptive Remediations:")
            for rem in self.prescriptive_remediations:
                lines.append(f"- {rem}")

        if self.post_hoc_fidelity_penalties:
            lines.append("Post-Hoc Fidelity Penalties:")
            for penalty in self.post_hoc_fidelity_penalties:
                lines.append(f"- {penalty}")

        return "\n".join(lines)


class MatrixExplanationContextDTO(V2CoreBase):
    """DTO representing the evaluated state of a matrix for synthesis explanation.

    Attributes:
        real_matrix_id: The original PromptBlock ID.
        matrix_id: The alias for the LLM.
        matrix_label: The localized matrix title.
        score: The normalized score.
        justification: The structured justification text including quotes.
        unmet_deficits: Structured failure and short-circuit deficits for this matrix.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    real_matrix_id: Annotated[str, Field(description="The original PromptBlock ID")]
    matrix_id: Annotated[str, Field(description="The alias for the LLM")]
    matrix_label: Annotated[str, Field(description="The localized matrix title")]
    score: Annotated[float | None, Field(description="The normalized score", default=None)]
    justification: Annotated[str, Field(description="The structured justification text including quotes")]
    unmet_deficits: Annotated[
        list[MatrixFailureDeficitDTO],
        Field(default_factory=list, description="Structured failure and short-circuit deficits for this matrix."),
    ]


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
    ]
    matrices_to_explain: Annotated[
        list[MatrixExplanationContextDTO],
        Field(default_factory=list, description="Evaluated matrix contexts requiring qualitative explanation"),
    ]
    source_alias_map: Annotated[
        dict[str, str], Field(default_factory=dict, description="Mapping of raw IDs to semantic aliases")
    ]
    output_profile_id: Annotated[
        str | None, Field(default=None, description="Optional presentation output profile identifier")
    ] = None
    target_locale: Annotated[str, Field(default="en", description="Target localization language code")] = "en"
    alias_registry: Annotated[dict[str, str], Field(default_factory=dict, description="Full alias registry mapping")]
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

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

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

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

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

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

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
    ]
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

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    sections: Annotated[
        list[SynthesisSectionDTO],
        Field(
            default_factory=list,
            description="List of synthesized sections. You MUST generate one item here for EVERY <section_instruction> provided in the system prompt!",
        ),
    ]


class XaiHighlightsResult(V2CoreBase):
    """Structured output expected from the dedicated XAI Highlights curation LLM task.

    Attributes:
        xai_highlights: The deduplicated insight items per extension category.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    xai_highlights: Annotated[
        list[XaiHighlightItem],
        Field(
            default_factory=list,
            description="List of synthesized XAI highlights deduced from the evaluation phase.",
        ),
    ]


class SynthesisOutputDTO(V2CoreBase):
    """Structured output expected from the Synthesis LLM.

    Attributes:
        user_role: Optional targeted user role for the output.
        user_role_justification: Optional LLM justification for role mapping.
        cited_sources: List of references or citations found.
        section_syntheses: List of synthesized sections, mapped by their layout ID.
        xai_highlights: The deduplicated insight items per extension category.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

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
            description="List of synthesized XAI highlights deduced from the evaluation phase.",
        ),
    ]
