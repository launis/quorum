from backend_v2.models.prompts.hook_prompts import (
    INTERACTION_OBJECTIVE,
    INTERACTION_RULES,
)


def test_hook_prompts_constants() -> None:
    """Test that all hook prompts are non-empty strings or lists of strings."""
    assert isinstance(INTERACTION_OBJECTIVE, str)
    assert "Analyze the user" in INTERACTION_OBJECTIVE

    assert isinstance(INTERACTION_RULES, list)
    assert len(INTERACTION_RULES) > 0
    assert all(isinstance(rule, str) for rule in INTERACTION_RULES)
