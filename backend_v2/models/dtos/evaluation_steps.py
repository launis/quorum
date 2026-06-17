from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BaseExtractionDTO(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _strip_llm_dunder_leaks(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if not (k.startswith("__") and k.endswith("__"))}
        return data


from backend_v2.models.enums import SystemConcurrency


class StepDTOStrict(BaseExtractionDTO):
    reasoning_steps: str = Field(description="Step by step cognitive breakdown of the text. MUST come before decision.")
    exact_quotes: list[str] = Field(
        default_factory=list, max_length=3, description="Physical verbatim matches from the text if condition is met."
    )
    structural_location: str = Field(description="Exact structural location (e.g. 'page 3'). Must be 'N/A' if missing.")
    localized_anchors_found: list[str] = Field(
        default_factory=list,
        max_length=SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS,
        description="Keywords in target language.",
    )
    falsification_argument: str = Field(
        description="Why this evidence might NOT satisfy the strict causal requirement of the rule."
    )
    decision: bool = Field(description="True if the condition is physically met, False otherwise.")
    semantic_reasoning: str = Field(description="Final summary of the decision.")


class StepDTOSemantic(BaseExtractionDTO):
    reasoning_steps: str = Field(description="Step by step cognitive breakdown of the text. MUST come before decision.")
    exact_quotes: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="Verbatim physical quotes from original text. ABSOLUTE PRIORITY. MUST be empty if override is True.",
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
        description="ABSOLUTE LAST RESORT. True only if no literal evidence exists but rule is implicitly matched. exact_quotes MUST be empty if True.",
    )
    override_reason: str | None = Field(default=None, description="Explanation for the contextual override.")
    falsification_argument: str = Field(
        description="Why this evidence might NOT satisfy the strict causal requirement of the rule."
    )
    decision: bool = Field(description="True if the condition is met (physically or semantically), False otherwise.")
    semantic_reasoning: str = Field(description="Final summary of the decision.")

    @model_validator(mode="after")
    def validate_override_logic(self) -> StepDTOSemantic:
        if self.contextual_override:
            if self.exact_quotes and any(
                q not in (None, "", "[CONTEXTUAL_OVERRIDE_APPLIED]") for q in self.exact_quotes
            ):
                raise ValueError(
                    "exact_quotes MUST be empty, null, or '[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is True."
                )
        else:
            if self.exact_quotes and any(q == "[CONTEXTUAL_OVERRIDE_APPLIED]" for q in self.exact_quotes):
                raise ValueError(
                    "exact_quotes cannot contain '[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is False."
                )
        return self


class ParsingLogStepsStrict(BaseExtractionDTO):
    steps: list[StepDTOStrict] = Field(description="The sequence of evaluation steps.")


class ParsingLogStepsSemantic(BaseExtractionDTO):
    steps: list[StepDTOSemantic] = Field(description="The sequence of evaluation steps.")
