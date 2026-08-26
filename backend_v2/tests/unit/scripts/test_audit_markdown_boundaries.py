"""Unit tests for the markdown boundaries structural audit script (scripts/audit_markdown_boundaries.py).

Tests all verification gates: ambiguity detection, XML tag truncation, file references,
AST line bounds, class hallucinations, settings validation, enum validation, CLI execution, and zero reflection.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.audit_markdown_boundaries import (
    GuardrailSeverity,
    MarkdownAuditFinding,
    MarkdownAuditor,
    main,
    print_error,
    print_success,
)


def test_markdown_auditor_dto_structure() -> None:
    """Test MarkdownAuditFinding Pydantic V2 DTO creation and strictness."""
    finding = MarkdownAuditFinding(
        line_number=10,
        rule_code="MBD001",
        category="Ambiguity",
        message="Ambiguous language detected 'e.g.'.",
        severity=GuardrailSeverity.WARNING,
        remediation="Replace with concrete list.",
    )
    assert finding.line_number == 10
    assert finding.rule_code == "MBD001"
    assert finding.severity == GuardrailSeverity.WARNING
    assert finding.remediation == "Replace with concrete list."


def test_print_helpers(capsys: pytest.CaptureFixture[str]) -> None:
    """Test print_error and print_success ANSI output."""
    print_error("Failed check")
    out_err = capsys.readouterr().out
    assert "ERROR: Failed check" in out_err

    print_success("Passed check")
    out_succ = capsys.readouterr().out
    assert "SUCCESS: Passed check" in out_succ


def test_markdown_auditor_ambiguity_detection(tmp_path: Path) -> None:
    """Test detection of ambiguous language (e.g., etc., such as, like)."""
    md_file = tmp_path / "ambiguous.md"
    md_file.write_text(
        "Line 1: For example, use e.g. foo.\n"
        "Line 2: Other items such as bar.\n"
        "Line 3: Clean line.\n"
        "Line 4: Things like this, etc.\n",
        encoding="utf-8",
    )

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_ambiguity()

    assert len(auditor.findings) == 3
    assert all(f.rule_code == "MBD001" for f in auditor.findings)
    assert all(f.severity == GuardrailSeverity.WARNING for f in auditor.findings)
    assert auditor.findings[0].line_number == 1
    assert auditor.findings[1].line_number == 2
    assert auditor.findings[2].line_number == 4


def test_markdown_auditor_ambiguity_clean(tmp_path: Path) -> None:
    """Test that unambiguous markdown produces zero ambiguity findings."""
    md_file = tmp_path / "clean.md"
    md_file.write_text(
        "Line 1: Specifically and exhaustively: A, B, C.\nLine 2: Programmatic SSOT reference to AnySduiBlock.\n",
        encoding="utf-8",
    )

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_ambiguity()
    assert len(auditor.findings) == 0
    assert len(auditor.errors) == 0


def test_markdown_auditor_xml_unclosed_tags(tmp_path: Path) -> None:
    """Test unclosed XML tags detection."""
    md_file = tmp_path / "unclosed.md"
    md_file.write_text('<execution_protocol>\n<step id="1">\n', encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_xml_truncation()

    assert len(auditor.findings) == 2
    assert all(f.rule_code == "MBD002" for f in auditor.findings)
    assert all(f.severity == GuardrailSeverity.FATAL for f in auditor.findings)


def test_markdown_auditor_xml_mismatched_and_orphan_closing(tmp_path: Path) -> None:
    """Test mismatched closing tag and closing tag without opening tag."""
    md_file = tmp_path / "mismatched.md"
    md_file.write_text(
        "<execution_protocol>\n</step>\n</execution_protocol>\n",
        encoding="utf-8",
    )

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_xml_truncation()

    assert len(auditor.findings) >= 1
    assert any("Mismatched closing tag" in f.message for f in auditor.findings)


def test_markdown_auditor_xml_orphan_closing_tag(tmp_path: Path) -> None:
    """Test closing tag without any opening tag."""
    md_file = tmp_path / "orphan_close.md"
    md_file.write_text("</step>\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_xml_truncation()

    assert len(auditor.findings) == 1
    assert "Closing tag </step> without opening tag." in auditor.findings[0].message


def test_markdown_auditor_xml_valid(tmp_path: Path) -> None:
    """Test valid properly nested XML tags produce zero findings."""
    md_file = tmp_path / "valid.md"
    md_file.write_text(
        '<execution_protocol>\n  <step id="1">\n  </step>\n</execution_protocol>\n',
        encoding="utf-8",
    )

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_xml_truncation()
    assert len(auditor.findings) == 0


def test_markdown_auditor_missing_file_reference(tmp_path: Path) -> None:
    """Test that missing referenced file emits MBD003 finding."""
    md_file = tmp_path / "test.md"
    md_file.write_text("See @[backend_v2/nonexistent.py#L1-L10]", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_file_references_and_ast_bounds()

    assert len(auditor.findings) == 1
    assert auditor.findings[0].rule_code == "MBD003"
    assert auditor.findings[0].severity == GuardrailSeverity.FATAL
    assert "Referenced file does not exist" in auditor.findings[0].message
    assert "Line 1: Referenced file does not exist" in auditor.errors[0]


def test_markdown_auditor_ignored_file_references(tmp_path: Path) -> None:
    """Test that [NEW], [DELETE], and ki_*.md references are ignored for file existence."""
    md_file = tmp_path / "test.md"
    md_file.write_text(
        "#### [NEW] @[backend_v2/new_file.py]\n"
        "#### [DELETE] @[backend_v2/old_file.py]\n"
        "<knowledge_item>@[ki_some_concept.md]</knowledge_item>\n",
        encoding="utf-8",
    )

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_file_references_and_ast_bounds()
    assert len(auditor.findings) == 0


def test_markdown_auditor_ast_bounds_valid_function(tmp_path: Path) -> None:
    """Test matching AST line bounds on Python function definition."""
    py_file = tmp_path / "module.py"
    py_file.write_text(
        "# Header\ndef compute_something(x: int) -> int:\n    y = x * 2\n    return y\n",
        encoding="utf-8",
    )

    md_file = tmp_path / "doc.md"
    md_file.write_text("Target: @[module.py#L2-L4]\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_file_references_and_ast_bounds()
    assert len(auditor.findings) == 0


def test_markdown_auditor_ast_bounds_valid_decorated_function(tmp_path: Path) -> None:
    """Test matching AST line bounds on decorated function."""
    py_file = tmp_path / "module.py"
    py_file.write_text(
        "@override\ndef execute(self) -> None:\n    pass\n",
        encoding="utf-8",
    )

    md_file = tmp_path / "doc.md"
    md_file.write_text("Target: @[module.py#L1-L3]\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_file_references_and_ast_bounds()
    assert len(auditor.findings) == 0


def test_markdown_auditor_ast_bounds_mismatch(tmp_path: Path) -> None:
    """Test mismatched AST line bounds emits MBD004."""
    py_file = tmp_path / "module.py"
    py_file.write_text(
        "def compute(x: int) -> int:\n    return x\n",
        encoding="utf-8",
    )

    md_file = tmp_path / "doc.md"
    md_file.write_text("Target: @[module.py#L1-L10]\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_file_references_and_ast_bounds()

    assert len(auditor.findings) == 1
    assert auditor.findings[0].rule_code == "MBD004"
    assert auditor.findings[0].severity == GuardrailSeverity.FATAL
    assert "AST Bound mismatch" in auditor.findings[0].message


def test_markdown_auditor_ast_syntax_error_resilience(tmp_path: Path) -> None:
    """Test that referenced Python file with syntax error emits MBD004 without crashing."""
    py_file = tmp_path / "broken.py"
    py_file.write_text("def broken_func(\n", encoding="utf-8")

    md_file = tmp_path / "doc.md"
    md_file.write_text("Target: @[broken.py#L1-L2]\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_file_references_and_ast_bounds()

    assert len(auditor.findings) == 1
    assert auditor.findings[0].rule_code == "MBD004"
    assert "SyntaxError parsing" in auditor.findings[0].message


def test_markdown_auditor_ast_read_error_resilience(tmp_path: Path) -> None:
    """Test that unreadable file during AST bound check emits MBD004."""
    py_file = tmp_path / "unreadable.py"
    py_file.write_text("class Test:\n    pass\n", encoding="utf-8")

    md_file = tmp_path / "doc.md"
    md_file.write_text("Target: @[unreadable.py#L1-L2]\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    with patch.object(Path, "read_text", side_effect=OSError("Permission denied")):
        auditor.check_file_references_and_ast_bounds()

    assert len(auditor.findings) == 1
    assert auditor.findings[0].rule_code == "MBD004"
    assert "Error reading" in auditor.findings[0].message


def test_markdown_auditor_class_hallucinations(tmp_path: Path) -> None:
    """Test detection of class hallucinations when DTO/Service is not in backend_v2."""
    backend_dir = tmp_path / "backend_v2" / "models"
    backend_dir.mkdir(parents=True)
    (backend_dir / "user.py").write_text("class UserDTO:\n    pass\n", encoding="utf-8")

    md_file = tmp_path / "plan.md"
    md_file.write_text(
        "Uses `UserDTO` and hallucinated `NonExistentService` and `FakeResponse`.\n",
        encoding="utf-8",
    )

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_class_hallucinations()

    hallucination_findings = [f for f in auditor.findings if f.rule_code == "MBD005"]
    assert len(hallucination_findings) == 2
    messages = [f.message for f in hallucination_findings]
    assert any("FakeResponse" in m for m in messages)
    assert any("NonExistentService" in m for m in messages)
    assert not any("UserDTO" in m for m in messages)


def test_markdown_auditor_class_hallucinations_no_mentioned_or_missing_backend(tmp_path: Path) -> None:
    """Test class hallucination check with no mentioned classes or non-existent backend directory."""
    md_file = tmp_path / "empty_classes.md"
    md_file.write_text("No special classes here.\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_class_hallucinations()
    assert len(auditor.findings) == 0

    # With mentioned class but no backend_v2 folder
    md_file2 = tmp_path / "has_class.md"
    md_file2.write_text("Mentions `MissingDTO`.\n", encoding="utf-8")
    auditor2 = MarkdownAuditor(str(md_file2), str(tmp_path))
    auditor2.check_class_hallucinations()
    assert len(auditor2.findings) == 1


def test_markdown_auditor_class_hallucinations_syntax_error_file(tmp_path: Path) -> None:
    """Test class hallucination scanner handles broken Python files gracefully."""
    backend_dir = tmp_path / "backend_v2"
    backend_dir.mkdir(parents=True)
    (backend_dir / "broken.py").write_text("class Incomplete(\n", encoding="utf-8")

    md_file = tmp_path / "plan.md"
    md_file.write_text("Mentions `UserDTO`.\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_class_hallucinations()

    parse_errors = [f for f in auditor.findings if "Failed to parse" in f.message]
    assert len(parse_errors) == 1


def test_markdown_auditor_settings_validation(tmp_path: Path) -> None:
    """Test validation of settings references against backend_v2/settings.py."""
    backend_dir = tmp_path / "backend_v2"
    backend_dir.mkdir(parents=True)
    (backend_dir / "settings.py").write_text(
        "class Settings:\n"
        "    app_env: str = 'development'\n"
        "    max_concurrent_llm_steps: int = 5\n"
        "    legacy_timeout = 10\n",
        encoding="utf-8",
    )

    md_file = tmp_path / "plan.md"
    md_file.write_text(
        "Check settings.app_env, settings.legacy_timeout, and settings.unreal_timeout_threshold.\n",
        encoding="utf-8",
    )

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_settings_validation()

    settings_findings = [f for f in auditor.findings if f.rule_code == "MBD006"]
    assert len(settings_findings) == 1
    assert "settings.unreal_timeout_threshold" in settings_findings[0].message
    assert "settings.app_env" not in settings_findings[0].message
    assert "settings.legacy_timeout" not in settings_findings[0].message


def test_markdown_auditor_settings_validation_no_mentioned_or_missing_file(tmp_path: Path) -> None:
    """Test settings validation when no settings are mentioned or settings.py is missing."""
    md_file = tmp_path / "no_settings.md"
    md_file.write_text("settings.py is mentioned as file name.\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_settings_validation()
    assert len(auditor.findings) == 0

    # With setting mentioned but missing settings.py
    md_file2 = tmp_path / "has_setting.md"
    md_file2.write_text("Uses settings.custom_var.\n", encoding="utf-8")
    auditor2 = MarkdownAuditor(str(md_file2), str(tmp_path))
    auditor2.check_settings_validation()
    assert len(auditor2.findings) == 1


def test_markdown_auditor_settings_validation_syntax_error(tmp_path: Path) -> None:
    """Test settings validation handles syntax error in settings.py."""
    backend_dir = tmp_path / "backend_v2"
    backend_dir.mkdir(parents=True)
    (backend_dir / "settings.py").write_text("class Settings(\n", encoding="utf-8")

    md_file = tmp_path / "plan.md"
    md_file.write_text("Uses settings.app_env.\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_settings_validation()
    assert any("Failed to parse" in f.message for f in auditor.findings)


def test_markdown_auditor_enum_validation(tmp_path: Path) -> None:
    """Test validation of Enum references against backend enums and Flutter enums."""
    backend_models = tmp_path / "backend_v2" / "models"
    backend_models.mkdir(parents=True)
    (backend_models / "enums.py").write_text("class ExecutionStatus:\n    PASSED = 'PASSED'\n", encoding="utf-8")

    flutter_models = tmp_path / "client_app_v2" / "lib" / "core" / "models"
    flutter_models.mkdir(parents=True)
    (flutter_models / "enums.dart").write_text("enum FlutterRole { admin, user }\n", encoding="utf-8")

    md_file = tmp_path / "plan.md"
    md_file.write_text(
        "Referencing `ExecutionStatus.PASSED`, `FlutterRole.admin`, and `FakeEnum.INVALID`.\n",
        encoding="utf-8",
    )

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_enum_validation()

    enum_findings = [f for f in auditor.findings if f.rule_code == "MBD007"]
    assert len(enum_findings) == 1
    assert "FakeEnum" in enum_findings[0].message


def test_markdown_auditor_enum_validation_error_handling(tmp_path: Path) -> None:
    """Test enum validation error handling when python/dart files have syntax or read errors."""
    backend_models = tmp_path / "backend_v2" / "models"
    backend_models.mkdir(parents=True)
    (backend_models / "enums.py").write_text("class Broken(\n", encoding="utf-8")

    flutter_models = tmp_path / "client_app_v2" / "lib" / "core" / "models"
    flutter_models.mkdir(parents=True)
    (flutter_models / "enums.dart").write_text("invalid dart", encoding="utf-8")

    md_file = tmp_path / "plan.md"
    md_file.write_text("Referencing `ExecutionStatus.PASSED`.\n", encoding="utf-8")

    auditor = MarkdownAuditor(str(md_file), str(tmp_path))
    auditor.check_enum_validation()
    assert any("Failed to parse" in f.message for f in auditor.findings)


def test_markdown_auditor_run_all_checks_exit_codes(tmp_path: Path) -> None:
    """Test run_all_checks with exit_on_completion True and False."""
    clean_md = tmp_path / "clean.md"
    clean_md.write_text("# Title\nValid content.\n", encoding="utf-8")

    auditor_clean = MarkdownAuditor(str(clean_md), str(tmp_path))
    findings = auditor_clean.run_all_checks(exit_on_completion=False)
    assert findings == []

    with pytest.raises(SystemExit) as exc_info:
        auditor_clean.run_all_checks(exit_on_completion=True)
    assert exc_info.value.code == 0

    dirty_md = tmp_path / "dirty.md"
    dirty_md.write_text("Uses e.g. ambiguous language.\n", encoding="utf-8")
    auditor_dirty = MarkdownAuditor(str(dirty_md), str(tmp_path))
    with pytest.raises(SystemExit) as exc_info2:
        auditor_dirty.run_all_checks(exit_on_completion=True)
    assert exc_info2.value.code == 1


def test_markdown_auditor_main_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main() CLI entrypoint execution."""
    clean_md = tmp_path / "clean.md"
    clean_md.write_text("# Clean\nContent.\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["audit_markdown_boundaries.py", "--file", str(clean_md)])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0

    # Non-existent file
    monkeypatch.setattr(sys, "argv", ["audit_markdown_boundaries.py", "--file", str(tmp_path / "missing.md")])
    with pytest.raises(SystemExit) as exc_info2:
        main()
    assert exc_info2.value.code == 1


def test_markdown_auditor_zero_reflection_compliance() -> None:
    """Verify scripts/audit_markdown_boundaries.py contains zero getattr/hasattr calls."""
    script_path = Path("scripts/audit_markdown_boundaries.py").resolve()
    tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=script_path.as_posix())

    reflection_calls: list[int] = []
    for node in ast.walk(tree):
        match node:
            case ast.Call(func=ast.Name(id="getattr" | "hasattr")):
                reflection_calls.append(node.lineno)
            case _:
                pass

    assert reflection_calls == [], f"Found banned reflection calls at lines: {reflection_calls}"
