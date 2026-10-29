"""Unit tests for backend_v2/llm/prompt_builder.py."""

from typing import cast

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.prompt_builder import build_system_directive


def test_build_system_directive_empty() -> None:
    """Positive: verify empty call returns an empty string."""
    result = build_system_directive()
    assert result == ""


def test_build_system_directive_with_objective_and_rules() -> None:
    """Positive: verify objective and rules sections are formatted as Markdown headings and bullets."""
    result = build_system_directive(objective="Test objective.", rules=["Rule 1", "Rule 2"])
    assert "## Objective" in result
    assert "Test objective." in result
    assert "## Rules" in result
    assert "- Rule 1" in result
    assert "- Rule 2" in result


def test_build_system_directive_with_kwargs() -> None:
    """Positive: verify dynamic keyword arguments format as titled Markdown sections and bullet lists."""
    result = build_system_directive(
        objective="Test objective.",
        context="Test context.",
        definitions=["Def 1", "Def 2"],
        unused_block=None,
    )
    assert "## Context" in result
    assert "Test context." in result
    assert "## Definitions" in result
    assert "- Def 1" in result
    assert "## Unused Block" not in result


def test_build_system_directive_boundary_whitespace_only() -> None:
    """Boundary (ISTQB BVA): verify whitespace-only inputs produce empty output without blank headings."""
    result = build_system_directive(
        objective="   ",
        rules=["   ", ""],
        context="   ",
        definitions=["   "],
    )
    assert result == ""


def test_build_system_directive_negative_invalid_objective_and_rules_types() -> None:
    """Negative (ISTQB Partition): verify non-string objective or invalid rules types raise AppException."""
    with pytest.raises(AppException) as exc_obj:
        build_system_directive(objective=cast(str, 123))
    assert exc_obj.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_rules_type:
        build_system_directive(rules=cast(list[str], "not a list"))
    assert exc_rules_type.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_rules_item:
        build_system_directive(rules=cast(list[str], ["Valid rule", 999]))
    assert exc_rules_item.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_build_system_directive_negative_invalid_kwargs_types() -> None:
    """Negative (ISTQB Partition): verify invalid keyword block types raise AppException."""
    with pytest.raises(AppException) as exc_kw_scalar:
        build_system_directive(context=cast(str, 42))
    assert exc_kw_scalar.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_kw_list:
        build_system_directive(definitions=cast(list[str], ["Valid", 42]))
    assert exc_kw_list.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_build_system_directive_negative_raw_xml_directive_tags() -> None:
    """Negative (ISTQB Partition): verify raw De-Generator XML wrapper tags raise AppException."""
    with pytest.raises(AppException) as exc_xml_obj:
        build_system_directive(objective="<system_directive>Do task</system_directive>")
    assert exc_xml_obj.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_xml_rule:
        build_system_directive(rules=["<objective>Rule</objective>"])
    assert exc_xml_rule.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_xml_kw:
        build_system_directive(context="<role>Expert</role>")
    assert exc_xml_kw.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_xml_kw_list:
        build_system_directive(definitions=["<system_directive>Nested</system_directive>"])
    assert exc_xml_kw_list.value.error_code == ErrorCodes.VALIDATION_FAILED.value
