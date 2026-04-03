import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.enums import BlockDataType
from backend_v2.models.v2_core import I18nText, PromptBlock, Step


def test_prompt_block_allow_decimals_requires_numeric() -> None:
    # Valid setup
    label = I18nText(default_locale="fi", translations={"fi": "Testi", "en": "Test"})
    desc = I18nText(default_locale="fi", translations={"fi": "Kuvaus", "en": "Desc"})

    # Should validate since type='string' is allowed for BARS format backwards compatibility
    valid_block = PromptBlock(
        id="blk_eeee5555eeee5555",
        slug="valid_slug",
        label=label,
        description=desc,
        category_id="test_cat",
        type=BlockDataType.STRING,  # Valid
        allow_decimals=True,
        output_extensions=[],
    )
    assert valid_block.allow_decimals is True

    # Should raise error for allow_decimals=True with incompatible type
    with pytest.raises(AppException) as exc_info:
        PromptBlock(
            id="blk_invalidblock",
            slug="invalid_slug",
            label=label,
            description=desc,
            category_id="test_cat",
            type=BlockDataType.INSTRUCTION,  # Invalid for decimals
            allow_decimals=True,
            output_extensions=[],
        )
    assert "allow_decimals is only valid for numeric logic" in str(exc_info.value)


def test_step_validation_fails_on_empty_execution_logic() -> None:
    label = I18nText(default_locale="fi", translations={"fi": "Blueprintti", "en": "Blueprint"})

    # Successful: Has prompt blocks
    valid_blueprint = Step(
        id="step_1111111111111111bbbbbbbb", slug="task_bp_valid", name=label, prompt_blocks=["some_block"], model_strategy="fast"
    )
    assert valid_blueprint.slug == "task_bp_valid"

    # Fails: Nothing defined
    with pytest.raises(AppException) as exc_info:
        Step(
            id="step_bpiderror",
            slug="task_bp_err",
            name=label,
            prompt_blocks=[],
            pre_hooks=["some_hook"],
            model_strategy="fast",
        )
    assert "must define at least one prompt_block." in str(exc_info.value)


def test_opaque_id_regex_validation() -> None:
    """Epic 10: Enforce Fail-Fast 422 on legacy slug usage in IDs."""
    label = I18nText(default_locale="en", translations={"en": "Test"})

    # 1. Test PromptBlock creation rejection
    with pytest.raises(ValidationError) as exc_pb:
        PromptBlock(
            id="org_1234567890123456",  # INVALID
            slug="valid_slug",
            label=label,
            description=label,
            category_id="test_cat",
            type=BlockDataType.STRING,
            output_extensions=[],
        )
    assert "String should match pattern '^([a-z]{2,5})_[a-zA-Z0-9]{8,}$'" in str(exc_pb.value)

    # 2. Test Step creation rejection
    with pytest.raises(ValidationError) as exc_step:
        Step(
            id="my_custom_slug123",  # INVALID, no prefix separated by underscore
            slug="slug",
            name=label,
            prompt_blocks=["blk_test"],
            model_strategy="fast",
        )
    assert "String should match pattern '^([a-z]{2,5})_[a-zA-Z0-9]{8,}$'" in str(exc_step.value)
