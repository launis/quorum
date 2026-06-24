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
    model = schema_factory.build_dynamic_schema("EmptySchema", [], strictness_level=50)
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

    class DummyPayload(BaseModel):
        test_field: str

    model = schema_factory.build_chunk_response_schema("ChunkSchema", DummyPayload)

    records = []
    for i in range(22):
        records.append({"original_id": f"id_{i}", "payload": {"test_field": "val"}})

    json_str = '{"chunk_id": "chunk_1", "records": ' + json.dumps(records) + "}"

    with pytest.raises(pydantic.ValidationError) as exc:
        model.model_validate_json(json_str)

    from backend_v2.models.enums import SystemConcurrency

    expected_max = SystemConcurrency.SCHEMA_MAX_CHUNK_RECORDS.value
    assert f"List should have at most {expected_max} items after validation, not 22" in str(exc.value)


def test_dunder_hallucination_rejected_by_extra_forbid() -> None:
    """Verify that LLM dunder-key hallucinations (e.g. __rule_satisfied__) are REJECTED.

    This ensures we enforce Fail-Fast validation instead of silently allowing hallucinations.
    """
    import pydantic

    from backend_v2.services.orchestrator.schema_factory import StrippedBaseTDAExtraction

    # Simulate LLM output with hallucinated __rule_satisfied__ field
    data = {
        "exact_quotes": ["test quote"],
        "contextual_override": False,
        "semantic_reasoning": "Test reasoning",
        "__rule_satisfied__": True,  # <-- LLM hallucination
    }

    # Strict validation MUST reject this to fail-fast and route to DLQ
    with pytest.raises(pydantic.ValidationError) as exc:
        StrippedBaseTDAExtraction.model_validate(data)

    assert "extra_forbidden" in str(exc.value)


def test_normal_typo_still_rejected_by_extra_forbid() -> None:
    """Verify that non-dunder typos still trigger extra_forbidden.

    The before-validator MUST only strip __dunder__ keys, not normal field typos.
    """
    import pydantic

    from backend_v2.services.orchestrator.schema_factory import StrippedBaseTDAExtraction

    data = {
        "exact_quotes": ["test quote"],
        "contextual_override": False,
        "semnatic_reasoning": "Typo field name",  # <-- typo, NOT a dunder
    }

    with pytest.raises(pydantic.ValidationError) as exc:
        StrippedBaseTDAExtraction.model_validate(data)

    assert "extra_forbidden" in str(exc.value)
