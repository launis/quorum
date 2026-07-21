from unittest.mock import AsyncMock
"""Tests for Vertex AI schema array bounds.

Verifies that all Pydantic models used in LLM Structured Output DO NOT have
explicit maxItems bounds.

Tekoälyn Structured Output -parsereiden matemaattisessa maailmassa sisäkkäiset
maxItems-määritykset luovat kombinaatioräjähdyksen (state machine explosion),
joka kaataa Vertex AI:n 400 'too many states' -virheeseen.

Tästä syystä maxItems-rajoitteet on tarkoituksella jätetty pois JSON-skeemoista.
Pydantic hoitaa datan oikeellisuuden ja pituuksien tarkistuksen turvallisesti
jälkikäteen, kun Vertex AI on palauttanut vastauksensa.
"""

from backend_v2.models.dtos.evaluation_steps import StepDTOStrict


def test_step_dto_strict_array_bounds() -> None:
    """Verify StepDTOStrict DOES NOT have maxItems on array fields."""
    schema = StepDTOStrict.model_json_schema()
    properties = schema.get("properties", {})

    exact_quotes_prop = properties.get("exact_quotes", {})
    source_aliases_prop = properties.get("source_document_aliases", {})
    used_aliases_prop = properties.get("used_source_aliases", {})

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
    props = schema.get("properties", {})
    doc_aliases = props.get("source_document_aliases", {})
    assert "maxItems" not in doc_aliases, "CRITICAL: StepDTOStrictDynamic.source_document_aliases has maxItems!"

    exact_quotes = props.get("exact_quotes", {})
    assert "maxItems" not in exact_quotes, "exact_quotes has maxItems in dynamic subclass!"

    class AtomResponseBase(BaseModel):
        model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
        atom_id: str = Field(..., description="Atom ID")

    class AtomResponseStrict(step_strict_dynamic, AtomResponseBase):  # type: ignore[misc, valid-type]
        pass

    atom_schema = AtomResponseStrict.model_json_schema()
    atom_props = atom_schema.get("properties", {})

    assert "maxItems" not in atom_props.get("exact_quotes", {}), "AtomResponseStrict has maxItems on exact_quotes!"
    assert "maxItems" not in atom_props.get("source_document_aliases", {}), (
        "AtomResponseStrict has maxItems on source_document_aliases!"
    )
    assert "maxItems" not in atom_props.get("used_source_aliases", {}), (
        "AtomResponseStrict has maxItems on used_source_aliases!"
    )
