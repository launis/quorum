"""Unit tests for dynamic performative linguistics prompt assets."""

from string.templatelib import Template

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.models.prompts.execution.dynamic_linguistics import (
    DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT,
    DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE,
    build_dynamic_performative_user_prompt,
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
    assert "When analyzing inflected languages (specifically Finnish)" in DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT


def test_dynamic_performative_user_prompt_template() -> None:
    """Verify user template contains necessary XML fencing and interpolation keys."""
    assert isinstance(DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE, str)
    assert "<source_data>" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "</source_data>" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "<target_language>{language}</target_language>" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "<user_payload>" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "</user_payload>" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "{text_to_scan}" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE
    assert "{language}" in DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE


def test_build_dynamic_performative_user_prompt() -> None:
    """Verify build_dynamic_performative_user_prompt returns Template rendered via TemplateProcessor."""
    tmpl = build_dynamic_performative_user_prompt(language="fi", text_to_scan="sample content <test>")
    assert isinstance(tmpl, Template)
    rendered = TemplateProcessor.render_prompt(tmpl)
    assert "<source_data>" in rendered
    assert "<target_language>fi</target_language>" in rendered
    assert "<user_payload>" in rendered
    assert "<![CDATA[sample content <test>]]>" in rendered
    assert "</user_payload>" in rendered
    assert "</source_data>" in rendered
