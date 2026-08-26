import pytest
from pydantic import ValidationError

from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, SystemRulePromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, Step, TDAAssertion


def test_prompt_block_allow_decimals_requires_numeric() -> None:
    # Valid setup
    label = I18nText(translations={"fi": "Testi", "en": "Test"})
    desc = I18nText(translations={"fi": "Kuvaus", "en": "Desc"})
    tda = TDAAssertion(
        tda_id="tda_11111111111111111111111111111111",
        concept_description="Valid concept description",
        aggregation_mode="ALL_MUST_COMPLY",
        inverse_evidence=False,
        depends_on=(),
    )
    claim = MatrixClaim(label=label, tda_assertions=[tda])
    scale = MatrixScale(score=1, ai_label="Level 1", claims=[claim])

    valid_block = MatrixPromptBlock(
        id="blk_eeee5555eeee5555",
        slug="valid_slug",
        label=label,
        description=desc,
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        allow_decimals=True,
        output_extensions=[],
        scales=[scale],
    )
    assert valid_block.allow_decimals is True

    # Should raise error for incompatible type with MatrixPromptBlock
    with pytest.raises(ValidationError) as exc_info:
        MatrixPromptBlock(
            id="blk_ffff1111ffff1111",
            slug="invalid_slug",
            label=label,
            description=desc,
            category_id=PromptBlockCategory.MATRIX,
            type=BlockDataType.INSTRUCTION,  # type: ignore[arg-type]
            allow_decimals=True,
            output_extensions=[],
            scales=[scale],
        )
    assert "Input should be <BlockDataType.FLOAT: 'float'> or <BlockDataType.INT: 'int'>" in str(exc_info.value)


def test_step_validation_fails_on_empty_execution_logic() -> None:
    label = I18nText(translations={"fi": "Blueprintti", "en": "Blueprint"})

    # Successful: Has prompt blocks
    valid_blueprint = Step(
        id="step_11111111abababab",
        slug="task_bp_valid",
        name=label,
        role_block_id=None,
        extraction_protocol_block_id="blk_573802341db9d68c",
        criteria_block_ids=["some_block"],
        model_strategy="fast",
    )
    assert valid_blueprint.slug == "task_bp_valid"

    # Fails: Nothing defined
    with pytest.raises(ValidationError) as exc_info:
        Step(
            id="step_ffff1111ffff1111",
            slug="task_bp_err",
            name=label,
            role_block_id=None,
            extraction_protocol_block_id="blk_573802341db9d68c",
            criteria_block_ids=[],
            pre_hooks=["some_hook"],
            model_strategy="fast",
        )
    assert "must define at least one criteria_block_id." in str(exc_info.value)


def test_opaque_id_regex_validation() -> None:
    """Epic 10: Enforce Fail-Fast 422 on legacy slug usage in IDs."""
    label = I18nText(translations={"en": "Test", "fi": "Test"})

    # 1. Test PromptBlock creation rejection
    with pytest.raises(ValidationError) as exc_pb:
        SystemRulePromptBlock(
            id="legacy-slug-without-prefix",  # INVALID
            slug="valid_slug",
            label=label,
            description=label,
            category_id=PromptBlockCategory.SYSTEM_RULE,
            type=BlockDataType.STRING,
            output_extensions=[],
        )
    assert "String should match pattern '^([a-z]{2,5})_[a-fA-F0-9]{16,32}$'" in str(exc_pb.value)

    # 2. Test Step creation rejection
    with pytest.raises(ValidationError) as exc_step:
        Step(
            id="my_custom_slug123",  # INVALID, no prefix separated by underscore
            slug="slug",
            name=label,
            role_block_id=None,
            extraction_protocol_block_id="blk_573802341db9d68c",
            criteria_block_ids=["blk_test"],
            model_strategy="fast",
        )
    assert "String should match pattern '^([a-z]{2,5})_[a-fA-F0-9]{16,32}$'" in str(exc_step.value)
