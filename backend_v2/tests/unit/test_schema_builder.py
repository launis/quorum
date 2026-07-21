import pytest
from pydantic import ValidationError

from backend_v2.llm.schema_builder import SchemaCompilerService
from backend_v2.models.enums import BlockDataType, PromptBlockCategory, XaiExtensionType
from backend_v2.models.v2_core import I18nText, PromptBlock


def create_mock_block(slug: str, btype: BlockDataType, extensions: list[str]) -> PromptBlock:
    """Helper to create a valid V2 PromptBlock for schema testing."""
    return PromptBlock(
        id="blk_1234567890abcdef1234567890abcdef",
        slug=slug,
        label=I18nText(default_locale="en", translations={"en": "Test Label", "fi": "Test Label"}),
        description=I18nText(default_locale="en", translations={"en": "Test Desc", "fi": "Test Desc"}),
        ai_description="Test AI instruction",
        category_id=PromptBlockCategory.SYSTEM_RULE,
        is_evaluative=True,
        type=btype,
        allow_decimals=False,
        output_extensions=extensions,
    )


def test_schema_compiler_basic_compile() -> None:
    """Test that a PromptBlock successfully compiles into a strict Pydantic model."""
    block = create_mock_block("test_metric", BlockDataType.FLOAT, [])

    DynamicModel = SchemaCompilerService.compile([block])

    # Should validate correct data using the alias
    instance = DynamicModel.model_validate({"eval_1": 3.5})
    assert instance.model_dump()["blk_1234567890abcdef1234567890abcdef"] == 3.5

    # Should forbid extra fields due to strict=True, extra='forbid'
    with pytest.raises(ValidationError):
        DynamicModel.model_validate({"eval_1": 3.5, "extra_field": "bad"})


def test_schema_compiler_xai_extensions() -> None:
    """Test that Anti-Sycophancy XAI Extensions are correctly injected."""
    block = create_mock_block(
        "obs_1",
        BlockDataType.STRING,
        [XaiExtensionType.COACHING.value, XaiExtensionType.FALSIFICATION.value],
    )

    DynamicModel = SchemaCompilerService.compile([block])
    schema = DynamicModel.model_json_schema()

    properties = schema.get("properties", {})
    assert "eval_1" in properties

    coaching_key = f"eval_1_{XaiExtensionType.COACHING.value}"
    falsification_key = f"eval_1_{XaiExtensionType.FALSIFICATION.value}"

    assert coaching_key in properties
    assert falsification_key in properties

    # Verify Anti-Sycophancy descriptions were applied
    assert "STRICT MANDATE" in properties[coaching_key]["description"]
    assert "STRICT MANDATE" in properties[falsification_key]["description"]
