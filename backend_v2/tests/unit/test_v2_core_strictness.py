import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import PromptBlock, TaskBlueprint, I18nText

def test_prompt_block_allow_decimals_requires_numeric():
    # Valid setup
    label = I18nText(default_locale="fi", translations={"fi": "Testi"})
    desc = I18nText(default_locale="fi", translations={"fi": "Kuvaus"})
    
    # Should validate since type='string' is allowed for BARS format backwards compatibility
    valid_block = PromptBlock(
        id="block_valid",
        label=label,
        description=desc,
        category_id="test_cat",
        type="string", # Valid
        allow_decimals=True,
        strictness_level=50,
        require_justification=False
    )
    assert valid_block.allow_decimals is True
    
    # Should raise error for allow_decimals=True with incompatible type
    with pytest.raises(Exception) as exc_info:
        PromptBlock(
            id="block_invalid",
            label=label,
            description=desc,
            category_id="test_cat",
            type="instruction", # Invalid for decimals
            allow_decimals=True,
            strictness_level=50,
            require_justification=False
        )
    assert "allow_decimals is only valid for numeric logic" in str(exc_info.value)


def test_task_blueprint_validation_fails_on_empty_execution_logic():
    label = I18nText(default_locale="fi", translations={"fi": "Blueprintti"})
    
    # Successful: Has prompt blocks
    valid_blueprint = TaskBlueprint(
        id="bp_id",
        slug="task_bp_valid",
        name=label,
        prompt_blocks=["some_block"]
    )
    assert valid_blueprint.slug == "task_bp_valid"
    
    # Successful: Has pre_hooks
    valid_blueprint_hooks = TaskBlueprint(
        id="bp_id_2",
        slug="task_bp_valid_hooks",
        name=label,
        pre_hooks=["some_hook"]
    )
    assert valid_blueprint_hooks.slug == "task_bp_valid_hooks"

    # Fails: Nothing defined
    with pytest.raises(Exception) as exc_info:
        TaskBlueprint(
            id="bp_id_err",
            slug="task_bp_err",
            name=label,
            prompt_blocks=[],
            pre_hooks=[]
        )
    assert "must define at least one prompt_block or pre_hook" in str(exc_info.value)
