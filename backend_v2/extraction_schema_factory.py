# extraction_schema_factory.py
"""Dynamic Pydantic model factory for EPIC 56.

The backend processes PDF/HTML chunks in parallel workers. Each chunk receives a
list of *facts_to_find* that the LLM must populate.  To enforce the
`extra='forbid'` and `strict=True` guarantees required by the Zero‑Compromise
pledge, we generate a model **at runtime** using ``pydantic.create_model``.

The generated model includes:
1. ``chunk_index`` – the zero‑based index of the processed chunk.
2. ``context_scan_trace`` – a short (≤400 chars) trace of the LLM's reasoning.
3. ``search_context_anchor`` – optional raw quote for debugging.
4. One nullable ``str`` field per fact, ordered alphabetically.

All fields inherit the strict configuration so that missing or unexpected keys
raise a ``ValidationError`` which is then turned into a deterministic ``DLQ``
state by the downstream evaluator.
"""

from __future__ import annotations

import secrets
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field, create_model, model_validator


def _standard_fields() -> dict[str, Any]:
    """Base fields that exist on every extraction model.

    ``chunk_index`` is required for deterministic *First‑Wins* merging.
    The remaining 4 fields enforce the Zero-Variance Extract-and-Justify schema.

    Returns:
        Dictionary of Pydantic field definitions.
    """
    return {
        "chunk_index": (int, Field(..., description="Zero‑based index of the chunk")),
        "localized_anchors_found": (
            list[str],
            Field(
                ...,
                description="Keywords in target language mapping English rule.",
            ),
        ),
        "semantic_reasoning": (str, Field(..., description="LLM explains its mapping logic briefly.")),
        "exact_quote": ((str | None), Field(..., description="The physical extraction verbatim quote.")),
        "contextual_override": (
            bool,
            Field(..., description="Escape hatch for implicit matches."),
        ),
    }


def create_extraction_model(facts_to_find: list[str]) -> type[BaseModel]:
    """Create a strict Pydantic model for a given list of facts.

    The function sorts ``facts_to_find`` alphabetically to ensure a **deterministic
    field order** – a prerequisite for Prompt‑Caching stability.  Each fact becomes
    a nullable ``str`` field.  The resulting model enforces ``extra='forbid'`` and
    ``strict=True`` so that any stray keys cause a validation error.

    Args:
        facts_to_find: List of data points to extract (keys for the model).

    Returns:
        A dynamically generated subclass of ``BaseModel`` ready for ``model_validate``.

    Example:
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
    """
    # Deduplicate and sort for deterministic schema generation
    unique_facts = sorted(set(facts_to_find))

    # Prepare the field definitions dict expected by ``create_model``
    fields: dict[str, Any] = _standard_fields()
    for fact in unique_facts:
        # Each fact is optional (nullable) – LLM may legitimately return null.
        fields[fact] = (str | None, Field(None, description=f"Extracted value for '{fact}'"))

    def _canonicalise_nulls(cls: Any, data: Any) -> Any:
        if isinstance(data, dict):
            placeholder_set = {"none", "n/a", "", None}
            for key, val in list(data.items()):
                if isinstance(val, str) and val.strip().lower() in placeholder_set:
                    data[key] = None
        return data

    def _enforce_null_hypothesis(self: Any) -> Any:
        if getattr(self, "contextual_override", False) is True:
            self.exact_quote = None
        return self

    # Dynamically build the model class
    model_name = f"ExtractionSchema_{secrets.token_hex(4)}"

    validators_dict: dict[str, Any] = {
        "canonicalise_nulls": model_validator(mode="before")(_canonicalise_nulls),
        "enforce_null_hypothesis": model_validator(mode="after")(_enforce_null_hypothesis),
    }

    DynamicModel = create_model(
        model_name,
        __config__=ConfigDict(extra="forbid", strict=True),
        __validators__=validators_dict,
        **fields,
    )

    return cast(type[BaseModel], DynamicModel)


# The factory is deliberately lightweight – import it wherever a chunk is processed
# (e.g. in ``worker.py``) and call ``model_validate`` with the appropriate context:
#
#   schema = create_extraction_model(facts)
#   instance = schema.model_validate(payload, context={"source_text": chunk_text})
