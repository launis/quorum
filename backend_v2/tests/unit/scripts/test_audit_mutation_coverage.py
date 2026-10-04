"""Unit tests for pure AST mutation coverage engine (scripts/audit_mutation_coverage.py).

Tests mutation site discovery, AST operator transformations, dry-run mode,
surviving mutant detection, and full mathematical invariance across targets.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.audit_mutation_coverage import (
    DEFAULT_TARGETS,
    MutationResult,
    MutationSpec,
    TargetAuditReport,
    TargetConfig,
    apply_mutation,
    audit_target_mutations,
    collect_mutation_sites,
    main,
    run_mutation_audit,
)


def test_collect_mutation_sites_discovers_operators_in_function_body() -> None:
    """Verifies that relational, arithmetic, and augmented assign operators are discovered."""
    code = """
def calculate(a: int, b: int) -> int:
    x = a + b
    y = x * 2
    if y > 10:
        y += 5
    return y
"""
    sites = collect_mutation_sites(code)
    assert len(sites) >= 4

    types = {s.target_type for s in sites}
    assert "BinOp" in types
    assert "Compare" in types
    assert "AugAssign" in types

    # Verify operations
    op_pairs = {(s.original_op, s.mutated_op) for s in sites}
    assert ("Add", "Sub") in op_pairs
    assert ("Mult", "Div") in op_pairs
    assert ("Gt", "LtE") in op_pairs


def test_collect_mutation_sites_ignores_type_annotations() -> None:
    """Verifies that operators in type annotations (e.g. BitOr in X | None) are not collected."""
    code = """
def evaluate_node(node: Node | None) -> Result | None:
    value: int | float = 10 + 5
    return None
"""
    sites = collect_mutation_sites(code)
    # Only 10 + 5 should be collected, NOT the BitOr in Node | None or int | float
    assert len(sites) == 1
    assert sites[0].target_type == "BinOp"
    assert sites[0].original_op == "Add"


def test_apply_mutation_transforms_compare_operator() -> None:
    """Verifies that apply_mutation properly replaces comparison operators."""
    code = "def check(x: int) -> bool:\n    return x > 10\n"
    sites = collect_mutation_sites(code)
    assert len(sites) == 1

    mutated_code = apply_mutation(code, sites[0])
    assert "x <= 10" in mutated_code or "x < 10" in mutated_code
    # Must remain syntactically valid Python
    ast.parse(mutated_code)


def test_apply_mutation_transforms_binop_operator() -> None:
    """Verifies that apply_mutation properly replaces arithmetic operators."""
    code = "def calc(x: int) -> int:\n    return x * 2\n"
    sites = collect_mutation_sites(code)
    assert len(sites) == 1

    mutated_code = apply_mutation(code, sites[0])
    assert "x / 2" in mutated_code
    ast.parse(mutated_code)


def test_apply_mutation_raises_value_error_for_mismatched_spec() -> None:
    """Verifies that apply_mutation raises ValueError when the target site cannot be found."""
    code = "def simple() -> int:\n    return 42\n"
    fake_spec = MutationSpec(
        target_type="BinOp",
        filepath="fake.py",
        lineno=999,
        col_offset=0,
        op_index=0,
        original_op="Add",
        mutated_op="Sub",
        description="Non-existent site",
    )
    with pytest.raises(ValueError, match="Mutation target not found"):
        apply_mutation(code, fake_spec)


def test_audit_target_mutations_dry_run() -> None:
    """Verifies that dry-run enumerates mutants without running subprocesses."""
    target = DEFAULT_TARGETS[0]
    report = audit_target_mutations(target, dry_run=True, max_mutants=3)

    assert isinstance(report, TargetAuditReport)
    assert report.total_mutants == 3
    assert report.killed_mutants == 3
    assert report.survived_mutants == 0
    assert report.kill_rate == 100.0
    assert len(report.results) == 3


def test_mutation_engine_detects_surviving_mutant() -> None:
    """Contract: Verifies that mutation engine detects surviving mutants when tests do not assert."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        dummy_src = tmp_path / "dummy_math.py"
        dummy_test = tmp_path / "test_dummy_math.py"

        # Source code has two operations
        dummy_src.write_text(
            "def add_and_double(a: int, b: int) -> int:\n    sum_val = a + b\n    return sum_val * 2\n",
            encoding="utf-8",
        )
        # Test only tests that result is positive (loose assert), so mutating * 2 to / 2 still produces > 0!
        dummy_test.write_text(
            "from dummy_math import add_and_double\ndef test_add_and_double() -> None:\n    res = add_and_double(10, 10)\n    assert res > 0\n",
            encoding="utf-8",
        )

        target = TargetConfig(
            name="dummy",
            target_file=str(dummy_src),
            test_file=str(dummy_test),
        )

        report = audit_target_mutations(target, timeout=10.0)
        # At least one mutant must survive the loose assertion (res > 0)
        assert report.survived_mutants > 0
        assert report.kill_rate < 100.0


def test_mutation_coverage_report_strictness_failure() -> None:
    """Contract: Verifies that run_mutation_audit sets success=False when kill rate < 100% in strict mode."""
    mock_report = TargetAuditReport(
        target_name="mock_target",
        target_file="mock.py",
        test_file="test_mock.py",
        total_mutants=10,
        killed_mutants=8,
        survived_mutants=2,
        kill_rate=80.0,
        results=[],
    )

    with patch("scripts.audit_mutation_coverage.audit_target_mutations", return_value=mock_report):
        report = run_mutation_audit(
            targets=[TargetConfig("mock", "mock.py", "test_mock.py")],
            strict=True,
        )
        assert report.overall_kill_rate == 80.0
        assert report.success is False


def test_mutation_coverage_kills_all_topological_mutants() -> None:
    """Contract 2: scripts/audit_mutation_coverage.py run against TopologicalEvaluator achieves 100% kill rate."""
    target = next(t for t in DEFAULT_TARGETS if t.name == "topological_evaluator")
    report = audit_target_mutations(target, timeout=15.0)

    assert report.total_mutants >= 10
    assert report.survived_mutants == 0
    assert report.kill_rate == 100.0
    assert all(r.killed for r in report.results)


def test_mutation_coverage_kills_all_arithmetic_mutants() -> None:
    """Contract 1: scripts/audit_mutation_coverage.py run against UnifiedScoringEngine achieves 100% kill rate."""
    target = next(t for t in DEFAULT_TARGETS if t.name == "unified_engine")
    report = audit_target_mutations(target, timeout=15.0)

    assert report.total_mutants >= 20
    assert report.survived_mutants == 0
    assert report.kill_rate == 100.0
    assert all(r.killed for r in report.results)


def test_audit_target_mutations_missing_source_file_raises() -> None:
    """Verifies that audit_target_mutations raises FileNotFoundError for missing source file."""
    target = TargetConfig(name="missing", target_file="nonexistent_src.py", test_file="tests/test_foo.py")
    with pytest.raises(FileNotFoundError, match="Target source file not found"):
        audit_target_mutations(target)


def test_audit_target_mutations_missing_test_file_raises() -> None:
    """Verifies that audit_target_mutations raises FileNotFoundError for missing test file."""
    existing_src = DEFAULT_TARGETS[0].target_file
    target = TargetConfig(name="missing_test", target_file=existing_src, test_file="nonexistent_test.py")
    with pytest.raises(FileNotFoundError, match="Target test suite file not found"):
        audit_target_mutations(target)


def test_audit_target_mutations_timeout_expired() -> None:
    """Verifies that timeout during mutant execution treats mutant as killed."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        dummy_src = tmp_path / "dummy_math.py"
        dummy_test = tmp_path / "test_dummy_math.py"
        dummy_src.write_text("def f(x: int) -> int:\n    return x + 1\n", encoding="utf-8")
        dummy_test.write_text("def test_f(): pass\n", encoding="utf-8")

        target = TargetConfig(name="dummy", target_file=str(dummy_src), test_file=str(dummy_test))
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["pytest"], timeout=1.0)):
            report = audit_target_mutations(target, max_mutants=1)
            assert report.total_mutants == 1
            assert report.killed_mutants == 1
            assert "TIMEOUT" in (report.results[0].killer_output or "")


def test_main_cli_dry_run_json(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies CLI execution with --dry-run and --json."""
    test_args = [
        "scripts/audit_mutation_coverage.py",
        "--dry-run",
        "--json",
        "--target=topological_evaluator",
        "--max-mutants=2",
    ]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert '"success": true' in captured.out


def test_main_cli_dry_run_console_success(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies CLI execution with --dry-run and human-readable console report."""
    test_args = ["scripts/audit_mutation_coverage.py", "--dry-run", "--target=unified_engine", "--max-mutants=2"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "QUORUM V2 AST MUTATION INVARIANCE REPORT" in captured.out
        assert "[PASS] MUTATION INVARIANCE VERIFIED" in captured.out


def test_main_cli_surviving_mutants_failure(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies CLI handles surviving mutants in console reporting and exits with 1."""
    failing_report = TargetAuditReport(
        target_name="mock_target",
        target_file="mock.py",
        test_file="test_mock.py",
        total_mutants=2,
        killed_mutants=1,
        survived_mutants=1,
        kill_rate=50.0,
        results=[
            MutationResult(
                spec=MutationSpec(
                    target_type="Compare",
                    filepath="mock.py",
                    lineno=10,
                    col_offset=4,
                    op_index=0,
                    original_op="Eq",
                    mutated_op="NotEq",
                    description="mock mutation",
                ),
                killed=False,
                killer_output=None,
            )
        ],
    )
    with patch("scripts.audit_mutation_coverage.audit_target_mutations", return_value=failing_report):
        test_args = ["scripts/audit_mutation_coverage.py", "--target=unified_engine", "--strict"]
        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "[WARN] SURVIVING MUTANTS DETECTED" in captured.out
            assert "[FAIL] MUTATION AUDIT FAILED" in captured.out


def test_main_cli_json_failure(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies CLI exits with 1 on JSON output failure."""
    failing_report = TargetAuditReport(
        target_name="mock_target",
        target_file="mock.py",
        test_file="test_mock.py",
        total_mutants=1,
        killed_mutants=0,
        survived_mutants=1,
        kill_rate=0.0,
        results=[],
    )
    with patch("scripts.audit_mutation_coverage.audit_target_mutations", return_value=failing_report):
        test_args = ["scripts/audit_mutation_coverage.py", "--json"]
        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert '"success": false' in captured.out
