"""Dynamic Pydantic model factory for EPIC 56 Decoupled TDA Architecture.

Constructs exact JSON schemas for LLM structured outputs dynamically at runtime,
enforcing strict validation, deterministic sorting, and Zero-Compromise pledges.
"""

from __future__ import annotations

import secrets
from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, create_model, model_validator

from backend_v2.models.prompts.field_prompts import DESC_CONTEXTUAL_OVERRIDE


class ExtractedFactsDTOBase(BaseModel):
    """Base class for dynamically compiled ExtractedFactsDTO, enforcing validation rules."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    @model_validator(mode="before")
    @classmethod
    def canonicalise_nulls(cls, data: Any) -> Any:
        # Phase 1, Milestone 2: Map cosmetic placeholders to None silently
        if isinstance(data, dict):
            placeholder_set = {"none", "n/a", "", None}
            for key, val in list(data.items()):
                if isinstance(val, str) and val.strip().lower() in placeholder_set:
                    data[key] = None
        return data


class DynamicExtractionResponseBase(BaseModel):
    """Base class for dynamically compiled DynamicExtractionResponse, enforcing global validation rules."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    @model_validator(mode="before")
    @classmethod
    def canonicalise_nulls(cls, data: Any) -> Any:
        # Phase 1, Milestone 2: Map cosmetic placeholders to None silently ONLY for search_context_anchor
        if isinstance(data, dict):
            placeholder_set = {"none", "n/a", "", None}
            if "search_context_anchor" in data:
                val = data["search_context_anchor"]
                if isinstance(val, str) and val.strip().lower() in placeholder_set:
                    data["search_context_anchor"] = None
        return data

    @model_validator(mode="after")
    def validate_lazy_dumping(self, info: ValidationInfo) -> DynamicExtractionResponseBase:
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
    facts_fields: dict[str, Any] = {}
    for index, fact in enumerate(unique_facts):
        alias_name = f"fact_{index + 1}"
        facts_fields[fact] = (
            str | None,
            Field(default=None, description=f"Extracted value for '{fact}'", alias=alias_name),
        )

    model_suffix = secrets.token_hex(4)
    extracted_facts_dto_name = f"ExtractedFactsDTO_{model_suffix}"

    ExtractedFactsDTO = create_model(
        extracted_facts_dto_name,
        __base__=ExtractedFactsDTOBase,
        __config__=ConfigDict(populate_by_name=True),
        **facts_fields,
    )

    # 3. Build the dynamic DynamicExtractionResponse root model
    root_fields: dict[str, Any] = {
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
    DynamicExtractionResponse = create_model(
        response_model_name,
        __base__=DynamicExtractionResponseBase,
        **root_fields,
    )

    return cast(type[BaseModel], DynamicExtractionResponse)
