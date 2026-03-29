from typing import Any
import pytest

from backend_v2.models.enums import BlockDataType
from backend_v2.models.v2_core import I18nText, PromptBlock, Step


def test_prompt_block_allow_decimals_requires_numeric() -> None:
    # Valid setup
    label = I18nText(default_locale="fi", translations={"fi": "Testi", "en": "Test"})
    desc = I18nText(default_locale="fi", translations={"fi": "Kuvaus", "en": "Desc"})

    # Should validate since type='string' is allowed for BARS format backwards compatibility
    valid_block = PromptBlock(
        id="blk_validblock",
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
    with pytest.raises(Exception) as exc_info:
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
    valid_blueprint = Step(id="step_blueprint", slug="task_bp_valid", name=label, prompt_blocks=["some_block"], model_strategy="fast")
    assert valid_blueprint.slug == "task_bp_valid"

    # Fails: Nothing defined
    with pytest.raises(Exception) as exc_info:
        Step(id="step_bpiderror", slug="task_bp_err", name=label, prompt_blocks=[], pre_hooks=["some_hook"], model_strategy="fast")
    assert "must define at least one prompt_block." in str(exc_info.value)
