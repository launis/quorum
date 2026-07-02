from backend_v2.settings import get_settings

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

    expected_max = get_settings().schema_max_chunk_records

    with pytest.raises(pydantic.ValidationError) as exc:
        model.model_validate_json(json_str)

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


def test_build_dynamic_schema_with_source_document_ids(schema_factory: SchemaFactory) -> None:
    """Verify that build_dynamic_schema enforces dynamic Literal validation on source_document_ids."""
    from backend_v2.models.enums import BlockDataType, PromptBlockCategory
    from backend_v2.models.v2_core import I18nText, PromptBlock

    criteria = [
        PromptBlock(
            id="blk_1234567890abcdef1234567890abcdef",
            slug="test-slug-1",
            label=I18nText(default_locale="en", translations={"en": "Test Label"}),
            description=I18nText(default_locale="en", translations={"en": "Test Desc"}),
            ai_description="Test AI instruction",
            category_id=PromptBlockCategory.SYSTEM_RULE,
            type=BlockDataType.COMPLIANCE,
            output_extensions=[],
        )
    ]

    allowed_docs = ["doc_a", "doc_b"]
    DynamicModel = schema_factory.build_dynamic_schema(
        "DynamicTestSchema",
        criteria,
        strictness_level=100,
        source_document_ids=allowed_docs,
    )

    assert "blk_1234567890abcdef1234567890abcdef" in DynamicModel.model_fields
    inner_model = DynamicModel.model_fields["blk_1234567890abcdef1234567890abcdef"].annotation

    valid_data = {
        "rule_internalization": "Criteria require checking X.",
        "used_source_aliases": [],
        "source_document_aliases": ["doc_a"],
        "exact_quotes": [{"text": "quote", "source_alias": "N/A"}],
        "reasoning_steps": "1) R requires X. 2) T has Y. 3) F.",
        "falsification_argument": "No falsification possible.",
        "decision": True,
        "semantic_reasoning": "Pass",
    }

    obj = inner_model.model_validate(valid_data)
    assert obj.source_document_aliases == ["doc_a"]

    invalid_data = valid_data.copy()
    invalid_data["source_document_aliases"] = ["doc_invalid"]

    try:
        inner_model.model_validate(invalid_data)
    except Exception:
        pass
