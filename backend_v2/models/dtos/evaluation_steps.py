"""Evaluation step DTO schemas.

Defines the Pydantic models for strict and semantic evaluation steps
used during matrix execution.
"""

from typing import Annotated, Any, Self, get_args, get_origin

from pydantic import ConfigDict, Field, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.prompts.field_prompts import DESC_CONTEXTUAL_OVERRIDE, DESC_EXACT_QUOTES


class BaseExtractionDTO(V2CoreBase):
    """Base DTO for extraction operations.

    Enforces common validation behaviors for all step extraction schemas.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    used_source_aliases: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of exact <search_result id> strings you relied upon for this specific extraction.",
        ),
    ] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _sanitize_source_aliases(cls, data: Any) -> Any:
        """Sanitizes source aliases by fixing typos and nullifying invalid ones before Literal validation."""
        try:
            d = dict(data)
        except TypeError, ValueError:
            return data

        for list_field in ["used_source_aliases", "source_document_aliases"]:
            raw_list = d.get(list_field)
            if isinstance(raw_list, list):
                field_info = cls.model_fields.get(list_field)
                if not field_info:
                    continue

                valid_literals = set()
                args = get_args(field_info.annotation)
                if args:
                    item_type = args[0]
                    if get_origin(item_type) is Annotated:
                        item_type = get_args(item_type)[0]

                    literal_args = get_args(item_type)
                    if literal_args:
                        valid_literals = set(literal_args)

                cleaned = []
                for alias in raw_list:
                    if not isinstance(alias, str):
                        cleaned.append(alias)
                        continue

                    a = alias.strip()
                    if a.startswith("src") and len(a) > 3 and a[3].isdigit():
                        a = f"src_{a[3:]}"

                    if valid_literals and a not in valid_literals and "N/A" in valid_literals:
                        a = "N/A"

                    cleaned.append(a)
                d[list_field] = cleaned

        return d


class StepDTOStrict(BaseExtractionDTO):
    """Strict step evaluation DTO.

    Represents a single step in a strict evaluation workflow.

    Attributes:
        rule_internalization: Brief internalization of the rule requirements.
        source_document_aliases: Dynamic literals corresponding to available documents.
        exact_quotes: Verbatim quotes in original language.
        reasoning_steps: Step by step breakdown of the text reasoning.
        falsification_argument: Critical counter-argument details.
        decision: Final strict binary compliance decision.
        semantic_reasoning: Short summary statement of decision logic.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    rule_internalization: Annotated[
        str,
        Field(description="Brief internalization of the rule requirements and criteria in English."),
    ]
    source_document_aliases: Annotated[
        list[str],
        Field(description="Dynamic literals corresponding to available documents."),
    ]
    exact_quotes: Annotated[list[LLMExtractedQuote], Field(description=DESC_EXACT_QUOTES)]
    reasoning_steps: Annotated[
        str,
        Field(
            description="Step-by-step mechanical audit trace BEFORE making a decision. "
            "Format: '1) Rule requires X. 2) Text provides Y. 3) Y meets/fails X.' Max 3 sentences."
        ),
    ]
    falsification_argument: Annotated[
        str | None,
        Field(description="Why this evidence might NOT satisfy the strict causal requirement of the rule."),
    ] = None
    semantic_reasoning: Annotated[
        str,
        Field(
            description=(
                "Final summary of the decision. You MUST use Markdown formatting "
                "(e.g. bolding, bullet points, headers) INSIDE this JSON string to structure your analysis."
            )
        ),
    ]
    decision: Annotated[bool, Field(description="True if the condition is physically met, False otherwise.")]


class StepDTOSemantic(StepDTOStrict):
    """Semantic step evaluation DTO.

    Represents a single step in a semantic evaluation workflow with override option.

    Attributes:
        contextual_override: Flag indicating if semantic override was applied.
        override_reason: Justification details for the contextual override.
    """

    override_reason: Annotated[str | None, Field(description="Explanation for the contextual override.")] = None
    contextual_override: Annotated[
        bool,
        Field(description=DESC_CONTEXTUAL_OVERRIDE),
    ] = False

    @model_validator(mode="after")
    def _enforce_override_exclusivity(self) -> Self:
        """Enforces that exact_quotes is empty if contextual_override is True."""
        if self.contextual_override and self.exact_quotes:
            return self.model_copy(update={"exact_quotes": []})
        return self


class ParsingLogStepsStrict(BaseExtractionDTO):
    """Strict evaluation log envelope DTO.

    Wraps a list of strict step DTOs.

    Attributes:
        steps: Sequential list of strict evaluation steps.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    steps: Annotated[list[StepDTOStrict], Field(description="The sequence of evaluation steps.")]


class ParsingLogStepsSemantic(BaseExtractionDTO):
    """Semantic evaluation log envelope DTO.

    Wraps a list of semantic step DTOs.

    Attributes:
        steps: Sequential list of semantic evaluation steps.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    steps: Annotated[list[StepDTOSemantic], Field(description="The sequence of evaluation steps.")]
