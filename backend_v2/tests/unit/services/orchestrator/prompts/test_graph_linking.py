from string.templatelib import Template

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.services.orchestrator.prompts.graph_linking import (
    LINKER_SYSTEM_PROMPT,
    LINKER_USER_PROMPT,
    build_linker_user_prompt,
)


def test_prompts_exist() -> None:
    assert isinstance(LINKER_SYSTEM_PROMPT, str)
    assert isinstance(LINKER_USER_PROMPT, str)
    assert len(LINKER_SYSTEM_PROMPT) > 0
    assert len(LINKER_USER_PROMPT) > 0


def test_build_linker_user_prompt() -> None:
    """Verify build_linker_user_prompt returns Template rendered correctly with CDATA."""
    tmpl = build_linker_user_prompt(
        global_ontology_map='{"entity": "User"}',
        claims_window="[a0] Claim A\nQuote: Quote A",
    )
    assert isinstance(tmpl, Template)
    rendered = TemplateProcessor.render_prompt(tmpl)
    assert "<global_ontology_map>" in rendered
    assert "<![CDATA[{\"entity\": \"User\"}]]>" in rendered
    assert "<claims_window>" in rendered
    assert "<![CDATA[[a0] Claim A\nQuote: Quote A]]>" in rendered
    assert "Analyze the claims in the window" in rendered

