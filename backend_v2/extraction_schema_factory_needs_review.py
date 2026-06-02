"""Dynamic Pydantic model factory for EPIC 56.

The backend processes PDF/HTML chunks in parallel workers. Each chunk receives a
list of *facts_to_find* that the LLM must populate. To enforce the
`extra='forbid'` and `strict=True` guarantees required by the Zero-Compromise
pledge, we generate a model **at runtime** using ``pydantic.create_model``.

The generated model includes:
1. ``chunk_index`` – the zero-based index of the processed chunk.
2. ``localized_anchors_found`` – Keywords in target language mapping English rule.
3. ``semantic_reasoning`` – LLM explains its mapping logic briefly.
4. ``exact_quote`` – The physical extraction verbatim quote.
5. ``contextual_override`` – Escape hatch for implicit matches.
6. One nullable ``str`` field per fact, ordered alphabetically.

All fields inherit the strict configuration so that missing or unexpected keys
raise a ``ValidationError`` which is then turned into a deterministic ``DLQ``
state by the downstream evaluator.
"""

from __future__ import annotations

import logging
import secrets
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field, create_model, model_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


def _standard_fields() -> dict[str, Any]:
    """Base fields that exist on every extraction model.

    ``chunk_index`` is required for deterministic *First-Wins* merging.
    The remaining 4 fields enforce the Zero-Variance Extract-and-Justify schema.

    Returns:
        dict[str, Any]: A dictionary representing base fields for model creation.
    """
    return {
        "chunk_index": (int, Field(..., description="Zero-based index of the chunk")),
        "localized_anchors_found": (
            list[str],
            Field(
                ...,
                description="Keywords in target language mapping English rule.",
            ),
        ),
        "semantic_reasoning": (str, Field(..., description="LLM explains its mapping logic briefly.")),
        "exact_quote": (str | None, Field(..., description="The physical extraction verbatim quote.")),
        "contextual_override": (
            bool,
            Field(..., description="Escape hatch for implicit matches."),
        ),
    }


def create_extraction_model(facts_to_find: list[str]) -> type[BaseModel]:
    """Create a strict Pydantic model for a given list of facts.

    The function sorts ``facts_to_find`` alphabetically to ensure a **deterministic
    field order** – a prerequisite for Prompt-Caching stability. Each fact becomes
    a nullable ``str`` field. The resulting model enforces ``extra='forbid'`` and
    ``strict=True`` so that any stray keys cause a validation error.

    Example::

        Model = create_extraction_model(["vaatimus_A", "poikkeus_B"])
        payload = Model(
            chunk_index=0,
            localized_anchors_found=["sääntö"],
            semantic_reasoning="reasoning text...",
            exact_quote="matched quote",
            contextual_override=False,
            vaatimus_A="some text",
            poikkeus_B=None,
        )

    Args:
        facts_to_find: A list of facts to extract.

    Returns:
        type[BaseModel]: A dynamically generated subclass of BaseModel ready for model_validate.

    Raises:
        AppException: If runtime schema creation fails.
    """
    # Deduplicate and sort for deterministic schema generation
    unique_facts = sorted(set(facts_to_find))

    # Prepare the field definitions dict expected by ``create_model``
    fields: dict[str, Any] = _standard_fields()
    for fact in unique_facts:
        # Each fact is optional (nullable) – LLM may legitimately return null.
        fields[fact] = (str | None, Field(None, description=f"Extracted value for '{fact}'"))

    # Dynamically build the model class
    model_name = f"ExtractionSchema_{secrets.token_hex(4)}"
    try:
        DynamicModel = create_model(
            model_name,
            __config__=ConfigDict(extra="forbid", strict=True),
            **fields,
        )
    except Exception as e:
        logger.error(
            "Failed to dynamically construct extraction schema: %s",
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED},
        )
        raise AppException(
            message=f"Dynamic schema instantiation aborted: {str(e)}",
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED},
        ) from e

    # Post-validation normalisation: treat common placeholder strings as ``None``.
    @model_validator(mode="before")
    def _canonicalise_nulls(cls: Any, data: Any) -> Any:
        if isinstance(data, dict):
            placeholder_set = {"none", "n/a", "", None}
            for key, val in list(data.items()):
                if isinstance(val, str) and val.strip().lower() in placeholder_set:
                    data[key] = None
        return data

    # Attach the validator to the generated class
    DynamicModel._canonicalise_nulls = _canonicalise_nulls

    return cast(type[BaseModel], DynamicModel)
