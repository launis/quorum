from backend_v2.models.prompts.hook_prompts import (
    INTERACTION_OBJECTIVE,
    INTERACTION_RULES,
    SYNTHESIS_CITATION_RULES,
    SYNTHESIS_LENGTH_CONSTRAINT,
    SYNTHESIS_SDUI_MANDATES,
    SYNTHESIS_SECTION_RULES_PREFIX,
    SYNTHESIS_STATE_ISOLATION_MANDATE,
)


def test_hook_prompts_constants() -> None:
    """Test that all hook prompts are non-empty strings or lists of strings."""
    assert isinstance(SYNTHESIS_SDUI_MANDATES, list)
    assert len(SYNTHESIS_SDUI_MANDATES) > 0
    assert all(isinstance(rule, str) for rule in SYNTHESIS_SDUI_MANDATES)

    assert isinstance(SYNTHESIS_LENGTH_CONSTRAINT, str)
    assert "LENGTH CONSTRAINT" in SYNTHESIS_LENGTH_CONSTRAINT

    assert isinstance(SYNTHESIS_SECTION_RULES_PREFIX, str)
    assert "Section-Level Synthesis" in SYNTHESIS_SECTION_RULES_PREFIX

    assert isinstance(SYNTHESIS_CITATION_RULES, str)
    assert "CITATIONS" in SYNTHESIS_CITATION_RULES

    assert isinstance(SYNTHESIS_STATE_ISOLATION_MANDATE, str)
    assert "STATE ISOLATION MANDATE" in SYNTHESIS_STATE_ISOLATION_MANDATE

    assert isinstance(INTERACTION_OBJECTIVE, str)
    assert "Analyze the user" in INTERACTION_OBJECTIVE

    assert isinstance(INTERACTION_RULES, list)
    assert len(INTERACTION_RULES) > 0
    assert all(isinstance(rule, str) for rule in INTERACTION_RULES)
