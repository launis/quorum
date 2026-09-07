"""Unit tests for dynamic performative linguistics prompt assets."""

from backend_v2.models.prompts.execution.dynamic_linguistics import (
    DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT,
    DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE,
)


def test_dynamic_performative_system_prompt() -> None:
    """Verify system prompt structure, XML boundaries, and extraction directives."""
    assert isinstance(DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT, str)
    assert "<role>" in DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT
    assert "</role>" in DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT
    assert "<objective>" in DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT
    assert "</objective>" in DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT
    assert "<extraction_protocol>" in DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT
    assert "</extraction_protocol>" in DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT
    assert "VERBATIM REQUIREMENT" in DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT


def test_dynamic_performative_user_prompt_template() -> None:
    """Verify user template contains necessary XML fencing and interpolation key."""
    assert isinstance(DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE, str)
    assert "<source_data>" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "</source_data>" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "<user_payload>" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "</user_payload>" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "{text_to_scan}" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE

    # Test formatting with sample text
    formatted = DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE.format(text_to_scan="sample content")
    assert "sample content" in formatted
