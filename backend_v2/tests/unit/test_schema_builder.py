import pytest
from pydantic import ValidationError

from backend_v2.llm.schema_builder import SchemaCompilerService
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock, SystemRulePromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory, XaiExtensionType
from backend_v2.models.prompts.common import (
    XAI_DESC_EMOTIONAL_SENTIMENT,
    XAI_DESC_MISSING_CONTEXT,
    XAI_DESC_REMEDIATION_STEPS,
    XAI_DESC_RISK_FLAG,
    XAI_DESC_THEORY_LINK,
)
from backend_v2.models.v2_core import I18nText


def create_mock_block(slug: str, btype: BlockDataType, extensions: list[str]) -> PromptBlock:
    """Helper to create a valid V2 PromptBlock for schema testing."""
    if btype in (BlockDataType.FLOAT, BlockDataType.INT):
        from backend_v2.models.v2_core import MatrixClaim, MatrixScale, TDAAssertion

        scale = MatrixScale(
            score=1,
            ai_label="TEST",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": "Test"}),
                    tda_assertions=[
                        TDAAssertion(
                            concept_description="Concept test",
                            inverse_evidence=False,
                            aggregation_mode="EXISTS",
                        )
                    ],
                )
            ],
        )
        return MatrixPromptBlock(
            id="blk_1234567890abcdef1234567890abcdef",
            slug=slug,
            label=I18nText(translations={"en": "Test Label", "fi": "Test Label"}),
            description=I18nText(translations={"en": "Test Desc", "fi": "Test Desc"}),
            ai_description="Test AI instruction",
            category_id=PromptBlockCategory.MATRIX,
            is_evaluative=True,
            type=btype,
            allow_decimals=False,
            output_extensions=extensions,
            scales=[scale],
        )
    return SystemRulePromptBlock(
        id="blk_1234567890abcdef1234567890abcdef",
        slug=slug,
        label=I18nText(translations={"en": "Test Label", "fi": "Test Label"}),
        description=I18nText(translations={"en": "Test Desc", "fi": "Test Desc"}),
        instruction_text="Test AI instruction",
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


def test_schema_compiler_all_xai_extensions_descriptions() -> None:
    """Test that all 5 advanced XAI Extensions are injected with SSOT descriptions."""
    block = create_mock_block(
        "obs_2",
        BlockDataType.STRING,
        [
            XaiExtensionType.MISSING_CONTEXT.value,
            XaiExtensionType.RISK_FLAG.value,
            XaiExtensionType.REMEDIATION_STEPS.value,
            XaiExtensionType.EMOTIONAL_SENTIMENT.value,
            XaiExtensionType.THEORY_LINK.value,
        ],
    )

    DynamicModel = SchemaCompilerService.compile([block])
    schema = DynamicModel.model_json_schema()
    props = schema.get("properties", {})

    assert props[f"eval_1_{XaiExtensionType.MISSING_CONTEXT.value}"]["description"] == XAI_DESC_MISSING_CONTEXT
    assert props[f"eval_1_{XaiExtensionType.RISK_FLAG.value}"]["description"] == XAI_DESC_RISK_FLAG
    assert props[f"eval_1_{XaiExtensionType.REMEDIATION_STEPS.value}"]["description"] == XAI_DESC_REMEDIATION_STEPS
    assert props[f"eval_1_{XaiExtensionType.EMOTIONAL_SENTIMENT.value}"]["description"] == XAI_DESC_EMOTIONAL_SENTIMENT
    assert props[f"eval_1_{XaiExtensionType.THEORY_LINK.value}"]["description"] == XAI_DESC_THEORY_LINK

