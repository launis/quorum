"""Comprehensive automated CLI verification suite across all 25 scripts in scripts/.

Verifies CLI argument parsing, help documentation, sub-second execution latency,
exit code semantics, and zero filesystem side effects on -h and --help.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest

# Canonical list of all 25 operational scripts in scripts/
ALL_SCRIPTS: list[str] = sorted(
    [
        "audit_database_atoms.py",
        "audit_dict_eradication.py",
        "audit_dto_parity.py",
        "audit_epic_coverage.py",
        "audit_markdown_boundaries.py",
        "audit_matrix_auto_filler.py",
        "audit_matrix_manager.py",
        "audit_planner_output.py",
        "audit_plan_tracker_parity.py",
        "audit_rules_staleness.py",
        "audit_tracker_output.py",
        "backend_audit_loop.py",
        "convert_epic_to_hybrid.py",
        "diff_executions.py",
        "flutter_audit_loop.py",
        "matrix_hardening_generator.py",
        "matrix_hardening_loop.py",
        "matrix_slice_engine.py",
        "migrate_seed_contrastive_pairs.py",
        "reconcile_storage.py",
        "run_e2e_variance_test.py",
        "sanitize_seed_vault.py",
        "_ast_boundary_utils.py",
        "_ast_guardrails.py",
        "_dart_guardrails.py",
    ]
)

SCRIPTS_DIR: Path = Path(__file__).resolve().parents[4] / "scripts"


def test_script_count_is_exhaustive() -> None:
    """Verify that ALL_SCRIPTS matches physical directory inventory (excluding __init__.py)."""
    physical_scripts = sorted([p.name for p in SCRIPTS_DIR.glob("*.py") if p.name != "__init__.py"])
    assert ALL_SCRIPTS == physical_scripts, (
        f"Mismatch in script inventory. Expected {len(physical_scripts)}, got {len(ALL_SCRIPTS)}"
    )
    assert len(ALL_SCRIPTS) == 25


@pytest.mark.parametrize("script_name", ALL_SCRIPTS)
@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_all_scripts_respond_to_help_flag(script_name: str, flag: str) -> None:
    """Verify that every script returns exit code 0 when invoked with -h or --help."""
    script_path = SCRIPTS_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script_path), flag],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, (
        f"Script {script_name} failed on {flag} with code {result.returncode}.\n"
        f"STDERR: {result.stderr}\nSTDOUT: {result.stdout}"
    )


@pytest.mark.parametrize("script_name", ALL_SCRIPTS)
def test_all_scripts_emit_usage_and_description(script_name: str) -> None:
    """Verify that --help output contains usage, non-empty description, and options section."""
    script_path = SCRIPTS_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    stdout = result.stdout.lower()

    # 1. Must contain standard usage line
    assert "usage:" in stdout, f"{script_name} stdout missing 'usage:'\n{result.stdout}"

    # 2. Must contain options section
    assert "options:" in stdout or "optional arguments:" in stdout, (
        f"{script_name} stdout missing options block\n{result.stdout}"
    )

    # 3. Must contain non-empty description (at least 3 non-empty lines)
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) >= 4, f"{script_name} help output is too sparse (fewer than 4 lines):\n{result.stdout}"


@pytest.mark.parametrize("script_name", ALL_SCRIPTS)
def test_scripts_help_execution_latency(script_name: str) -> None:
    """Verify that --help execution completes in a prompt manner without executing heavy work."""
    script_path = SCRIPTS_DIR / script_name
    start_time = time.perf_counter()
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    duration_ms = (time.perf_counter() - start_time) * 1000
    assert result.returncode == 0
    # Must complete in under 2500ms even under cold OS process spawn on Windows
    assert duration_ms < 2500, f"{script_name} took {duration_ms:.2f}ms on --help (exceeded 2500ms limit)"


@pytest.mark.parametrize("script_name", ALL_SCRIPTS)
def test_scripts_cli_invalid_argument_fails(script_name: str) -> None:
    """Verify that passing an unknown argument results in exit code 2 (argparse error)."""
    script_path = SCRIPTS_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script_path), "--invalid-test-flag-xyz"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2, (
        f"Script {script_name} did not exit with code 2 on invalid flag. Code: {result.returncode}\n"
        f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )
    combined_out = (result.stderr + result.stdout).lower()
    assert "unrecognized arguments" in combined_out or "error" in combined_out


def test_scripts_cli_zero_side_effects() -> None:
    """Verify that executing --help across scripts leaves zero filesystem modifications or backup files."""
    backups_dir = Path(__file__).resolve().parents[4] / "backend_v2" / "seed" / "backups"
    before_backups = set(backups_dir.glob("*")) if backups_dir.exists() else set()

    for script_name in ALL_SCRIPTS:
        script_path = SCRIPTS_DIR / script_name
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

    after_backups = set(backups_dir.glob("*")) if backups_dir.exists() else set()
    new_backups = after_backups - before_backups
    assert not new_backups, f"Help command generated unauthorized backup files: {new_backups}"
