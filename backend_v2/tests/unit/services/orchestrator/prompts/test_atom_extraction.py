from string.templatelib import Template

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.services.orchestrator.prompts.atom_extraction import (
    PHASE_0_SYSTEM_PROMPT,
    PHASE_1_SYSTEM_PROMPT,
    build_phase_1_system_prompt,
)


def test_prompts_exist() -> None:
    assert isinstance(PHASE_0_SYSTEM_PROMPT, str)
    assert isinstance(PHASE_1_SYSTEM_PROMPT, str)
    assert len(PHASE_0_SYSTEM_PROMPT) > 0
    assert len(PHASE_1_SYSTEM_PROMPT) > 0


def test_build_phase_1_system_prompt() -> None:
    """Verify build_phase_1_system_prompt returns Template rendered correctly with CDATA."""
    tmpl = build_phase_1_system_prompt(ontology_map_json='{"entities": ["User"]}')
    assert isinstance(tmpl, Template)
    rendered = TemplateProcessor.render_prompt(tmpl)
    assert "ROLE: ATOM EXTRACTION SPECIALIST" in rendered
    assert "<execution_parameters>" in rendered
    assert '<![CDATA[{"entities": ["User"]}]]>' in rendered
    assert "</execution_parameters>" in rendered
