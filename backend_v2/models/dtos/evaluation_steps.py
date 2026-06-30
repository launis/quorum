"""Evaluation step DTO schemas.

Defines the Pydantic models for strict and semantic evaluation steps
used during matrix execution.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.prompts.field_prompts import DESC_CONTEXTUAL_OVERRIDE, DESC_EXACT_QUOTES


class BaseExtractionDTO(BaseModel):
    """Base DTO for extraction operations.

    Enforces common validation behaviors for all step extraction schemas.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    used_source_aliases: list[str] = Field(
        default_factory=list,
        description="List of exact <search_result id> strings you relied upon for this specific extraction.",
    )

    @model_validator(mode="before")
    @classmethod
    def _enforce_contextual_override_exclusivity(cls, data: Any) -> Any:
        """Enforces contextual override exclusivity before validation.

        Args:
            data: Raw dictionary or input payload.

        Returns:
            The sanitized data with exact_quotes cleared if contextual_override is True.
        """
        if isinstance(data, dict):
            if data.get("contextual_override") is True:
                data["exact_quotes"] = []
        return data


class StepDTOStrict(BaseExtractionDTO):
    """Strict step evaluation DTO.

    Represents a single step in a strict evaluation workflow.

    Attributes:
        rule_internalization: Brief internalization of the rule requirements.
        source_document_ids: Dynamic literals corresponding to available documents.
        exact_quotes: Verbatim quotes in original language.
        reasoning_steps: Step by step breakdown of the text reasoning.
        falsification_argument: Critical counter-argument details.
        decision: Final strict binary compliance decision.
        semantic_reasoning: Short summary statement of decision logic.
    """

    rule_internalization: str = Field(
        description="Brief internalization of the rule requirements and criteria in English."
    )
    source_document_aliases: list[str] = Field(
        default_factory=list, description="Dynamic literals corresponding to available documents."
    )
    exact_quotes: list[LLMExtractedQuote] = Field(default_factory=list, description=DESC_EXACT_QUOTES)
    reasoning_steps: str = Field(
        description=(
            "Step-by-step mechanical audit trace BEFORE making a decision. "
            "Format: '1) Rule requires X. 2) Text provides Y. 3) Y meets/fails X.' Max 3 sentences."
        )
    )
    falsification_argument: str = Field(
        description="Why this evidence might NOT satisfy the strict causal requirement of the rule."
    )
    decision: bool = Field(description="True if the condition is physically met, False otherwise.")
    semantic_reasoning: str = Field(
        description="Final summary of the decision. You MUST use Markdown formatting (e.g. bolding, bullet points, headers) INSIDE this JSON string to structure your analysis."
    )


class StepDTOSemantic(StepDTOStrict):
    """Semantic step evaluation DTO.

    Represents a single step in a semantic evaluation workflow with override option.

    Attributes:
        contextual_override: Flag indicating if semantic override was applied.
        override_reason: Justification details for the contextual override.
    """

    contextual_override: bool = Field(
        default=False,
        description=DESC_CONTEXTUAL_OVERRIDE,
    )
    override_reason: str | None = Field(default=None, description="Explanation for the contextual override.")


class ParsingLogStepsStrict(BaseExtractionDTO):
    """Strict evaluation log envelope DTO.

    Wraps a list of strict step DTOs.

    Attributes:
        steps: Sequential list of strict evaluation steps.
    """

    steps: list[StepDTOStrict] = Field(description="The sequence of evaluation steps.")


class ParsingLogStepsSemantic(BaseExtractionDTO):
    """Semantic evaluation log envelope DTO.

    Wraps a list of semantic step DTOs.

    Attributes:
        steps: Sequential list of semantic evaluation steps.
    """

    steps: list[StepDTOSemantic] = Field(description="The sequence of evaluation steps.")
