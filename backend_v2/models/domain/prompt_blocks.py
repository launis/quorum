"""V2 PromptBlock Polymorphic Domain Models.

Fuses legacy components and matrices into a strict Pydantic V2 discriminated union.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import (
    ConfigDict,
    Field,
    StringConstraints,
    TypeAdapter,
    model_validator,
)

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import I18nText, MatrixRow, MatrixScale, TheoryGrounding

__all__ = [
    "AnyPromptBlock",
    "MatrixPromptBlock",
    "PersonaPromptBlock",
    "PromptBlock",
    "PromptBlockAdapter",
    "PromptBlockBase",
    "ProtocolPromptBlock",
    "SystemRulePromptBlock",
    "PROMPT_BLOCK_REGISTRY",
    "StrictStr",
]

StrictStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class PromptBlockBase(V2CoreBase):
    """Base model for polymorphic prompt blocks with shared attributes."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str,
        Field(
            pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
            description="Unique identifier for the prompt block. MUST be a valid Stripe Pattern Opaque ID.",
        ),
    ]
    slug: StrictStr = Field(description="URL routing helper field. Strictly no data relation role.")
    organization_id: str | None = Field(default=None, description="Tenant organization ID.")
    label: I18nText = Field(description="Localizable label for the UI.")
    description: I18nText = Field(description="Localizable description or help text for the UI.")
    output_extensions: list[str] = Field(
        default_factory=list,
        description="List of requested XAI output extensions (e.g. 'justification', 'risk_flag').",
    )
    ai_description: str | None = Field(
        default=None,
        description=(
            "MANDATORY: English cognitive instructions for the LLM. "
            "Completely isolates AI prompt from UI localizations."
        ),
    )
    theory_grounding: TheoryGrounding | None = Field(
        default=None,
        description="Fetches and injects source theory as <theory_context>.",
    )


class MatrixPromptBlock(PromptBlockBase):
    """Matrix prompt block evaluating behavioral claims across BARS scales."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    category_id: Literal[PromptBlockCategory.MATRIX] = PromptBlockCategory.MATRIX
    type: Literal[BlockDataType.FLOAT, BlockDataType.INT] = BlockDataType.FLOAT
    is_evaluative: bool = True
    allow_decimals: bool = False
    allow_contextual_override: bool = False
    is_lightweight_protocol: bool = False
    scales: list[MatrixScale] = Field(..., min_length=1, description="BARS scale definitions with scores and claims.")
    rows: list[MatrixRow] | None = None
    columns: list[I18nText] | None = None
    computed_min: int | None = Field(default=None, description="Derived or calculated minimum score.")
    computed_max: int | None = Field(default=None, description="Derived or calculated maximum score.")

    @model_validator(mode="before")
    @classmethod
    def _compute_extrema(cls, data: Any) -> Any:
        """Dynamically computes absolute minimum and maximum scores from scales if not provided."""
        try:
            d = dict(data)
        except TypeError, ValueError:
            return data

        scales = d.get("scales")
        if isinstance(scales, list) and scales:
            scores: list[int] = []
            for s in scales:
                match s:
                    case MatrixScale(score=score):
                        scores.append(score)
                    case _:
                        try:
                            score_raw = s.get("score")
                            if score_raw is not None:
                                scores.append(int(score_raw))
                        except AttributeError, TypeError, ValueError:
                            try:
                                scores.append(int(s.score))
                            except AttributeError, TypeError, ValueError:
                                pass
            if scores:
                if d.get("computed_min") is None:
                    d["computed_min"] = min(scores)
                if d.get("computed_max") is None:
                    d["computed_max"] = max(scores)
        return d


class SystemRulePromptBlock(PromptBlockBase):
    """System rule, runtime variables, or task definition prompt block."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    category_id: Literal[
        PromptBlockCategory.SYSTEM_RULE,
        PromptBlockCategory.RUNTIME_VARIABLES,
        PromptBlockCategory.TASK_DEFINITION,
    ] = PromptBlockCategory.SYSTEM_RULE
    type: Literal[
        BlockDataType.INSTRUCTION,
        BlockDataType.STRING,
        BlockDataType.PANEL,
        BlockDataType.COMPLIANCE,
        BlockDataType.QUESTION,
        BlockDataType.CRITERIA,
    ] = BlockDataType.INSTRUCTION
    is_evaluative: bool = False
    allow_decimals: bool = False
    is_lightweight_protocol: bool = False
    instruction_text: StrictStr | None = None


class PersonaPromptBlock(PromptBlockBase):
    """Execution persona or agent role prompt block."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    category_id: Literal[
        PromptBlockCategory.EXECUTION_PERSONA,
        PromptBlockCategory.AGENT_ROLE,
    ] = PromptBlockCategory.EXECUTION_PERSONA
    type: Literal[BlockDataType.INSTRUCTION, BlockDataType.STRING] = BlockDataType.INSTRUCTION
    is_evaluative: bool = False
    allow_decimals: bool = False
    is_lightweight_protocol: bool = False
    role_enforcement: StrictStr | None = None
    tone_directives: list[StrictStr] = Field(default_factory=list)


class ProtocolPromptBlock(PromptBlockBase):
    """Protocol prompt block defining execution extraction mechanics."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    category_id: Literal[PromptBlockCategory.PROTOCOL] = PromptBlockCategory.PROTOCOL
    type: Literal[BlockDataType.INSTRUCTION, BlockDataType.STRING] = BlockDataType.INSTRUCTION
    is_evaluative: bool = False
    allow_decimals: bool = False
    is_lightweight_protocol: bool = False
    protocol_instructions: StrictStr | None = None


AnyPromptBlock = Annotated[
    MatrixPromptBlock | SystemRulePromptBlock | PersonaPromptBlock | ProtocolPromptBlock,
    Field(discriminator="category_id"),
]

PromptBlock = AnyPromptBlock
PromptBlockAdapter: TypeAdapter[AnyPromptBlock] = TypeAdapter(AnyPromptBlock)

PROMPT_BLOCK_REGISTRY: dict[PromptBlockCategory, type[PromptBlockBase]] = {
    PromptBlockCategory.MATRIX: MatrixPromptBlock,
    PromptBlockCategory.SYSTEM_RULE: SystemRulePromptBlock,
    PromptBlockCategory.RUNTIME_VARIABLES: SystemRulePromptBlock,
    PromptBlockCategory.TASK_DEFINITION: SystemRulePromptBlock,
    PromptBlockCategory.EXECUTION_PERSONA: PersonaPromptBlock,
    PromptBlockCategory.AGENT_ROLE: PersonaPromptBlock,
    PromptBlockCategory.PROTOCOL: ProtocolPromptBlock,
}
