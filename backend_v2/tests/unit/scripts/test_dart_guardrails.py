"""ISTQB Unit Tests for Dart Codebase Guardrails Engine (_dart_guardrails.py).

Verifies DGR000 through DGR004 detection, generated file immunity (*.freezed.dart, *.g.dart),
false-positive immunity for non-UI/test scopes, CLI table formatting, and --strict escalation.
"""

from __future__ import annotations

from pathlib import Path

from scripts._dart_guardrails import (
    DartViolation,
    GuardrailSeverity,
    format_dart_violations_table,
    is_generated_dart_file,
    main,
    scan_dart_file,
    scan_dart_files,
    scan_dart_source,
)


def _scan_snippet(
    code: str, filepath: str = "client_app_v2/lib/features/studio/presentation/sample_widget.dart", strict: bool = False
) -> list[DartViolation]:
    """Helper to scan a Dart code snippet as source bytes."""
    return scan_dart_source(filepath, code.encode("utf-8"), strict=strict)


# ==============================================================================
# Partition 1: Generated File Immunity
# ==============================================================================


def test_is_generated_dart_file_freezed_extension() -> None:
    assert is_generated_dart_file("workflow.freezed.dart") is True
    assert is_generated_dart_file("client_app_v2/lib/models/workflow.freezed.dart") is True


def test_is_generated_dart_file_g_extension() -> None:
    assert is_generated_dart_file("workflow.g.dart") is True
    assert is_generated_dart_file("client_app_v2/lib/models/workflow.g.dart") is True


def test_is_generated_dart_file_path_directories() -> None:
    assert is_generated_dart_file("client_app_v2/.dart_tool/package_config.dart") is True
    assert is_generated_dart_file("client_app_v2/build/flutter_assets/AssetManifest.dart") is True


def test_is_generated_dart_file_header_detection() -> None:
    source = "// GENERATED CODE - DO NOT MODIFY BY HAND\n// ignore_for_file: type=lint\n"
    assert is_generated_dart_file("custom_output.dart", source) is True


def test_generated_file_has_zero_violations_even_with_anti_patterns() -> None:
    code = """
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: invalid_annotation_target
Future<Map<String, dynamic>> fetchRaw() async => {};
Widget build() => const SizedBox.shrink();
Widget text() => const Text("Hardcoded string");
"""
    violations = scan_dart_source("workflow.freezed.dart", code.encode("utf-8"), strict=True)
    assert len(violations) == 0


# ==============================================================================
# Partition 2: DGR001 Banned Loose Map Return Types in API Clients & Models
# ==============================================================================


def test_dgr001_typed_dto_return_allowed() -> None:
    code = """
class StudioClient {
  Future<WorkflowDto> getWorkflow(String id) async {
    return WorkflowDto();
  }
}
"""
    violations = _scan_snippet(code, filepath="client_app_v2/lib/core/api/studio_client.dart")
    dgr001 = [v for v in violations if v.rule_code == "DGR001"]
    assert len(dgr001) == 0


def test_dgr001_map_return_in_api_client_warning() -> None:
    code = """
class ExecutionClient {
  Future<Map<String, dynamic>> renderExecution(String id) async {
    return {};
  }
}
"""
    violations = _scan_snippet(code, filepath="client_app_v2/lib/core/api/execution_client.dart", strict=False)
    dgr001 = [v for v in violations if v.rule_code == "DGR001"]
    assert len(dgr001) == 1
    assert dgr001[0].severity == GuardrailSeverity.WARNING
    assert "Map<String, dynamic>" in dgr001[0].message
    assert "renderExecution" in dgr001[0].message


def test_dgr001_map_return_strict_fatal() -> None:
    code = """
class ReportsClient {
  Future<Map<String, dynamic>> getReportSdui(String id) async {
    return {};
  }
}
"""
    violations = _scan_snippet(code, filepath="client_app_v2/lib/core/api/reports_client.dart", strict=True)
    dgr001 = [v for v in violations if v.rule_code == "DGR001"]
    assert len(dgr001) == 1
    assert dgr001[0].severity == GuardrailSeverity.FATAL


def test_dgr001_list_map_return_flagged() -> None:
    code = """
class WorkflowClient {
  Future<List<Map<String, dynamic>>> listWorkflows() async => [];
}
"""
    violations = _scan_snippet(code, filepath="client_app_v2/lib/core/api/workflow_client.dart")
    dgr001 = [v for v in violations if v.rule_code == "DGR001"]
    assert len(dgr001) == 1
    assert "List<Map" in dgr001[0].message


def test_dgr001_outside_api_scope_ignored() -> None:
    code = "Map<String, dynamic> toMap() => {};\n"
    violations = _scan_snippet(code, filepath="client_app_v2/lib/utils/converter.dart")
    dgr001 = [v for v in violations if v.rule_code == "DGR001"]
    assert len(dgr001) == 0


# ==============================================================================
# Partition 3: DGR002 Banned SizedBox.shrink Concealment
# ==============================================================================


def test_dgr002_sizedbox_shrink_in_features_flagged() -> None:
    code = """
Widget build(BuildContext context) {
  if (hasError) {
    return const SizedBox.shrink();
  }
  return const Text("ok");
}
"""
    violations = _scan_snippet(code, filepath="client_app_v2/lib/features/studio/view.dart", strict=False)
    dgr002 = [v for v in violations if v.rule_code == "DGR002"]
    assert len(dgr002) == 1
    assert dgr002[0].severity == GuardrailSeverity.WARNING
    assert "SizedBox.shrink()" in dgr002[0].message


def test_dgr002_sizedbox_shrink_in_shared_flagged() -> None:
    code = "return SizedBox.shrink();\n"
    violations = _scan_snippet(code, filepath="client_app_v2/lib/shared/widgets/card.dart", strict=True)
    dgr002 = [v for v in violations if v.rule_code == "DGR002"]
    assert len(dgr002) == 1
    assert dgr002[0].severity == GuardrailSeverity.FATAL


def test_dgr002_sizedbox_with_dimensions_allowed() -> None:
    code = "return const SizedBox(width: 16, height: 16);\n"
    violations = _scan_snippet(code, filepath="client_app_v2/lib/features/studio/view.dart")
    dgr002 = [v for v in violations if v.rule_code == "DGR002"]
    assert len(dgr002) == 0


# ==============================================================================
# Partition 4: DGR003 Banned Hardcoded UI String Literals
# ==============================================================================


def test_dgr003_localized_string_allowed() -> None:
    code = """
Widget build(BuildContext context) {
  final l10n = AppLocalizations.of(context);
  return Text(l10n.loginTitle);
}
"""
    violations = _scan_snippet(code, filepath="client_app_v2/lib/features/auth/login.dart")
    dgr003 = [v for v in violations if v.rule_code == "DGR003"]
    assert len(dgr003) == 0


def test_dgr003_hardcoded_string_literal_flagged() -> None:
    code = 'return const Text("Mock Login (Admin)");\n'
    violations = _scan_snippet(code, filepath="client_app_v2/lib/features/auth/login.dart", strict=False)
    dgr003 = [v for v in violations if v.rule_code == "DGR003"]
    assert len(dgr003) == 1
    assert dgr003[0].severity == GuardrailSeverity.WARNING
    assert "Mock Login (Admin)" in dgr003[0].message


def test_dgr003_strict_fatal_severity() -> None:
    code = "return Text('Welcome to Quorum');\n"
    violations = _scan_snippet(code, filepath="client_app_v2/lib/features/auth/login.dart", strict=True)
    dgr003 = [v for v in violations if v.rule_code == "DGR003"]
    assert len(dgr003) == 1
    assert dgr003[0].severity == GuardrailSeverity.FATAL


def test_dgr003_pure_punctuation_or_empty_allowed() -> None:
    code = """
final t1 = const Text(":");
final t2 = const Text(" - ");
final t3 = const Text("");
final t4 = Text(" | ");
"""
    violations = _scan_snippet(code, filepath="client_app_v2/lib/features/studio/view.dart")
    dgr003 = [v for v in violations if v.rule_code == "DGR003"]
    assert len(dgr003) == 0


# ==============================================================================
# Partition 5: DGR004 Banned Dart Lint Suppressions
# ==============================================================================


def test_dgr004_ignore_comment_flagged() -> None:
    code = "final x = 1; // ignore: unused_local_variable\n"
    violations = _scan_snippet(code, filepath="client_app_v2/lib/core/utils.dart", strict=False)
    dgr004 = [v for v in violations if v.rule_code == "DGR004"]
    assert len(dgr004) == 1
    assert dgr004[0].severity == GuardrailSeverity.WARNING
    assert "ignore:" in dgr004[0].remediation


def test_dgr004_ignore_for_file_flagged() -> None:
    code = "// ignore_for_file: invalid_annotation_target\nclass MyModel {}\n"
    violations = _scan_snippet(code, filepath="client_app_v2/lib/features/model.dart", strict=True)
    dgr004 = [v for v in violations if v.rule_code == "DGR004"]
    assert len(dgr004) == 1
    assert dgr004[0].severity == GuardrailSeverity.FATAL


def test_dgr004_standard_comment_allowed() -> None:
    code = "// This is a regular design comment explaining why the class exists\nclass Service {}\n"
    violations = _scan_snippet(code, filepath="client_app_v2/lib/core/service.dart")
    dgr004 = [v for v in violations if v.rule_code == "DGR004"]
    assert len(dgr004) == 0


# ==============================================================================
# Partition 6: File I/O, CLI & Formatting Verification
# ==============================================================================


def test_dgr000_unicode_decode_error() -> None:
    invalid_bytes = b"\xff\xfe\x00\x00InvalidDart"
    violations = scan_dart_source("bad.dart", invalid_bytes)
    assert len(violations) == 1
    assert violations[0].rule_code == "DGR000"
    assert violations[0].severity == GuardrailSeverity.FATAL


def test_dgr000_missing_file_error(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.dart"
    violations = scan_dart_file(missing_file)
    assert len(violations) == 1
    assert violations[0].rule_code == "DGR000"
    assert violations[0].severity == GuardrailSeverity.FATAL


def test_scan_dart_files_directory(tmp_path: Path) -> None:
    d = tmp_path / "lib"
    d.mkdir()
    f1 = d / "clean.dart"
    f1.write_text("class Clean {}\n", encoding="utf-8")
    f2 = d / "suppressed.dart"
    f2.write_text("// ignore: avoid_print\n", encoding="utf-8")

    violations = scan_dart_files([d])
    assert len(violations) == 1
    assert violations[0].rule_code == "DGR004"


def test_format_dart_violations_table() -> None:
    v = DartViolation(
        filepath="client_app_v2/lib/core/api/test.dart",
        lineno=10,
        col_offset=2,
        rule_code="DGR001",
        message="Banned Map return type",
        remediation="Use DTO",
        severity=GuardrailSeverity.WARNING,
        is_suppressed=False,
    )
    table = format_dart_violations_table([v])
    assert "DGR001" in table
    assert "WARNING" in table
    assert "Banned Map return type" in table

    empty_table = format_dart_violations_table([])
    assert "No Dart guardrail violations found" in empty_table


def test_main_cli_execution_clean(tmp_path: Path) -> None:
    clean_file = tmp_path / "clean.dart"
    clean_file.write_text("class Clean {}\n", encoding="utf-8")
    exit_code = main([str(clean_file)])
    assert exit_code == 0


def test_main_cli_execution_warning_passes_default(tmp_path: Path) -> None:
    warn_file = tmp_path / "warn.dart"
    warn_file.write_text("// ignore: lint_error\n", encoding="utf-8")
    exit_code = main([str(warn_file)])
    assert exit_code == 0


def test_main_cli_execution_strict_fails(tmp_path: Path) -> None:
    warn_file = tmp_path / "warn.dart"
    warn_file.write_text("// ignore: lint_error\n", encoding="utf-8")
    exit_code = main([str(warn_file), "--strict"])
    assert exit_code == 1
