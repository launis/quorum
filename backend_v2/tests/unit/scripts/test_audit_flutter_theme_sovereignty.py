"""Unit tests for Flutter Theme Sovereignty audit script."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.audit_flutter_theme_sovereignty import (
    DEFAULT_TARGET_FILES,
    ThemeAuditReportDTO,
    ThemeViolationDTO,
    main,
    scan_theme_sovereignty,
)


def test_theme_violation_dto_validation() -> None:
    """Verify ThemeViolationDTO instantiation and extra forbid enforcement."""
    dto = ThemeViolationDTO(
        file_path="lib/test.dart",
        line_number=10,
        line_content="final c = Color(0xFF123456);",
        violation_type="PROHIBITED_RAW_HEX_COLOR",
        remediation="Use colorScheme tokens.",
    )
    assert dto.file_path == "lib/test.dart"
    assert dto.line_number == 10

    with pytest.raises(ValidationError):
        ThemeViolationDTO.model_validate(
            {
                "file_path": "lib/test.dart",
                "line_number": 10,
                "line_content": "bad",
                "violation_type": "type",
                "remediation": "fix",
                "extra_key": "forbidden",
            }
        )


def test_theme_audit_report_dto_validation() -> None:
    """Verify ThemeAuditReportDTO structure and extra forbid enforcement."""
    report = ThemeAuditReportDTO(
        total_files_scanned=1,
        total_violations=0,
        violations=[],
    )
    assert report.total_files_scanned == 1
    assert report.total_violations == 0

    with pytest.raises(ValidationError):
        ThemeAuditReportDTO.model_validate(
            {
                "total_files_scanned": 1,
                "total_violations": 0,
                "violations": [],
                "extra": "bad",
            }
        )


def test_scan_theme_sovereignty_clean_file(tmp_path: Path) -> None:
    """Verify that a compliant Dart file emits zero violations."""
    clean_file = tmp_path / "clean_widget.dart"
    clean_file.write_text(
        """
import 'package:flutter/material.dart';

class CleanWidget extends StatelessWidget {
  const CleanWidget({super.key});

  @override
  Widget build(BuildContext context) {
    // Single line comment
    /* Block comment */
    final theme = Theme.of(context);
    final color = theme.colorScheme.primary;
    final style = theme.textTheme.bodyMedium;
    return Container(color: color, child: Text("Hello", style: style));
  }
}
""",
        encoding="utf-8",
    )

    report = scan_theme_sovereignty([str(clean_file)])
    assert report.total_files_scanned == 1
    assert report.total_violations == 0
    assert len(report.violations) == 0


def test_scan_theme_sovereignty_violations(tmp_path: Path) -> None:
    """Verify detection of hex colors, factory colors, Colors.*, and naked TextStyle in UI widgets."""
    dirty_file = tmp_path / "dirty_widget.dart"
    dirty_file.write_text(
        """
import 'package:flutter/material.dart';

class DirtyWidget extends StatelessWidget {
  const DirtyWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final c1 = Color(0xFF123456);
    final c2 = Color.fromARGB(255, 10, 20, 30);
    final c3 = Color.fromRGBO(10, 20, 30, 0.5);
    final c4 = Colors.blue;
    final s1 = TextStyle(fontSize: 14);
    final s2 = const TextStyle(fontSize: 16);
    return Container();
  }
}
""",
        encoding="utf-8",
    )

    report = scan_theme_sovereignty([str(dirty_file)])
    assert report.total_files_scanned == 1
    assert report.total_violations == 6
    types = [v.violation_type for v in report.violations]
    assert "PROHIBITED_RAW_HEX_COLOR" in types
    assert "PROHIBITED_COLOR_FACTORY" in types
    assert "PROHIBITED_STATIC_COLORS_PALETTE" in types
    assert "PROHIBITED_NAKED_TEXT_STYLE" in types


def test_scan_theme_sovereignty_theme_definition_file(tmp_path: Path) -> None:
    """Verify that theme definition files permit Color(0x...) but prohibit Colors.* and TextStyle."""
    theme_file = tmp_path / "app_colors.dart"
    theme_file.write_text(
        """
import 'package:flutter/material.dart';

class AppSemanticColors {
  final Color validToken = const Color(0xFF00FF00);
  final Color badStatic = Colors.red;
  final TextStyle badStyle = TextStyle(fontSize: 14);
}
""",
        encoding="utf-8",
    )

    report = scan_theme_sovereignty([str(theme_file)])
    assert report.total_files_scanned == 1
    assert report.total_violations == 2
    types = [v.violation_type for v in report.violations]
    assert "PROHIBITED_STATIC_COLORS_PALETTE" in types
    assert "PROHIBITED_TEXT_STYLE" in types
    assert "PROHIBITED_RAW_HEX_COLOR" not in types


def test_scan_theme_sovereignty_specialist_section_exemption(tmp_path: Path) -> None:
    """Verify that specialist_section.dart is exempt from naked TextStyle rule."""
    specialist_file = tmp_path / "specialist_section.dart"
    specialist_file.write_text(
        """
import 'package:flutter/material.dart';

class SpecialistSection extends StatelessWidget {
  const SpecialistSection({super.key});

  @override
  Widget build(BuildContext context) {
    final style = TextStyle(fontSize: 12);
    return Container();
  }
}
""",
        encoding="utf-8",
    )

    report = scan_theme_sovereignty([str(specialist_file)])
    assert report.total_files_scanned == 1
    assert report.total_violations == 0


def test_scan_theme_sovereignty_non_existent_file() -> None:
    """Verify that non-existent paths are safely skipped without crash."""
    report = scan_theme_sovereignty(["non_existent_file.dart"])
    assert report.total_files_scanned == 0
    assert report.total_violations == 0


def test_scan_theme_sovereignty_unicode_error(tmp_path: Path) -> None:
    """Verify handling of invalid UTF-8 files."""
    bad_encoding_file = tmp_path / "bad.dart"
    bad_encoding_file.write_bytes(b"\xff\xfe\x00\x00bad")

    report = scan_theme_sovereignty([str(bad_encoding_file)])
    assert report.total_files_scanned == 1
    assert report.total_violations == 1
    assert report.violations[0].violation_type == "ENCODING_ERROR"


def test_main_cli_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify main CLI with clean file exits with code 0."""
    clean_file = tmp_path / "clean.dart"
    clean_file.write_text("// clean\n", encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["audit_flutter_theme_sovereignty.py", str(clean_file)])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Theme Sovereignty Pass" in captured.out


def test_main_cli_violations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify main CLI with violations exits with code 1."""
    dirty_file = tmp_path / "dirty.dart"
    dirty_file.write_text("final c = Colors.red;\n", encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["audit_flutter_theme_sovereignty.py", str(dirty_file)])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Theme Sovereignty Violations Detected" in captured.out


def test_default_target_files_constant() -> None:
    """Verify DEFAULT_TARGET_FILES list is defined and non-empty."""
    assert len(DEFAULT_TARGET_FILES) >= 5
    assert "client_app_v2/lib/theme/app_colors.dart" in DEFAULT_TARGET_FILES
