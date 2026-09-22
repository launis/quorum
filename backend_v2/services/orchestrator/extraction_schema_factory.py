from __future__ import annotations

"""Dynamic Pydantic model factory for Decoupled TDA Architecture.

Constructs exact JSON schemas for LLM structured outputs dynamically at runtime,
enforcing strict validation, deterministic sorting, and Zero-Compromise pledges.
"""

import logging
import secrets
from collections.abc import MutableMapping
from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, create_model, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.prompts.common import DESC_CONTEXTUAL_OVERRIDE

__all__ = [
    "DynamicExtractionResponseBase",
    "ExtractedFactsDTOBase",
    "create_extraction_model",
]

logger = logging.getLogger(__name__)


class ExtractedFactsDTOBase(BaseModel):
    """Base class for dynamically compiled ExtractedFactsDTO, enforcing validation rules.

    Attributes:
        model_config: Strict Pydantic configuration forbidding extra attributes.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True, populate_by_name=True)

    def __getitem__(self, key: str) -> Any:
        """Allow subscript access to extracted facts by fact key.

        Args:
            key: Fact attribute name to access.

        Returns:
            Extracted fact value.
        """
        return self.model_dump()[key]

    @model_validator(mode="before")
    @classmethod
    def canonicalise_nulls(cls, data: Any) -> Any:
        """Map cosmetic placeholder strings to None silently before validation.

        Args:
            data: Raw input dictionary or scalar data.

        Returns:
            Sanitized data structure with cosmetic placeholders replaced with None.

        Raises:
            AppException: If input data is an unexpected non-dictionary container.
        """
        # Map cosmetic placeholders to None
        if isinstance(data, MutableMapping):
            placeholder_set = {"none", "n/a", "", None}
            for key, val in list(data.items()):
                if isinstance(val, str) and val.strip().lower() in placeholder_set:
                    data[key] = None
        elif data is not None and not isinstance(data, (str, int, float, bool, list)):
            logger.error(
                "[ExtractedFactsDTOBase] %s: Expected dictionary for canonicalise_nulls, got %s",
                ErrorCodes.VALIDATION_FAILED.name,
                type(data).__name__,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=f"Expected dictionary payload for dynamic extraction, got {type(data).__name__}",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return data


class DynamicExtractionResponseBase(BaseModel):
    """Base class for dynamically compiled DynamicExtractionResponse, enforcing global validation rules.

    Attributes:
        model_config: Strict Pydantic configuration forbidding extra attributes.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    @model_validator(mode="before")
    @classmethod
    def canonicalise_nulls(cls, data: Any) -> Any:
        """Map cosmetic placeholder strings to None silently ONLY for search_context_anchor.

        Args:
            data: Raw input dictionary or scalar data.

        Returns:
            Sanitized data structure with cosmetic placeholders replaced with None for search_context_anchor.

        Raises:
            AppException: If input data is an unexpected non-dictionary container.
        """
        # Map cosmetic placeholders to None silently ONLY for search_context_anchor
        if isinstance(data, MutableMapping):
            placeholder_set = {"none", "n/a", "", None}
            if "search_context_anchor" in data:
                val = data["search_context_anchor"]
                if isinstance(val, str) and val.strip().lower() in placeholder_set:
                    data["search_context_anchor"] = None
        elif data is not None and not isinstance(data, (str, int, float, bool, list)):
            logger.error(
                "[DynamicExtractionResponseBase] %s: Expected dictionary for canonicalise_nulls, got %s",
                ErrorCodes.VALIDATION_FAILED.name,
                type(data).__name__,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=f"Expected dictionary payload for extraction response, got {type(data).__name__}",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return data

    @model_validator(mode="after")
    def validate_lazy_dumping(self, info: ValidationInfo) -> DynamicExtractionResponseBase:
        """Enforce Lazy Dumping Ban (>80% of source text).

        Args:
            info: Pydantic validation context containing source_text.

        Returns:
            Self instance if validation passes.

        Raises:
            ValueError: If quote length exceeds 80% of source text.
        """
        # Phase 1, Milestone 2: Enforce Lazy Dumping Ban (>80% of source text)
        context = info.context
        if context and "source_text" in context:
            source_text = context["source_text"]
            if source_text:
                limit = 0.80 * len(source_text)

                # Check search_context_anchor
                model_dict = self.model_dump()
                if "search_context_anchor" in model_dict:
                    anchor = model_dict["search_context_anchor"]
                    if isinstance(anchor, str) and len(anchor) > limit:
                        raise ValueError(
                            f"Lazy dumping detected for search_context_anchor: quote length "
                            f"({len(anchor)}) exceeds 80% of source_text length ({len(source_text)})."
                        )

                # Check all fields inside extracted_facts
                if "extracted_facts" in model_dict and model_dict["extracted_facts"]:
                    facts_dict = model_dict["extracted_facts"]
                    for key, val in facts_dict.items():
                        if isinstance(val, str) and len(val) > limit:
                            raise ValueError(
                                f"Lazy dumping detected for fact '{key}': extracted quote length "
                                f"({len(val)}) exceeds 80% of source_text length ({len(source_text)})."
                            )
        return self


def create_extraction_model(
    facts: list[str],
    track: Literal["EXTRACTIVE_SENSOR", "COGNITIVE_JUDGEMENT"] = "EXTRACTIVE_SENSOR",
) -> type[BaseModel]:
    """Create a strict Pydantic model for a given list of facts.

    The function sorts facts alphabetically to ensure a deterministic field order,
    enforcing prompt caching stability.

    Args:
        facts: List of facts to extract.
        track: The extraction track to use.

    Returns:
        A dynamically generated subclass of BaseModel ready for model_validate.
    """
    # 1. Deduplicate and sort for deterministic schema generation (caching-friendly)
    unique_facts = sorted(set(facts))

    # 2. Build the dynamic ExtractedFactsDTO model
    facts_fields: dict[str, tuple[Any, Any]] = {}
    for index, fact in enumerate(unique_facts):
        alias_name = f"fact_{index + 1}"
        facts_fields[fact] = (
            str | None,
            Field(default=None, description=f"Extracted value for '{fact}'", alias=alias_name),
        )

    model_suffix = secrets.token_hex(4)
    extracted_facts_dto_name = f"ExtractedFactsDTO_{model_suffix}"

    create_model_fn: Any = create_model
    ExtractedFactsDTO = create_model_fn(
        extracted_facts_dto_name,
        __base__=ExtractedFactsDTOBase,
        __config__=ConfigDict(populate_by_name=True, extra="forbid", strict=True, frozen=True),
        **facts_fields,
    )

    # 3. Build the dynamic DynamicExtractionResponse root model
    root_fields: dict[str, tuple[Any, Any]] = {
        "chunk_index": (int, Field(..., description="Zero-based index of the chunk")),
        "context_scan_trace": (str, Field(..., max_length=400, description="Short trace of LLM reasoning")),
        "search_context_anchor": (str | None, Field(default=None, description="Optional raw quote anchor")),
        "contextual_override": (bool, Field(default=False, description=DESC_CONTEXTUAL_OVERRIDE)),
        "semantic_reasoning": (str, Field(default="", description="Detailed semantic explanation")),
    }

    if track == "COGNITIVE_JUDGEMENT":
        root_fields["validation_decision"] = (
            bool,
            Field(..., description="Validation decision on cognitive judgement track"),
        )

    root_fields["extracted_facts"] = (
        ExtractedFactsDTO,
        Field(..., description="Extracted facts DTO"),
    )

    response_model_name = f"DynamicExtractionResponse_{model_suffix}"
    DynamicExtractionResponse = create_model_fn(
        response_model_name,
        __base__=DynamicExtractionResponseBase,
        __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
        **root_fields,
    )

    return cast(type[BaseModel], DynamicExtractionResponse)
