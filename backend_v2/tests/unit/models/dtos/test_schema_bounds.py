"""Tests for Vertex AI schema array bounds.

Verifies that all Pydantic models used in LLM Structured Output have
explicit maxItems bounds to prevent Vertex AI 400 'too many states' errors.
"""

from backend_v2.models.dtos.evaluation_steps import StepDTOStrict


def test_step_dto_strict_array_bounds() -> None:
    """Verify StepDTOStrict has maxItems on all array fields."""
    schema = StepDTOStrict.model_json_schema()
    properties = schema.get("properties", {})

    exact_quotes_prop = properties.get("exact_quotes", {})
    source_aliases_prop = properties.get("source_document_aliases", {})
    used_aliases_prop = properties.get("used_source_aliases", {})

    # Phase 1, Step 1c: exact_quotes must have maxItems
    assert "maxItems" in exact_quotes_prop, (
        "CRITICAL: exact_quotes array is missing maxItems bound! "
        "This causes Vertex AI 400 'too many states for serving'."
    )
    assert exact_quotes_prop["maxItems"] == 5

    # Phase 1, Step 1b: source_document_aliases must have maxItems
    assert "maxItems" in source_aliases_prop, "CRITICAL: source_document_aliases array is missing maxItems bound!"
    assert source_aliases_prop["maxItems"] == 5

    # Phase 1, Step 1a: used_source_aliases must have maxItems
    assert "maxItems" in used_aliases_prop, "CRITICAL: used_source_aliases array is missing maxItems bound!"
    assert used_aliases_prop["maxItems"] == 5


def test_schema_factory_atom_response_has_bounded_arrays() -> None:
    """Verify the full atom response schema chain has maxItems everywhere.

    This test simulates what schema_factory.py produces when
    has_shuffled_atoms=True: AtomResponseStrict inherits from StepDTOStrict.
    The dynamic StepDTOStrictDynamic overrides source_document_aliases
    with Literal types — we verify the override preserves max_length.
    """
    from typing import Literal

    from pydantic import BaseModel, ConfigDict, Field, create_model

    from backend_v2.models.dtos.evaluation_steps import StepDTOStrict

    # Simulate schema_factory.py lines 188-198
    DocIdsLiteral = Literal["src_0", "src_1", "src_2", "N/A"]

    step_strict_dynamic = create_model(
        "StepDTOStrictDynamic",
        __base__=StepDTOStrict,
        source_document_aliases=(
            list[DocIdsLiteral],
            Field(..., max_length=5, description="Dynamic literals corresponding to available documents."),
        ),
        __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
    )

    # Phase 2, Step 2a: Verify dynamic override preserves maxItems
    schema = step_strict_dynamic.model_json_schema()
    props = schema.get("properties", {})
    doc_aliases = props.get("source_document_aliases", {})
    assert "maxItems" in doc_aliases, (
        "CRITICAL: StepDTOStrictDynamic.source_document_aliases lost maxItems after create_model() override!"
    )
    assert doc_aliases["maxItems"] == 5

    # Also verify exact_quotes survived inheritance
    exact_quotes = props.get("exact_quotes", {})
    assert "maxItems" in exact_quotes, "exact_quotes lost maxItems in dynamic subclass!"
    assert exact_quotes["maxItems"] == 5

    # Build full AtomResponseStrict chain
    class AtomResponseBase(BaseModel):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
        atom_id: str = Field(..., description="Atom ID")

    class AtomResponseStrict(step_strict_dynamic, AtomResponseBase):  # type: ignore[misc, valid-type]
        pass

    atom_schema = AtomResponseStrict.model_json_schema()
    atom_props = atom_schema.get("properties", {})

    # Final verification: the full chain maintains all bounds
    assert "maxItems" in atom_props.get("exact_quotes", {}), "AtomResponseStrict lost maxItems on exact_quotes!"
    assert "maxItems" in atom_props.get("source_document_aliases", {}), (
        "AtomResponseStrict lost maxItems on source_document_aliases!"
    )
    assert "maxItems" in atom_props.get("used_source_aliases", {}), (
        "AtomResponseStrict lost maxItems on used_source_aliases!"
    )
