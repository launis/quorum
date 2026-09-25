"""Unit tests for audit_epic_coverage.py.

Verifies post-flight Epic specification coverage, symbol eradication scanning,
and CLI entrypoint behaviors.
"""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from scripts.audit_epic_coverage import (
    extract_phase_content,
    main,
    scan_for_lingering_symbols,
)


def test_extract_phase_content() -> None:
    """Test extract_phase_content helper function across phases and all-phases mode."""
    sample = "# Epic\n## Phase 1: Foundation\nPhase 1 content\n## Phase 2: Logic\nPhase 2 content\n"
    assert "Phase 1 content" in extract_phase_content(sample, 1)
    assert "Phase 2 content" in extract_phase_content(sample, 2)
    assert extract_phase_content(sample, None) == sample


def test_scan_for_lingering_symbols(tmp_path: Path) -> None:
    """Test scan_for_lingering_symbols helper function across backend and client files."""
    assert scan_for_lingering_symbols(tmp_path, set()) == []

    backend = tmp_path / "backend_v2"
    backend.mkdir()
    py_file = backend / "test_module.py"
    py_file.write_text("def legacy_symbol():\n    pass\n", encoding="utf-8")

    # Non-utf8 file handling
    bad_py = backend / "bad_encoding.py"
    bad_py.write_bytes(b"\xff\xfe\x00\x00def broken(): pass")

    client = tmp_path / "client_app_v2"
    client.mkdir()
    dart_file = client / "widget.dart"
    dart_file.write_text("void legacy_symbol() {}\n", encoding="utf-8")

    findings = scan_for_lingering_symbols(tmp_path, {"legacy_symbol"})
    assert len(findings) == 2
    symbols_found = {f[0] for f in findings}
    assert "legacy_symbol" in symbols_found


def test_audit_epic_coverage_cli_success(tmp_path: Path) -> None:
    """Test audit_epic_coverage main() CLI succeeds on valid files and symbols."""
    workspace = tmp_path / "workspace"
    backend_dir = workspace / "backend_v2"
    backend_dir.mkdir(parents=True)

    target_file = backend_dir / "valid_service.py"
    target_file.write_text("class ValidService:\n    pass\n", encoding="utf-8")

    epic_file = tmp_path / "EPIC_TEST.md"
    epic_file.write_text(
        "## Phase 1: Service Update\n\n"
        "- `[MODIFY]` `@[backend_v2/valid_service.py]`\n"
        "<demolish>\n"
        "  `old_deprecated_symbol_none`\n"
        "</demolish>\n",
        encoding="utf-8",
    )

    report_path = tmp_path / "report.md"

    # Execute main via argv
    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "--epic",
                str(epic_file),
                "--phase",
                "1",
                "--workspace-root",
                str(workspace),
                "--output-report",
                str(report_path),
            ]
        )
    assert exc_info.value.code == 0
    assert report_path.exists()
    assert "Epic Coverage Audit Report" in report_path.read_text(encoding="utf-8")


def test_audit_epic_coverage_cli_missing_epic(tmp_path: Path) -> None:
    """Test audit_epic_coverage main() CLI exits with 1 when epic file does not exist."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--epic", str(tmp_path / "missing_epic.md")])
    assert exc_info.value.code == 1


def test_audit_epic_coverage_cli_failures(tmp_path: Path) -> None:
    """Test audit_epic_coverage main() CLI exits with 1 when target file is missing or symbol remains."""
    workspace = tmp_path / "workspace"
    backend_dir = workspace / "backend_v2"
    backend_dir.mkdir(parents=True)

    # Lingering symbol
    legacy_file = backend_dir / "legacy.py"
    legacy_file.write_text("def old_lingering_fn(): pass\n", encoding="utf-8")

    epic_file = tmp_path / "EPIC_FAIL.md"
    epic_file.write_text(
        "## Phase 1: Test\n\n"
        "- `[NEW]` `@[backend_v2/missing_new.py]`\n"
        "- `[DELETE]` `@[backend_v2/legacy.py]`\n"
        "<demolish>\n"
        "  `old_lingering_fn`\n"
        "</demolish>\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "--epic",
                str(epic_file),
                "--workspace-root",
                str(workspace),
            ]
        )
    assert exc_info.value.code == 1
