"""Unit tests for deterministic technical debt scanner CLI (scripts/audit_technical_debt.py).

Verifies the 7-item technical debt sweep, static 1-hop caller discovery,
plan target extraction, markdown/JSON formatting, and CLI entrypoint.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError
import pytest

from scripts._script_base import GuardrailSeverity
from scripts.audit_technical_debt import (
    TechnicalDebtFindingDTO,
    TechnicalDebtScanResultDTO,
    find_one_hop_callers,
    format_technical_debt_markdown,
    main,
    scan_dart_technical_debt,
    scan_python_technical_debt,
    scan_targets_technical_debt,
)


def test_technical_debt_finding_dto_valid() -> None:
    """Verifies that TechnicalDebtFindingDTO instantiates properly with valid strict fields."""
    finding = TechnicalDebtFindingDTO(
        rule_code="QGR001",
        file_path="backend_v2/services/execution.py",
        lineno=42,
        col_offset=4,
        message="Banned reflection call getattr()",
        remediation="Use direct attribute access.",
        severity=GuardrailSeverity.WARNING,
        debt_category="python_ast_reflection",
    )
    assert finding.rule_code == "QGR001"
    assert finding.lineno == 42
    assert finding.severity == GuardrailSeverity.WARNING


def test_technical_debt_finding_dto_extra_fields_error() -> None:
    """ISTQB Negative: Verifies that extra fields trigger ValidationError under extra='forbid'."""
    with pytest.raises(ValidationError):
        TechnicalDebtFindingDTO.model_validate(
            {
                "rule_code": "QGR001",
                "file_path": "backend_v2/services/execution.py",
                "lineno": 42,
                "col_offset": 4,
                "message": "Banned reflection",
                "remediation": "Fix it",
                "severity": "WARNING",
                "debt_category": "python_ast_reflection",
                "extra_forbidden_key": "not_allowed",
            }
        )


def test_technical_debt_finding_dto_immutable_failure() -> None:
    """ISTQB Negative: Verifies that DTO instances are frozen and reject field assignment."""
    finding = TechnicalDebtFindingDTO(
        rule_code="QGR001",
        file_path="backend_v2/services/execution.py",
        lineno=42,
        col_offset=4,
        message="Banned reflection",
        remediation="Fix it",
        severity=GuardrailSeverity.WARNING,
        debt_category="python_ast_reflection",
    )
    with pytest.raises(ValidationError):
        finding.__setattr__("lineno", 100)


def test_scan_python_technical_debt_reflection_detected() -> None:
    """Verifies detection of getattr, hasattr, and setattr in domain Python code (Item 1)."""
    code = """
def process(obj):
    a = getattr(obj, "field")
    b = hasattr(obj, "other")
    setattr(obj, "val", 123)
    return a
"""
    findings = scan_python_technical_debt("backend_v2/services/sample.py", source_text=code)
    rule_codes = [f.rule_code for f in findings]
    assert rule_codes.count("QGR001") == 3
    assert all(f.debt_category == "python_ast_reflection" for f in findings)


def test_scan_python_technical_debt_dict_fallback_detected() -> None:
    """Verifies detection of banned .get() lookups on domain state (Item 2)."""
    code = """
def read_state(state):
    val = state.get("key")
    return val
"""
    findings = scan_python_technical_debt("backend_v2/services/sample.py", source_text=code)
    assert any(f.rule_code == "TD_DICT_GET" for f in findings)


def test_scan_python_technical_debt_dict_fallback_exemptions() -> None:
    """Verifies that os.environ.get and client.get are exempted from dict fallback check."""
    code = """
import os
def fetch(client):
    env_val = os.environ.get("MY_VAR")
    resp = client.get("https://example.com")
    return env_val, resp
"""
    findings = scan_python_technical_debt("backend_v2/services/sample.py", source_text=code)
    assert not any(f.rule_code == "TD_DICT_GET" for f in findings)


def test_scan_python_technical_debt_exception_swallowing_detected() -> None:
    """Verifies detection of except Exception: pass (Item 3)."""
    code = """
def risky_operation():
    try:
        do_something()
    except Exception:
        pass
"""
    findings = scan_python_technical_debt("backend_v2/services/sample.py", source_text=code)
    assert any(f.rule_code == "TD_EXCEPT_PASS" for f in findings)
    swallow_finding = next(f for f in findings if f.rule_code == "TD_EXCEPT_PASS")
    assert swallow_finding.severity == GuardrailSeverity.FATAL


def test_scan_python_technical_debt_mutable_defaults_in_functions() -> None:
    """Verifies detection of mutable default arguments in functions (Item 4)."""
    code = """
def append_item(x, items=[], mapping={}):
    items.append(x)
    return items
"""
    findings = scan_python_technical_debt("backend_v2/services/sample.py", source_text=code)
    mutable_findings = [f for f in findings if f.rule_code == "TD_MUTABLE_DEFAULT"]
    assert len(mutable_findings) == 2


def test_scan_python_technical_debt_mutable_defaults_in_classes() -> None:
    """Verifies detection of class-level mutable defaults and duplicate Field() (Item 4)."""
    code = """
from typing import Annotated
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    items: list[str] = []
    field_dup: Annotated[int, Field(ge=0)] = Field(default=0)
"""
    findings = scan_python_technical_debt("backend_v2/models/sample.py", source_text=code)
    qgr020_findings = [f for f in findings if f.rule_code == "QGR020"]
    assert len(qgr020_findings) >= 2


def test_scan_python_technical_debt_clean_python_code() -> None:
    """Verifies that clean, compliant Python code generates zero technical debt findings."""
    code = """
from __future__ import annotations
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

class CompliantDTO(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    count: Annotated[int, Field(ge=0)] = 0

def calculate_total(a: int, b: int) -> int:
    return a + b
"""
    findings = scan_python_technical_debt("backend_v2/services/clean.py", source_text=code)
    assert len(findings) == 0


def test_scan_python_technical_debt_syntax_error() -> None:
    """ISTQB Negative: Verifies that Python syntax errors are reported as fatal QGR000 findings."""
    code = "def broken_syntax( "
    findings = scan_python_technical_debt("backend_v2/services/broken.py", source_text=code)
    assert len(findings) == 1
    assert findings[0].rule_code == "QGR000"
    assert findings[0].severity == GuardrailSeverity.FATAL


def test_scan_python_technical_debt_istqb_negative_partitions() -> None:
    """Verifies detection of test files lacking negative test partitions (Item 6)."""
    code = """
def test_happy_path_only():
    assert True
"""
    findings = scan_python_technical_debt("backend_v2/tests/unit/test_sample.py", source_text=code)
    assert any(f.rule_code == "TD_ISTQB_NEGATIVE" for f in findings)


def test_scan_python_technical_debt_istqb_negative_partitions_satisfied() -> None:
    """Verifies that test files with negative test partitions pass the ISTQB check."""
    code = """
def test_happy_path():
    assert True

def test_missing_key_failure():
    assert True
"""
    findings = scan_python_technical_debt("backend_v2/tests/unit/test_sample.py", source_text=code)
    assert not any(f.rule_code == "TD_ISTQB_NEGATIVE" for f in findings)


def test_scan_python_technical_debt_model_factory_parity() -> None:
    """Verifies detection of raw dicts passed to model_validate in test files (Item 7)."""
    code = """
from backend_v2.models.domain.workflow import Workflow

def test_create_workflow():
    wf = Workflow.model_validate({"id": "wf_123", "name": "Test"})
    assert wf.id == "wf_123"
"""
    findings = scan_python_technical_debt("backend_v2/tests/unit/test_workflow.py", source_text=code)
    assert any(f.rule_code == "TD_MODEL_FACTORY" for f in findings)


def test_scan_dart_technical_debt_clean(tmp_path: Path) -> None:
    """Verifies clean Dart code produces zero technical debt findings."""
    dart_code = b"""
import 'package:flutter/material.dart';

class CompliantWidget extends StatelessWidget {
  const CompliantWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Container();
  }
}
"""
    dart_file = tmp_path / "compliant_widget.dart"
    dart_file.write_bytes(dart_code)
    findings = scan_dart_technical_debt(dart_file)
    assert len(findings) == 0


def test_scan_dart_technical_debt_violations(tmp_path: Path) -> None:
    """Verifies detection of Dart anti-patterns (hex colors, substring, etc.) (Item 5)."""
    dart_code = b"""
import 'package:flutter/material.dart';

class FeatureWidget extends StatelessWidget {
  const FeatureWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final clipped = "hello".substring(0, 2);
    return Container(
      color: Color(0xFF123456),
    );
  }
}
"""
    feature_dir = tmp_path / "lib" / "features" / "sample"
    feature_dir.mkdir(parents=True)
    dart_file = feature_dir / "feature_widget.dart"
    dart_file.write_bytes(dart_code)

    findings = scan_dart_technical_debt(dart_file)
    rule_codes = {f.rule_code for f in findings}
    assert "DGR007" in rule_codes
    assert "DGR008" in rule_codes


def test_find_one_hop_callers_synthetic(tmp_path: Path) -> None:
    """Verifies static 1-hop caller discovery via AST import parsing."""
    backend_dir = tmp_path / "backend_v2"
    services_dir = backend_dir / "services"
    services_dir.mkdir(parents=True)

    target_file = services_dir / "target_service.py"
    target_file.write_text("class TargetService:\n    pass\n", encoding="utf-8")

    caller_file = services_dir / "caller_service.py"
    caller_file.write_text(
        "from backend_v2.services.target_service import TargetService\n\ndef run():\n    return TargetService()\n",
        encoding="utf-8",
    )

    unrelated_file = services_dir / "other_service.py"
    unrelated_file.write_text("def other():\n    return 42\n", encoding="utf-8")

    callers = find_one_hop_callers([target_file], repo_root=tmp_path)
    assert "backend_v2/services/caller_service.py" in callers
    assert "backend_v2/services/other_service.py" not in callers


def test_scan_targets_technical_debt_full_flow(tmp_path: Path) -> None:
    """Verifies full sweep including targets and 1-hop callers with markdown formatting."""
    backend_dir = tmp_path / "backend_v2" / "services"
    backend_dir.mkdir(parents=True)

    clean_file = backend_dir / "clean_file.py"
    clean_file.write_text("def add(x: int, y: int) -> int:\n    return x + y\n", encoding="utf-8")

    result = scan_targets_technical_debt([clean_file], include_one_hop=False, strict=True, repo_root=tmp_path)
    assert result.passed is True
    assert len(result.findings) == 0

    markdown_report = format_technical_debt_markdown(result)
    assert "PASSED (Clean)" in markdown_report
    assert "No technical debt discovered" in markdown_report


def test_format_technical_debt_markdown_with_findings() -> None:
    """Verifies markdown table formatting when findings exist."""
    finding = TechnicalDebtFindingDTO(
        rule_code="QGR001",
        file_path="backend_v2/services/sample.py",
        lineno=10,
        col_offset=4,
        message="Banned reflection",
        remediation="Direct access",
        severity=GuardrailSeverity.WARNING,
        debt_category="python_ast_reflection",
    )
    result = TechnicalDebtScanResultDTO(
        targets=["backend_v2/services/sample.py"],
        one_hop_callers=[],
        findings=[finding],
        passed=False,
    )
    report = format_technical_debt_markdown(result)
    assert "| `backend_v2/services/sample.py` | 10 | `QGR001` | ⚠️ WARN |" in report
    assert "FAILED (Technical Debt Detected)" in report


def test_main_cli_missing_targets_error(capsys: pytest.CaptureFixture[str]) -> None:
    """ISTQB Negative: Verifies CLI returns exit code 1 when no targets or plan provided."""
    exit_code = main([])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: No target files specified" in captured.err


def test_main_cli_missing_plan_file_error(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """ISTQB Negative: Verifies CLI returns exit code 1 when specified plan file does not exist."""
    non_existent = tmp_path / "non_existent_plan.md"
    exit_code = main(["--plan", str(non_existent)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error: Plan file not found" in captured.err


def test_main_cli_plan_target_extraction(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies CLI extracts targets from implementation plan and scans them."""
    monkeypatch.chdir(tmp_path)
    # Create fake pyproject.toml so get_repo_root finds tmp_path
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n", encoding="utf-8")

    services_dir = tmp_path / "backend_v2" / "services"
    services_dir.mkdir(parents=True)
    target_py = services_dir / "target.py"
    target_py.write_text("def test_fn():\n    return 42\n", encoding="utf-8")

    plan_file = tmp_path / "implementation_plan.md"
    plan_file.write_text(
        f"# Plan\n- [MODIFY] @[backend_v2/services/target.py]\n- [NEW] @[backend_v2/services/new_target.py]\n",
        encoding="utf-8",
    )

    exit_code = main(["--plan", str(plan_file), "--strict"], repo_root=tmp_path)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "- **Targets Scanned:** 2" in captured.out
    assert "PASSED (Clean)" in captured.out


def test_main_cli_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies CLI emits valid JSON matching TechnicalDebtScanResultDTO when --json is passed."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n", encoding="utf-8")

    target_py = tmp_path / "clean.py"
    target_py.write_text("def hello() -> str:\n    return 'world'\n", encoding="utf-8")

    exit_code = main(["--targets", str(target_py), "--json"], repo_root=tmp_path)
    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    result_dto = TechnicalDebtScanResultDTO.model_validate(payload)
    assert result_dto.passed is True
    assert len(result_dto.findings) == 0


def test_scan_targets_directory(tmp_path: Path) -> None:
    """Verifies scanning a directory recursively processes python and dart files."""
    pkg_dir = tmp_path / "backend_v2" / "pkg"
    pkg_dir.mkdir(parents=True)
    py_file = pkg_dir / "service.py"
    py_file.write_text("def fn() -> int:\n    return 1\n", encoding="utf-8")

    dart_file = pkg_dir / "widget.dart"
    dart_file.write_bytes(b"class W {}\n")

    result = scan_targets_technical_debt([pkg_dir], repo_root=tmp_path)
    assert result.passed is True


def test_find_one_hop_callers_edge_cases(tmp_path: Path) -> None:
    """Verifies edge cases in find_one_hop_callers: missing backend dir, syntax errors, non-py targets."""
    # 1. No backend_v2 dir
    callers = find_one_hop_callers(["some/file.py"], repo_root=tmp_path)
    assert callers == []

    # 2. backend_v2 dir exists, but target is non-py
    backend_dir = tmp_path / "backend_v2"
    backend_dir.mkdir()
    callers = find_one_hop_callers(["some/file.dart"], repo_root=tmp_path)
    assert callers == []

    # 3. Candidate caller file has a syntax error
    bad_py = backend_dir / "bad.py"
    bad_py.write_text("def broken(", encoding="utf-8")
    callers = find_one_hop_callers(["backend_v2/target.py"], repo_root=tmp_path)
    assert callers == []


def test_scan_async_function_mutable_default() -> None:
    """Verifies mutable defaults in async functions are detected."""
    code = """
async def async_fn(items=[]):
    return items
"""
    findings = scan_python_technical_debt("backend_v2/services/async_sample.py", source_text=code)
    assert any(f.rule_code == "TD_MUTABLE_DEFAULT" for f in findings)


def test_scan_file_missing_returns_empty(tmp_path: Path) -> None:
    """Verifies that non-existent files return empty findings without crashing."""
    findings_py = scan_python_technical_debt(tmp_path / "non_existent.py")
    assert findings_py == []
    findings_dart = scan_dart_technical_debt(tmp_path / "non_existent.dart")
    assert findings_dart == []


def test_main_cli_relative_plan_path(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies CLI handles relative plan paths correctly."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n", encoding="utf-8")

    plan_file = tmp_path / "plan.md"
    target_file = tmp_path / "target.py"
    target_file.write_text("def foo():\n    pass\n", encoding="utf-8")
    plan_file.write_text("- [MODIFY] @[target.py]\n", encoding="utf-8")

    exit_code = main(["--plan", "plan.md"], repo_root=tmp_path)
    assert exit_code == 0

