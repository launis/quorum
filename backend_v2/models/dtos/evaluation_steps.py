from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.models.prompts.field_prompts import DESC_CONTEXTUAL_OVERRIDE, DESC_EXACT_QUOTES


class BaseExtractionDTO(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_llm_dunder_leaks(cls, data: Any) -> Any:
        if isinstance(data, dict):
            cleaned = {k: v for k, v in data.items() if not (k.startswith("__") and k.endswith("__"))}
            if cleaned.get("contextual_override") is True:
                cleaned["exact_quotes"] = []
            return cleaned
        return data


from backend_v2.models.enums import SystemConcurrency


class StepDTOStrict(BaseExtractionDTO):
    reasoning_steps: str = Field(description="Step by step cognitive breakdown of the text. MUST come before decision.")
    exact_quotes: list[str] = Field(default_factory=list, max_length=3, description=DESC_EXACT_QUOTES)
    structural_location: str = Field(description="Exact structural location (e.g. 'page 3'). Must be 'N/A' if missing.")
    localized_anchors_found: list[str] = Field(
        default_factory=list,
        max_length=SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS,
        description="Keywords in target language.",
    )
    falsification_argument: str = Field(
        description="Why this evidence might NOT satisfy the strict causal requirement of the rule."
    )
    counter_quote: str | None = Field(
        default=None,
        description=(
            "If you believe the exact_quotes are taken out of context, provide a SEPARATE "
            "verbatim quote from the source text that contradicts or contextualizes them. "
            "This counter-evidence MUST also be a physically contiguous substring. "
            "If you cannot find contradicting evidence, leave this as null."
        ),
    )
    decision: bool = Field(description="True if the condition is physically met, False otherwise.")
    semantic_reasoning: str = Field(description="Final summary of the decision.")


class StepDTOSemantic(BaseExtractionDTO):
    reasoning_steps: str = Field(description="Step by step cognitive breakdown of the text. MUST come before decision.")
    exact_quotes: list[str] = Field(
        default_factory=list,
        max_length=3,
        description=DESC_EXACT_QUOTES,
    )
    structural_location: str = Field(
        description="Exact structural location. If override is True, MUST provide location."
    )
    localized_anchors_found: list[str] = Field(
        default_factory=list,
        max_length=SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS,
        description="Keywords in target language.",
    )
    contextual_override: bool = Field(
        default=False,
        description=DESC_CONTEXTUAL_OVERRIDE,
    )
    override_reason: str | None = Field(default=None, description="Explanation for the contextual override.")
    falsification_argument: str = Field(
        description="Why this evidence might NOT satisfy the strict causal requirement of the rule."
    )
    counter_quote: str | None = Field(
        default=None,
        description=(
            "If you believe the exact_quotes are taken out of context, provide a SEPARATE "
            "verbatim quote from the source text that contradicts or contextualizes them. "
            "This counter-evidence MUST also be a physically contiguous substring. "
            "If you cannot find contradicting evidence, leave this as null."
        ),
    )
    decision: bool = Field(description="True if the condition is met (physically or semantically), False otherwise.")
    semantic_reasoning: str = Field(description="Final summary of the decision.")


class ParsingLogStepsStrict(BaseExtractionDTO):
    steps: list[StepDTOStrict] = Field(description="The sequence of evaluation steps.")


class ParsingLogStepsSemantic(BaseExtractionDTO):
    steps: list[StepDTOSemantic] = Field(description="The sequence of evaluation steps.")
