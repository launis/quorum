"""Unit Tests for Clean Import Verification Tool (scripts/audit_clean_imports.py).

Verifies deterministic module scanning, circular dependency detection, syntax error handling,
path exclusions, and CLI JSON reporting.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Generator
from pathlib import Path

import pytest

# Add repo root to sys.path
repo_root = Path(".").resolve()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from scripts.audit_clean_imports import (
    main as audit_clean_imports_main,
)
from scripts.audit_clean_imports import (
    scan_clean_imports,
)


@pytest.fixture
def clean_import_env(tmp_path: Path) -> Generator[Path]:
    """Fixture ensuring sys.path and sys.modules rollbacks after synthetic imports."""
    orig_path = list(sys.path)
    orig_modules = set(sys.modules.keys())

    yield tmp_path

    sys.path[:] = orig_path
    for mod in list(sys.modules.keys()):
        if mod not in orig_modules:
            del sys.modules[mod]


def test_clean_imports_success_on_valid_module(clean_import_env: Path) -> None:
    """Verify that syntactically valid and decoupled modules import with 100% pass."""
    pkg_dir = clean_import_env / "synth_clean_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("# init", encoding="utf-8")
    (pkg_dir / "valid_service.py").write_text(
        "CONST_VAL = 42\n\ndef get_val() -> int:\n    return CONST_VAL\n",
        encoding="utf-8",
    )

    report = scan_clean_imports(
        target_dir=pkg_dir,
        repo_root=clean_import_env,
    )

    assert report.passed is True
    assert report.total_modules_scanned == 2
    assert report.successful_imports == 2
    assert report.failed_imports == 0
    assert len(report.failures) == 0


def test_clean_imports_detects_circular_dependency(clean_import_env: Path) -> None:
    """Contract: test_clean_imports_detects_circular_dependency.

    Two synthetic modules importing each other at top level must trigger a failure
    reporting a circular import error.
    """
    pkg_dir = clean_import_env / "synth_circ_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "module_alpha.py").write_text(
        "from synth_circ_pkg.module_beta import BETA_CONST\nALPHA_CONST = 'A'\n",
        encoding="utf-8",
    )
    (pkg_dir / "module_beta.py").write_text(
        "from synth_circ_pkg.module_alpha import ALPHA_CONST\nBETA_CONST = 'B'\n",
        encoding="utf-8",
    )

    report = scan_clean_imports(
        target_dir=pkg_dir,
        repo_root=clean_import_env,
    )

    assert report.passed is False
    assert report.failed_imports >= 1
    failure_messages = [f.error_message.lower() for f in report.failures]
    assert any(
        "circular" in msg or "partially initialized" in msg or "cannot import name" in msg for msg in failure_messages
    )


def test_clean_imports_detects_syntax_error(clean_import_env: Path) -> None:
    """Verify that syntax errors are trapped cleanly and reported with SyntaxError type."""
    pkg_dir = clean_import_env / "synth_syntax_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "broken.py").write_text("def unclosed_func(\n", encoding="utf-8")

    report = scan_clean_imports(
        target_dir=pkg_dir,
        repo_root=clean_import_env,
    )

    assert report.passed is False
    assert report.failed_imports == 1
    assert report.failures[0].error_type == "SyntaxError"
    assert report.failures[0].module_name == "synth_syntax_pkg.broken"


def test_clean_imports_detects_missing_dependency(clean_import_env: Path) -> None:
    """Verify that unresolvable external imports trigger ModuleNotFoundError."""
    pkg_dir = clean_import_env / "synth_missing_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "missing.py").write_text(
        "import non_existent_quorum_phantom_lib_12345\n",
        encoding="utf-8",
    )

    report = scan_clean_imports(
        target_dir=pkg_dir,
        repo_root=clean_import_env,
    )

    assert report.passed is False
    assert report.failed_imports == 1
    assert report.failures[0].error_type == "ModuleNotFoundError"


def test_clean_imports_excludes_specified_dirs(clean_import_env: Path) -> None:
    """Verify that excluded subdirectories (e.g. tests, __pycache__) are ignored."""
    pkg_dir = clean_import_env / "synth_exclude_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")

    tests_dir = pkg_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "test_broken.py").write_text("invalid syntax (\n", encoding="utf-8")

    report = scan_clean_imports(
        target_dir=pkg_dir,
        repo_root=clean_import_env,
        exclude_dirs=("tests", "__pycache__"),
    )

    assert report.passed is True
    assert report.total_modules_scanned == 1
    assert report.failed_imports == 0


def test_clean_imports_cli_main_clean(clean_import_env: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify CLI main entrypoint returns exit code 0 and valid JSON on clean modules."""
    pkg_dir = clean_import_env / "synth_cli_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "mod.py").write_text("X = 1\n", encoding="utf-8")

    exit_code = audit_clean_imports_main(
        [
            "--target-dir",
            str(pkg_dir),
            "--repo-root",
            str(clean_import_env),
            "--json",
        ]
    )

    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["passed"] is True
    assert data["total_modules_scanned"] == 2


def test_clean_imports_cli_main_failure(clean_import_env: Path) -> None:
    """Verify CLI main entrypoint returns exit code 1 when errors exist."""
    pkg_dir = clean_import_env / "synth_cli_fail_pkg"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("import phantom_module_does_not_exist_987\n", encoding="utf-8")

    exit_code = audit_clean_imports_main(
        [
            "--target-dir",
            str(pkg_dir),
            "--repo-root",
            str(clean_import_env),
        ]
    )

    assert exit_code == 1
