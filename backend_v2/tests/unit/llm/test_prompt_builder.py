from unittest.mock import AsyncMock
from backend_v2.llm.prompt_builder import build_system_directive


def test_build_system_directive_empty() -> None:
    result = build_system_directive()
    assert result == ""


def test_build_system_directive_with_objective_and_rules() -> None:
    result = build_system_directive(objective="Test objective.", rules=["Rule 1", "Rule 2"])
    assert "## Objective" in result
    assert "Test objective." in result
    assert "## Rules" in result
    assert "- Rule 1" in result


def test_build_system_directive_with_kwargs() -> None:
    result = build_system_directive(
        objective="Test objective.", context="Test context.", definitions=["Def 1", "Def 2"]
    )
    assert "## Context" in result
    assert "Test context." in result
    assert "## Definitions" in result
    assert "- Def 1" in result
