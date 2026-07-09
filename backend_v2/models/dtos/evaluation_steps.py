"""Evaluation step DTO schemas.

Defines the Pydantic models for strict and semantic evaluation steps
used during matrix execution.
"""

from types import UnionType
from typing import Any, Union, get_args, get_origin

from pydantic import Field, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.prompts.field_prompts import DESC_CONTEXTUAL_OVERRIDE, DESC_EXACT_QUOTES


class BaseExtractionDTO(V2CoreBase):
    """Base DTO for extraction operations.

    Enforces common validation behaviors for all step extraction schemas.
    """

    used_source_aliases: list[str] = Field(
        ...,
        description="List of exact <search_result id> strings you relied upon for this specific extraction.",
    )

    @model_validator(mode="before")
    @classmethod
    def _enforce_contextual_override_exclusivity(cls, data: Any) -> Any:
        """Enforces contextual override exclusivity, sanitizes null lists, and coerces N/A strings.

        Args:
            data: Raw dictionary or input payload.

        Returns:
            The sanitized data with exact_quotes cleared if contextual_override is True,
            null lists converted to empty lists, and 'N/A' strings coerced to None.
        """
        if isinstance(data, dict):
            if data.get("contextual_override") is True:
                data["exact_quotes"] = []

            # Sanitize null collections for the specific known list fields
            if data.get("used_source_aliases") is None:
                data["used_source_aliases"] = []
            if data.get("source_document_aliases") is None:
                data["source_document_aliases"] = []
            if data.get("exact_quotes") is None:
                data["exact_quotes"] = []

            # Coerce N/A strings to None only if the field allows it
            junk_strings = {"n/a", "-", "none", "null", "ei saatavilla", "not applicable", "empty", "n\\a"}
            for key, value in data.items():
                if isinstance(value, str) and value.strip().lower() in junk_strings:
                    field_info = cls.model_fields.get(key)
                    if field_info is not None:
                        annotation = field_info.annotation
                        origin = get_origin(annotation)
                        args = get_args(annotation)

                        allows_none = (
                            annotation is type(None)
                            or (origin in (Union, UnionType) and type(None) in args)
                            or field_info.default is None
                        )
                        if allows_none:
                            data[key] = None

        return data

    @model_validator(mode="before")
    @classmethod
    def _sanitize_source_aliases(cls, data: Any) -> Any:
        """Sanitizes source aliases by fixing typos and nullifying invalid ones before Literal validation."""
        if not isinstance(data, dict):
            return data

        for list_field in ["used_source_aliases", "source_document_aliases"]:
            if list_field in data and isinstance(data[list_field], list):
                field_info = cls.model_fields.get(list_field)
                if not field_info:
                    continue

                valid_literals = set()
                args = get_args(field_info.annotation)
                if args:
                    item_type = args[0]
                    from typing import Annotated

                    if get_origin(item_type) is Annotated:
                        item_type = get_args(item_type)[0]

                    literal_args = get_args(item_type)
                    if literal_args:
                        valid_literals = set(literal_args)

                cleaned = []
                for alias in data[list_field]:
                    if not isinstance(alias, str):
                        cleaned.append(alias)
                        continue

                    a = alias.strip()
                    if a.startswith("src") and len(a) > 3 and a[3].isdigit():
                        a = f"src_{a[3:]}"

                    if valid_literals and a not in valid_literals and "N/A" in valid_literals:
                        a = "N/A"

                    cleaned.append(a)
                data[list_field] = cleaned

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
        ...,
        description="Dynamic literals corresponding to available documents.",
    )
    exact_quotes: list[LLMExtractedQuote] = Field(..., description=DESC_EXACT_QUOTES)
    reasoning_steps: str = Field(
        description=(
            "Step-by-step mechanical audit trace BEFORE making a decision. "
            "Format: '1) Rule requires X. 2) Text provides Y. 3) Y meets/fails X.' Max 3 sentences."
        )
    )
    falsification_argument: str | None = Field(
        default=None, description="Why this evidence might NOT satisfy the strict causal requirement of the rule."
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
