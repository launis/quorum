"""Domain models for behavioral matrices and TDA assertions.

SSOT for TheoryGrounding, AcceptanceCriterion, AntiPattern, ContrastivePairDTO,
TDAAssertion, MatrixClaim, MatrixRow, and MatrixScale.
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Annotated, Any, Literal, Self

if TYPE_CHECKING:
    from backend_v2.models.dtos.dag_models import CausalEdge

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StringConstraints, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import I18nText, V2CoreBase
from backend_v2.models.enums import TargetSpeaker

logger = logging.getLogger(__name__)

__all__ = [
    "AcceptanceCriterion",
    "AntiPattern",
    "ContrastivePairDTO",
    "FlattenedAtom",
    "MatrixClaim",
    "MatrixRow",
    "MatrixScale",
    "TDAAssertion",
    "TheoryGrounding",
]


class TheoryGrounding(V2CoreBase):
    """Used in PromptBlock to bind criteria to organizational truth.

    Attributes:
        source_url: URL or reference to the source material.
        citation_reference: Specific section or phrase to cite from the source.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    source_url: str = Field(description="URL or reference to the source material.")
    citation_reference: str | None = Field(
        default=None, description="Specific section or phrase to cite from the source."
    )


class AcceptanceCriterion(V2CoreBase):
    """Structured acceptance criterion with bilingual instruction."""

    model_config = ConfigDict(strict=True, extra="forbid")

    instruction: str = Field(description="Structured monolingual instruction.")
    requires_contextual_override: bool = Field(default=False)


class AntiPattern(V2CoreBase):
    """Known anti-pattern with bilingual description."""

    model_config = ConfigDict(strict=True, extra="forbid")

    pattern: str = Field(description="Known anti-pattern with monolingual description.")
    allows_contextual_excuse: bool = Field(default=False)


def _coerce_to_tuple(v: Any) -> Any:
    """Coerces list to tuple for immutable DAG depends_on fields."""
    if isinstance(v, list):
        return tuple(v)
    return v


class ContrastivePairDTO(V2CoreBase):
    """Structured contrastive calibration pair for TDA assertion boundary grounding.

    Attributes:
        acceptable: Textual exemplar satisfying the evaluation assertion.
        rejected: Textual counterpart demonstrating disqualification or boundary failure.
    """

    acceptable: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=10),
        Field(description="Textual exemplar satisfying the evaluation assertion."),
    ]
    rejected: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=10),
        Field(description="Textual counterpart demonstrating disqualification or boundary failure."),
    ]

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    @model_validator(mode="after")
    def validate_contrastive_diversity(self) -> Self:
        """Enforces that acceptable and rejected exemplars are distinct and non-empty.

        Raises:
            ValueError: If acceptable equals rejected or either exemplar is blank.
        """
        if self.acceptable.strip().lower() == self.rejected.strip().lower():
            msg = "Contrastive acceptable and rejected exemplars cannot be identical."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self


class TDAAssertion(V2CoreBase):
    """Deterministic rule evaluated by the backend.

    Attributes:
        tda_id: Opaque Stripe ID for this assertion.
        inverse_evidence: If True, acts as a poison/penalty detector.
        aggregation_mode: Aggregation constraint.
        evaluation_track: Decoupled evaluation track.
        facts_to_find: The list of facts to extract for this assertion.
        logical_expression: Whitelisted Boolean logical expression using extracted facts.
        allow_contextual_override: If True, allows overriding this assertion with a contextual excuse.
        high_entropy: If True, enables multi-agent ensemble majority voting for this assertion.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    tda_id: str = Field(
        default_factory=lambda: f"tda_{uuid.uuid4().hex}",
        pattern=r"^tda_[a-f0-9]{32}$",
        description="Opaque Stripe ID for this assertion.",
    )
    inverse_evidence: bool = Field(description="If True, acts as a poison/penalty detector.")
    aggregation_mode: Literal["EXISTS", "ALL_MUST_COMPLY"] = Field(description="Aggregation constraint.")

    # Decoupled evaluation track properties for extractive sensor and cognitive judgement pipelines
    evaluation_track: Literal["EXTRACTIVE_SENSOR", "COGNITIVE_JUDGEMENT"] = Field(
        default="COGNITIVE_JUDGEMENT",
        description="Decoupled evaluation track: extractive logic vs cognitive judgement.",
    )
    facts_to_find: list[str] = Field(
        default_factory=list,
        description="The list of facts to extract for this assertion.",
    )
    logical_expression: str | None = Field(
        default=None,
        description="Whitelisted Boolean logical expression using extracted facts.",
    )
    high_entropy: bool = Field(
        default=False,
        description="If True, enables multi-agent ensemble majority voting for this assertion.",
    )
    target_speaker: Annotated[
        TargetSpeaker,
        Field(
            default=TargetSpeaker.USER,
            strict=False,
            description="Evaluated target actor (USER, AI). Defaults to USER.",
        ),
    ] = TargetSpeaker.USER

    # Monolingual concept description consumed by the LLM extraction pipeline
    concept_description: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=10),
    ] = Field(description="Concise concept definition for this assertion, not runtime instructions")
    anchor_target: str | None = Field(default=None, description="Target anchor to search for during extraction")
    bounding_box_scope: Literal["sentence", "paragraph", "document", "adjacent_paragraphs"] = Field(default="paragraph")
    extraction_rule: str | None = Field(default=None, description="The extraction rule that data must satisfy")
    acceptance_criteria: list[AcceptanceCriterion] = Field(
        default_factory=list,
        description="Structured acceptance criteria with monolingual instructions.",
    )
    anti_patterns: list[AntiPattern] = Field(
        default_factory=list,
        description="Known anti-patterns with monolingual descriptions.",
    )
    contrastive_example: ContrastivePairDTO | None = Field(
        default=None,
        description="Structured contrastive pair showing acceptable vs rejected exemplars.",
    )
    syntactic_anchors: list[str] = Field(
        default_factory=list,
        description="Exact syntactic markers for extractive matching.",
    )
    enforce_pre_flight: bool = Field(
        default=False,
        description="If True, enables pre-flight validation before LLM evaluation.",
    )
    depends_on: Annotated[
        tuple[CausalEdge, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(
            default_factory=tuple,
            description="Causal preconditions required for this assertion.",
        ),
    ]

    @model_validator(mode="after")
    def validate_math_logic(self) -> TDAAssertion:
        """Validates the consistency of the assertion constraints.

        Raises:
            AppException: If constraints are mathematically or logically invalid.

        Returns:
            The validated assertion.
        """
        if self.inverse_evidence and self.aggregation_mode == "ALL_MUST_COMPLY":
            msg = "Inverse evidence (poison detection) strictly requires 'EXISTS' aggregation mode."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)

        if self.enforce_pre_flight and len(self.syntactic_anchors) == 0:
            msg = "enforce_pre_flight=True requires at least one syntactic anchor."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)

        for crit in self.acceptance_criteria:
            if len(crit.instruction.strip()) < 5:
                msg = "All acceptance_criteria instructions must be at least 5 characters long."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)

        for anti in self.anti_patterns:
            if len(anti.pattern.strip()) < 5:
                msg = "All anti_patterns descriptions must be at least 5 characters long."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)

        # Enforce strict dual-track TDA validations
        if self.evaluation_track == "EXTRACTIVE_SENSOR":
            if not self.facts_to_find:
                msg = "EXTRACTIVE_SENSOR track requires at least one fact in facts_to_find."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.logical_expression or not self.logical_expression.strip():
                msg = "EXTRACTIVE_SENSOR track requires a defined logical_expression."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        return self


class MatrixClaim(V2CoreBase):
    """Represents a single behavioral claim with empirical TDA assertions.

    Attributes:
        label: User-facing empirical claim.
        tda_assertions: Test-Driven Assertion rules explicitly set by experts.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    label: I18nText = Field(description="User-facing empirical claim.")
    tda_assertions: list[TDAAssertion] = Field(
        ...,
        min_length=1,
        description="Test-Driven Assertion rules explicitly set by experts.",
    )


class MatrixRow(V2CoreBase):
    """Represents a row in a 2D matrix evaluating multiple dimensions.

    Attributes:
        label: User-facing row name.
        ai_description: Dedicated AI evaluation instruction for this sub-dimension.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    label: I18nText = Field(description="User-facing row name.")
    ai_description: str = Field(description="Dedicated AI evaluation instruction for this sub-dimension.")


class MatrixScale(V2CoreBase):
    """Represents a single score point in a BARS matrix scale.

    Attributes:
        score: Numerical value of the scale point.
        name: Optional name for the scale point (e.g., 'Excellent').
        ai_label: Short uppercase AI mnemonic replacing English target label, e.g. CATASTROPHIC FAILURE.
        claims: List of behavioral claims/criteria for this score.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    score: int = Field(description="Numerical value of the scale point.")
    name: I18nText | None = Field(default=None, description="Optional name for the scale point (e.g., 'Excellent').")
    ai_label: str = Field(
        description="Short uppercase AI mnemonic replacing English target label, e.g. CATASTROPHIC FAILURE"
    )
    claims: list[MatrixClaim] = Field(
        default_factory=list, description="List of behavioral claims/criteria for this score."
    )


from backend_v2.models.dtos.dag_models import CausalEdge

TDAAssertion.model_rebuild(_types_namespace={"CausalEdge": CausalEdge})


class FlattenedAtom(BaseModel):
    """Strict Pydantic schema for individual shuffled items (No Naked Dicts rule).

    Attributes:
        atom_id: The unique identifier of the atom.
        question: The evaluation question or statement for the atom.
        depends_on: Immutable tuple of causal edge dependencies in the DAG.
        contrastive_example: Contrastive calibration pair for assertion boundary grounding.
        acceptance_criteria: Structured acceptance criteria with bilingual instructions.
        anti_patterns: Known anti-patterns with bilingual descriptions.
        syntactic_anchors: Required lexical tokens/phrases for surface syntax grounding.
        target_speaker: The speaker role this atom evaluates against.
    """

    atom_id: Annotated[str, Field(description="The unique identifier of the atom.")]
    question: Annotated[str, Field(description="The evaluation question or statement for the atom.")]
    extraction_rule: Annotated[str, Field(default="", description="The specific validation rule.")] = ""
    anchor_target: Annotated[str, Field(default="", description="Semantic bounding box target.")] = ""
    is_inverse: Annotated[bool, Field(default=False, description="True if this is an inverse assertion.")] = False
    depends_on: Annotated[
        tuple[CausalEdge, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(default_factory=tuple, description="Immutable tuple of causal dependencies."),
    ]
    contrastive_example: Annotated[
        ContrastivePairDTO | None,
        Field(default=None, description="Contrastive calibration pair for assertion boundary grounding."),
    ] = None
    acceptance_criteria: Annotated[
        tuple[AcceptanceCriterion, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(default_factory=tuple, description="Structured acceptance criteria."),
    ]
    anti_patterns: Annotated[
        tuple[AntiPattern, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(default_factory=tuple, description="Known anti-patterns."),
    ]
    syntactic_anchors: Annotated[
        tuple[str, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(default_factory=tuple, description="Required lexical tokens/phrases."),
    ]
    target_speaker: Annotated[
        TargetSpeaker,
        Field(default=TargetSpeaker.USER, strict=False, description="Evaluated speaker role."),
    ] = TargetSpeaker.USER

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
