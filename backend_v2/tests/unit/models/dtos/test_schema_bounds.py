"""Tests verifying JSON schema generation bounds for Vertex AI and structured output compatibility.

Ensures arrays in critical DTOs don't have unbounded/problematic maxItems limits.
"""

from backend_v2.models.dtos.evaluation_steps import StepDTOStrict


def test_step_dto_strict_array_bounds() -> None:
    """Verify StepDTOStrict DOES NOT have maxItems on array fields."""
    schema = StepDTOStrict.model_json_schema()
    properties = schema["properties"] if "properties" in schema else {}

    exact_quotes_prop = properties["exact_quotes"] if "exact_quotes" in properties else {}
    source_aliases_prop = properties["source_document_aliases"] if "source_document_aliases" in properties else {}
    used_aliases_prop = properties["used_source_aliases"] if "used_source_aliases" in properties else {}

    assert "maxItems" not in exact_quotes_prop, (
        "CRITICAL: exact_quotes array has maxItems bound! This causes Vertex AI 400 'too many states for serving'."
    )

    assert "maxItems" not in source_aliases_prop, "CRITICAL: source_document_aliases array has maxItems bound!"
    assert "maxItems" not in used_aliases_prop, "CRITICAL: used_source_aliases array has maxItems bound!"


def test_schema_factory_atom_response_has_bounded_arrays() -> None:
    """Verify the full atom response schema chain DOES NOT have maxItems everywhere.

    This test simulates what schema_factory.py produces when
    has_shuffled_atoms=True: AtomResponseStrict inherits from StepDTOStrict.
    """
    from typing import Literal

    from pydantic import BaseModel, ConfigDict, Field, create_model

    from backend_v2.models.dtos.evaluation_steps import StepDTOStrict

    DocIdsLiteral = Literal["src_0", "src_1", "src_2", "N/A"]

    step_strict_dynamic = create_model(
        "StepDTOStrictDynamic",
        __base__=StepDTOStrict,
        source_document_aliases=(
            list[DocIdsLiteral],
            Field(..., description="Dynamic literals corresponding to available documents."),
        ),
        __config__=ConfigDict(extra="forbid", strict=True, frozen=True),
    )

    schema = step_strict_dynamic.model_json_schema()
    props = schema["properties"] if "properties" in schema else {}
    doc_aliases = props["source_document_aliases"] if "source_document_aliases" in props else {}
    assert "maxItems" not in doc_aliases, "CRITICAL: StepDTOStrictDynamic.source_document_aliases has maxItems!"

    exact_quotes = props["exact_quotes"] if "exact_quotes" in props else {}
    assert "maxItems" not in exact_quotes, "exact_quotes has maxItems in dynamic subclass!"

    class AtomResponseBase(BaseModel):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
        atom_id: str = Field(..., description="Atom ID")

    class AtomResponseStrict(step_strict_dynamic, AtomResponseBase):  # type: ignore[misc, valid-type]
        pass

    atom_schema = AtomResponseStrict.model_json_schema()
    atom_props = atom_schema["properties"] if "properties" in atom_schema else {}

    atom_quotes = atom_props["exact_quotes"] if "exact_quotes" in atom_props else {}
    assert "maxItems" not in atom_quotes, "AtomResponseStrict has maxItems on exact_quotes!"
    atom_doc_aliases = atom_props["source_document_aliases"] if "source_document_aliases" in atom_props else {}
    assert "maxItems" not in atom_doc_aliases, "AtomResponseStrict has maxItems on source_document_aliases!"
    atom_used_aliases = atom_props["used_source_aliases"] if "used_source_aliases" in atom_props else {}
    assert "maxItems" not in atom_used_aliases, "AtomResponseStrict has maxItems on used_source_aliases!"
