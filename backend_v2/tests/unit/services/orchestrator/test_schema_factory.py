"""Unit tests for SchemaFactory dynamic Pydantic schema generation."""

import pytest
from pydantic import BaseModel

from backend_v2.services.orchestrator.schema_factory import SchemaFactory


def dummy_resolve_i18n(text: str, locale: str) -> str:
    """No-op I18n resolver returning the input text unchanged."""
    return text


@pytest.fixture
def schema_factory() -> SchemaFactory:
    return SchemaFactory(resolve_i18n_fn=dummy_resolve_i18n)


def test_build_blind_evaluation_schema(schema_factory: SchemaFactory) -> None:
    """Verify blind evaluation schema contains required evaluations field."""
    model = schema_factory.build_blind_evaluation_schema("BlindSchema")
    assert issubclass(model, BaseModel)
    assert "evaluations" in model.model_fields


def test_build_chunk_response_schema(schema_factory: SchemaFactory) -> None:
    """Verify chunk response schema nests records and chunk_id fields."""

    class DummyPayload(BaseModel):
        test_field: str

    model = schema_factory.build_chunk_response_schema("ChunkSchema", DummyPayload)
    assert issubclass(model, BaseModel)
    assert "records" in model.model_fields
    assert "chunk_id" in model.model_fields


def test_build_dynamic_schema_empty(schema_factory: SchemaFactory) -> None:
    """Verify empty criteria produces fallback reasoning and evaluation fields."""
    model = schema_factory.build_dynamic_schema("EmptySchema", [])
    assert issubclass(model, BaseModel)
    assert "reasoning_trace" in model.model_fields
    assert "evaluation_notes" in model.model_fields


def test_schema_strictness_triggers_dlq_fallback(schema_factory: SchemaFactory) -> None:
    """TDD GREEN: Test that Pydantic strictness correctly triggers a ValidationError
    if the LLM hallucinates extra items beyond the Chunk Size bounds (max_length=10).
    This proves that Fail-Fast works at the boundary, ensuring ChunkWorker delegates to DLQ.
    """
    import json

    import pydantic

    model = schema_factory.build_blind_evaluation_schema("BlindSchema")

    # Create 12 items to simulate LLM array hallucination (Chunk size 10 + 2 hallucinations)
    evaluations = []
    for i in range(12):
        evaluations.append(
            {
                "atom_id": f"tda_fake_{i}",
                "step_1_evidence_type": "NO_EVIDENCE",
                "step_2_quote": None,
                "step_3_implicit_justification": None,
                "step_4_reasoning": "Hallucinated reasoning trace",
                "step_5_boolean": False,
            }
        )

    json_str = '{"evaluations": ' + json.dumps(evaluations) + "}"

    # This MUST fail with ValidationError because max_length is 10.
    # The ChunkWorker's try-except catches this and initiates DLQ.
    with pytest.raises(pydantic.ValidationError) as exc:
        model.model_validate_json(json_str)

    assert "List should have at most 10 items after validation, not 12" in str(exc.value)


def test_dunder_hallucination_stripped_by_before_validator() -> None:
    """Verify that LLM dunder-key hallucinations (e.g. __rule_satisfied__) are silently stripped.

    Reproduces the exact failure from exe_b0a68f2c7bfe4c359331a71fbb777c8a where
    the LLM added __rule_satisfied__: true/false to every evaluation, causing
    10/15 atoms to be lost to DLQ via extra_forbidden.
    """
    from backend_v2.services.orchestrator.schema_factory import StrippedBaseTDAExtraction

    # Simulate LLM output with hallucinated __rule_satisfied__ field
    data = {
        "exact_quote": "test quote",
        "structural_location": "page 1",
        "localized_anchors_found": ["test"],
        "contextual_override": False,
        "semantic_reasoning": "Test reasoning",
        "__rule_satisfied__": True,  # <-- LLM hallucination
    }

    # Before-validator must strip __rule_satisfied__ so this succeeds
    result = StrippedBaseTDAExtraction.model_validate(data)
    assert result.semantic_reasoning == "Test reasoning"
    assert not hasattr(result, "__rule_satisfied__")


def test_normal_typo_still_rejected_by_extra_forbid() -> None:
    """Verify that non-dunder typos still trigger extra_forbidden.

    The before-validator MUST only strip __dunder__ keys, not normal field typos.
    """
    import pydantic

    from backend_v2.services.orchestrator.schema_factory import StrippedBaseTDAExtraction

    data = {
        "exact_quote": "test quote",
        "structural_location": "page 1",
        "localized_anchors_found": [],
        "contextual_override": False,
        "semnatic_reasoning": "Typo field name",  # <-- typo, NOT a dunder
    }

    with pytest.raises(pydantic.ValidationError) as exc:
        StrippedBaseTDAExtraction.model_validate(data)

    assert "extra_forbidden" in str(exc.value)
