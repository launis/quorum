import pytest

from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import I18nText, PromptBlock
from backend_v2.services.orchestrator.schema_factory import SchemaFactory


@pytest.mark.asyncio
async def test_tier4_reasoning_trace_truncation_bug() -> None:
    """Reproduces the token limit bug where reasoning_trace eats all tokens.

    If reasoning_trace is the first field in the schema, the LLM starts writing
    a massive markdown string. If it hits max_tokens, the JSON is truncated.
    UniversalIngress heals the JSON syntax by appending `"}`, but Pydantic
    throws a ValidationError because the subsequent required fields
    (evaluation_notes, eval_1) are completely missing.
    """
    # 1. Create a dynamic schema using SchemaFactory
    factory = SchemaFactory(resolve_i18n_fn=lambda data, locale: data.translations.get(locale, ""))
    criteria = [
        PromptBlock(
            id="blk_0000000000000000",
            slug="test_slug",
            category_id=PromptBlockCategory.SYSTEM_RULE,
            type=BlockDataType.INSTRUCTION,
            label=I18nText(default_locale="fi", translations={"fi": "Testi", "en": "Test"}),
            description=I18nText(default_locale="fi", translations={"fi": "Kuvaus", "en": "Desc"}),
        )
    ]

    schema_model = factory.build_dynamic_schema(
        schema_name="TestSchema",
        has_search_result=False,
        has_shuffled_atoms=False,
        target_locale="fi",
        criteria=criteria,
        strictness_level=100,
    )

    # 2. Verify that reasoning_trace is the LAST field in the schema model
    field_keys = list(schema_model.model_fields.keys())
    assert field_keys[-1] == "reasoning_trace", (
        "reasoning_trace should be the LAST field to prevent token limit truncation errors!"
    )
    assert field_keys[-2] == "evaluation_notes", "evaluation_notes should be the second to last field!"
