from backend_v2.models.prompts.hook_prompts import SYNTHESIS_SDUI_MANDATES


def test_sdui_prompt_alignment_with_schema() -> None:
    """Verify that the prompt instructions align with the actual Pydantic schema literals."""
    # 1. The prompt MUST NOT contain Python class names, because it confuses the LLM
    # into using them as block_type discriminators.
    assert "ParagraphBlock" not in SYNTHESIS_SDUI_MANDATES, "Prompt must not use literal class names!"
    assert "BulletListBlock" not in SYNTHESIS_SDUI_MANDATES, "Prompt must not use literal class names!"

    # 2. The prompt MUST contain the actual Pydantic literal discriminators
    assert "paragraph" in SYNTHESIS_SDUI_MANDATES, "Prompt must instruct the LLM to use the 'paragraph' discriminator"
    assert "bullet_list" in SYNTHESIS_SDUI_MANDATES, (
        "Prompt must instruct the LLM to use the 'bullet_list' discriminator"
    )
