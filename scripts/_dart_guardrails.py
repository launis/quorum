"""Automated Dart Codebase Guardrails Engine (DGR001-DGR014).

Single Source of Truth for static Dart architectural rules enforcement across Quorum Flutter client.
Scans handwritten client code across full multi-line source text for loose Map types, anonymous HTTP
payloads, UI error concealment, unlocalized strings, lint suppressions, hardcoded hex colors, manual
string clippings, missing error boundaries, unguarded async values, deprecated useIsMounted() or
unguarded post-await hook ValueNotifier mutations, GoRouter provider ref.watch disposal hazards,
banned Freezed .when()/.maybeWhen()/.map() chains, and manual Riverpod providers or ref.read/ref.watch misuse.
Guarantees 100% false-positive immunity for generated files (*.freezed.dart, *.g.dart, .dart_tool/, build/).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

try:
    from _script_base import (
        GuardrailSeverity as GuardrailSeverity,
    )
    from _script_base import (
        setup_script_environment,
    )
except ImportError:
    from scripts._script_base import (
        GuardrailSeverity as GuardrailSeverity,
    )
    from scripts._script_base import (
        setup_script_environment,
    )

setup_script_environment()

__all__ = [
    "DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES",
    "DGR013_FREEZED_WHEN_PATTERN",
    "DGR014_CALLBACK_REF_WATCH_PATTERN",
    "DGR014_LEGACY_PROVIDER_PATTERN",
    "DartViolation",
    "GuardrailSeverity",
    "format_dart_violations_table",
    "is_dgr005_object_map_exempt",
    "is_generated_dart_file",
    "main",
    "scan_dart_file",
    "scan_dart_files",
    "scan_dart_source",
]


class DartViolation(BaseModel):
    """Pydantic V2 DTO representing a Dart architectural violation.

    Attributes:
        filepath: Target file path relative to workspace.
        lineno: 1-indexed line number where violation occurred.
        col_offset: Column offset of violation.
        rule_code: Rule code matching pattern DGR000-DGR999.
        message: Descriptive violation message.
        remediation: Deterministic remediation guidance.
        severity: Severity tier of the violation.
        is_suppressed: Whether violation is suppressed.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    filepath: Annotated[str, Field(description="Target file path relative to workspace")]
    lineno: Annotated[int, Field(ge=0, description="1-indexed line number where violation occurred")]
    col_offset: Annotated[int, Field(ge=0, description="Column offset of violation")]
    rule_code: Annotated[str, Field(pattern=r"^DGR\d{3}$", description="Rule code e.g. DGR001")]
    message: Annotated[str, Field(description="Descriptive violation message")]
    remediation: Annotated[str, Field(description="Deterministic remediation guidance")]
    severity: Annotated[GuardrailSeverity, Field(description="Severity tier")]
    is_suppressed: Annotated[bool, Field(description="Whether violation is suppressed")]


# Any file outside these 9 pure transport boundary files using Map<String, Object?> triggers a FATAL DGR005 violation.
DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES: frozenset[str] = frozenset(
    {
        # HTTP / SSE / Error transport boundaries (Group 1 only)
        "client_app_v2/lib/core/api/execution_client.dart",
        "client_app_v2/lib/core/api/reports_client.dart",
        "client_app_v2/lib/core/api/sse_client.dart",
        "client_app_v2/lib/core/api/studio_client.dart",
        "client_app_v2/lib/core/api/workflow_client.dart",
        "client_app_v2/lib/core/error/app_exception.dart",
        "client_app_v2/lib/core/network/interceptors/error_interceptor.dart",
        "client_app_v2/lib/features/auth/data/auth_repository.dart",
        "client_app_v2/lib/features/auth/data/repositories/user_repository.dart",
    }
)


# ==============================================================================
# Multi-Line Capable Rule Patterns
# ==============================================================================

# Tokenizer pattern matching Dart string literals or single/multi-line comments
_DART_STRING_OR_COMMENT_PATTERN = re.compile(
    r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/)'
)

# DGR001: Loose Map return types in API clients, models, controllers, or providers (single or multi-line)
DGR001_PATTERN = re.compile(
    r"\b(Future\s*<\s*List\s*<\s*Map(?:\s*<[^>]+>)?\s*>\s*>|"
    r"FutureOr\s*<\s*List\s*<\s*Map(?:\s*<[^>]+>)?\s*>\s*>|"
    r"Future\s*<\s*Map(?:\s*<[^>]+>)?\s*>|"
    r"FutureOr\s*<\s*Map(?:\s*<[^>]+>)?\s*>|"
    r"List\s*<\s*Map(?:\s*<[^>]+>)?\s*>|"
    r"Map\s*<[A-Za-z0-9_?,\s]+>)\s+([A-Za-z0-9_]+)\s*\("
)

# DGR002: SizedBox.shrink() concealment (single or multi-line)
DGR002_PATTERN = re.compile(r"\b(?:const\s+)?SizedBox\s*\.\s*shrink\s*\(\s*\)")

# DGR003: Raw hardcoded string literals in Text(...) widgets (single-line, multi-line, and adjacent string literals)
DGR003_TEXT_LITERAL_PATTERN = re.compile(r"\b(?:const\s+)?Text\s*\(\s*((?:(['\"])(?:\\.|(?!\2)[^\n\\])*\2\s*)+)\s*[,)]")
_DGR003_STRING_SEGMENT_PATTERN = re.compile(r"(['\"])((?:\\.|(?!\1)[^\n\\])*)\1")

DGR003_RAW_ERROR_PATTERN = re.compile(
    r"\b(?:l10n\.\w+\s*\(\s*(?:(?:e|err|error)\s*\.\s*toString\s*\(\s*\)|['\"]\$(?:e|err|error)['\"])"
    r"|AsyncError\s*\([^)]*\)\s*=>\s*(?:const\s+)?Text\s*\(\s*(?:e|err|error)\s*\.\s*toString\s*\(\s*\))",
    re.DOTALL,
)

# DGR004: Dart lint suppressions (// ignore: or // ignore_for_file:) and plan/phase/step breadcrumb comments
DGR004_PATTERN = re.compile(r"//\s*(?:ignore_for_file|ignore):")
DGR004_PLAN_BREADCRUMB_PATTERN = re.compile(
    r"///*\s*(?:Phase\s+\d+[A-Z]?\s*(?:,\s*Step\s+\d+(?:\.\d+)?(?:\s*&\s*Step\s+\d+(?:\.\d+)?)?|:)|Step\s+\d+(?:\.\d+)?\s*:)|//[^\n]*\(\s*REQ-\d{3}\s*\)"
)

# DGR005: Non-codec Map<String, dynamic>, Map<String, Object?>, Map<Object?, Object?>, or Map<dynamic, dynamic>
DGR005_DYNAMIC_MAP_PATTERN = re.compile(
    r"\bMap\s*<\s*(?:String|dynamic|Object\??)\s*,\s*dynamic\s*>"
    r"|\bMap\s*<\s*dynamic\s*,\s*[A-Za-z0-9_?\s]+\s*>"
)
DGR005_OBJECT_MAP_PATTERN = re.compile(r"\bMap\s*<\s*(?:String|Object\??|dynamic)\s*,\s*Object\??\s*>")
DGR005_CODEC_EXEMPT_PATTERN = re.compile(
    r"fromJson\s*\(\s*Map\s*<\s*String\s*,\s*(?:dynamic|Object\??)\s*>\s+\w+\s*,?\s*\)"
    r"|Map\s*<\s*String\s*,\s*(?:dynamic|Object\??)\s*>\s+toJson\s*\("
)

# DGR006: Anonymous Map literals in HTTP request payloads (single or multi-line, with optional type args)
DGR006_PATTERN = re.compile(r"\b(?:data|queryParameters)\s*:\s*(?:<[^>]+>\s*)?\{")

# DGR007: Banned hardcoded hex colors, direct Colors.* calls, or deprecated .withOpacity(...) in UI widgets
DGR007_PATTERN = re.compile(r"\bColor\s*\(\s*0x[0-9a-fA-F]+\s*,?\s*\)|\bColors\s*\.\s*[a-zA-Z]+")
DGR007_WITH_OPACITY_PATTERN = re.compile(r"\.\s*withOpacity\s*\(")

# DGR008: Banned manual string clippings via .substring() and legacy Uuid().v4()
DGR008_PATTERN = re.compile(r"\.\s*substring\s*\(")
DGR008_UUID_V4_PATTERN = re.compile(r"\.\s*v4\s*\(")

# DGR010: Missing AsyncValue guards on dynamic AsyncNotifierProvider consumers
DGR010_PATTERN = re.compile(r"\.\s*requireValue\b")

# DGR011: Deprecated useIsMounted() hook & custom hook post-await ValueNotifier disposal guard
DGR011_USE_IS_MOUNTED_PATTERN = re.compile(r"\buseIsMounted\s*\(")
_CUSTOM_HOOK_HEADER_PATTERN = re.compile(
    r"\b[A-Za-z0-9_<>,?]+\s+(use[A-Z]\w*)\s*(?:<[^>]+>)?\s*\([^)]*\)\s*\{",
    re.DOTALL,
)

# DGR012: GoRouter provider direct ref.watch disposal hazard & mandatory refreshListenable
_GOROUTER_PROVIDER_HEADER_PATTERN = re.compile(r"\bGoRouter\s+router\s*\(\s*[A-Za-z0-9_]*Ref\s+\w+\s*\)\s*\{")
DGR012_REF_WATCH_PATTERN = re.compile(r"\bref\s*\.\s*watch\s*\(")

DGR013_FREEZED_WHEN_PATTERN = re.compile(
    r"\.\s*(?:when|maybeWhen|maybeMap|whenOrNull|mapOrNull)\s*\("
    r"|\.\s*map\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*:"
)

DGR014_LEGACY_PROVIDER_PATTERN = re.compile(
    r"\b(?:StateProvider|ChangeNotifierProvider|StateNotifierProvider|ChangeNotifier)\b"
)
DGR014_CALLBACK_REF_WATCH_PATTERN = re.compile(
    r"\bon[A-Z][A-Za-z0-9_]*\s*:\s*(?:\([^)]*\)\s*(?:async\s*)?\{[^}]*?\bref\s*\.\s*watch\s*\("
    r"|\([^)]*\)\s*(?:async\s*)?=>[^\n;]*?\bref\s*\.\s*watch\s*\()",
    re.DOTALL,
)
_WIDGET_BUILD_HEADER_PATTERN = re.compile(
    r"\bWidget\s+build\s*\([^)]*\)\s*\{",
    re.DOTALL,
)
_DGR014_REF_READ_CALL_PATTERN = re.compile(r"\bref\s*\.\s*read\s*\(([^)]*)\)")

# Ignored trivial string literals for DGR003 (pure symbols or separators)
PUNCTUATION_OR_EMPTY_PATTERN = re.compile(r"^[\s\-:–—|/\\.,;*+~#_!?@$%^&()\[\]{}'\"0-9→←↑↓↳•×+%=<>]*$")


def _strip_dart_comments(source_text: str) -> str:
    """Replace Dart line and block comments with spaces while preserving string literals and newlines.

    Preserving newline characters ensures that character offsets in the returned string map 1:1
    to the exact 1-based line numbers and column offsets in the original source text.

    Args:
        source_text: Raw Dart source text.

    Returns:
        Source text with all comments replaced by whitespace of identical length and line structure.
    """

    def _replace_match(match: re.Match[str]) -> str:
        token = match.group(0)
        if token.startswith("//") or token.startswith("/*"):
            return "".join("\n" if ch == "\n" else " " for ch in token)
        return token

    return _DART_STRING_OR_COMMENT_PATTERN.sub(_replace_match, source_text)


def _offset_to_line_col(source_text: str, offset: int) -> tuple[int, int]:
    """Convert a 0-based character offset in source_text to (1-based lineno, 0-based col_offset).

    Args:
        source_text: Full source text string.
        offset: 0-based character index into source_text.

    Returns:
        2-tuple of (lineno, col_offset).
    """
    lineno = source_text.count("\n", 0, offset) + 1
    last_nl = source_text.rfind("\n", 0, offset)
    col_offset = offset if last_nl == -1 else offset - last_nl - 1
    return lineno, max(0, col_offset)


def _strip_dart_interpolations(text: str) -> str:
    """Strip Dart string interpolations and numeric unit suffixes from a string literal.

    Args:
        text: Raw string literal contents extracted from a Text widget.

    Returns:
        Remaining static text after removing ${...}, $ident, escaped newlines, and 'ms' unit tokens.
    """
    without_braces = re.sub(r"\$\{[^}]*\}", "", text)
    without_vars = re.sub(r"\$[a-zA-Z_][a-zA-Z0-9_]*", "", without_braces)
    without_escapes = without_vars.replace("\\n", " ")
    return re.sub(r"\bms\b", "", without_escapes).strip()


def is_dgr005_object_map_exempt(filepath: str) -> bool:
    """Check whether a file path is in the locked DGR005 Map<String, Object?> boundary/open-JSON exemption set.

    Args:
        filepath: File path string to evaluate.

    Returns:
        True if the file is an exempted transport boundary, open-JSON DTO, or locked residual file.
    """
    normalized = filepath.replace("\\", "/").strip("/")
    if normalized in DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES:
        return True
    return any(normalized.endswith("/" + exempt) for exempt in DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES)


def is_generated_dart_file(filepath: Path | str, source_text: str | None = None) -> bool:
    """Check if a Dart file is generated by build_runner or external tooling.

    Args:
        filepath: File path to inspect for generated extensions or directories.
        source_text: Optional file text content to inspect header comments.

    Returns:
        True if the file is an auto-generated artifact, False otherwise.
    """
    p = Path(filepath)
    name = p.name.lower()
    if name.endswith(".freezed.dart") or name.endswith(".g.dart"):
        return True

    normalized_path = str(p).replace("\\", "/")
    if (
        name == "firebase_options.dart"
        or "/l10n/gen/" in normalized_path
        or normalized_path.endswith("/l10n/gen")
        or "l10n/gen" in normalized_path
    ):
        return True

    parts = set(normalized_path.strip("/").split("/"))
    if ".dart_tool" in parts or "build" in parts:
        return True

    if source_text is not None:
        for line in source_text.splitlines()[:15]:
            upper_line = line.upper()
            if "GENERATED CODE - DO NOT MODIFY BY HAND" in upper_line or "GENERATED BY BUILD_RUNNER" in upper_line:
                return True

    return False


def _check_api_and_codec_multiline_rules(
    filepath: str,
    source_text: str,
    uncommented_text: str,
    *,
    is_api_or_model_scope: bool,
    is_test_scope: bool,
) -> list[DartViolation]:
    """Evaluate DGR001, DGR005, and DGR006 across full comment-stripped multi-line Dart source.

    Args:
        filepath: Target file path being scanned.
        source_text: Original decoded UTF-8 source text.
        uncommented_text: Source text with comments replaced by spaces preserving line breaks.
        is_api_or_model_scope: Whether the file resides in an API, model, controller, data, repository, or provider directory.
        is_test_scope: Whether the file resides in a test directory.

    Returns:
        List of DartViolation instances detected in the file.
    """
    violations: list[DartViolation] = []
    codec_exempt_spans = [m.span() for m in DGR005_CODEC_EXEMPT_PATTERN.finditer(uncommented_text)]

    def _is_inside_codec_span(offset: int) -> bool:
        return any(start <= offset < end for start, end in codec_exempt_spans)

    if is_api_or_model_scope and not is_test_scope:
        for dgr001_match in DGR001_PATTERN.finditer(uncommented_text):
            if _is_inside_codec_span(dgr001_match.start()):
                continue
            ret_type = re.sub(r"\s+", " ", dgr001_match.group(1).strip())
            method_name = dgr001_match.group(2).strip()
            lineno, col_offset = _offset_to_line_col(source_text, dgr001_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR001",
                    message=f"Banned loose Map return type `{ret_type}` in method `{method_name}`.",
                    remediation="Return strongly typed Freezed DTOs or domain models instead of raw Map<String, dynamic> in API clients.",
                    severity=GuardrailSeverity.FATAL,
                    is_suppressed=False,
                )
            )

    seen_dgr005_offsets: set[int] = set()
    if not is_test_scope:
        for dgr005_match in DGR005_DYNAMIC_MAP_PATTERN.finditer(uncommented_text):
            start_pos = dgr005_match.start()
            if _is_inside_codec_span(start_pos):
                continue
            seen_dgr005_offsets.add(start_pos)
            lineno, col_offset = _offset_to_line_col(source_text, start_pos)
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR005",
                    message="Banned non-codec `Map<String, dynamic>` detected in handwritten Dart code.",
                    remediation="Retype to a strongly typed Freezed DTO or domain model instead of raw Map.",
                    severity=GuardrailSeverity.FATAL,
                    is_suppressed=False,
                )
            )

    if not is_test_scope and not is_dgr005_object_map_exempt(filepath):
        for obj_map_match in DGR005_OBJECT_MAP_PATTERN.finditer(uncommented_text):
            start_pos = obj_map_match.start()
            if start_pos in seen_dgr005_offsets or _is_inside_codec_span(start_pos):
                continue
            matched_token = re.sub(r"\s+", " ", obj_map_match.group(0).strip())
            lineno, col_offset = _offset_to_line_col(source_text, start_pos)
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR005",
                    message=f"Banned untyped `{matched_token}` map loophole detected in handwritten Dart code.",
                    remediation="Retype to a strongly typed Freezed DTO or domain model instead of `Map<String, Object?>`.",
                    severity=GuardrailSeverity.FATAL,
                    is_suppressed=False,
                )
            )

    if not is_test_scope:
        for dgr006_match in DGR006_PATTERN.finditer(uncommented_text):
            lineno, col_offset = _offset_to_line_col(source_text, dgr006_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR006",
                    message="Banned anonymous Map literal in HTTP request payload `data: { ... }` or `queryParameters: { ... }`.",
                    remediation="Serialize a strongly typed Freezed DTO via `request.toJson()` instead of passing an inline Map literal.",
                    severity=GuardrailSeverity.FATAL,
                    is_suppressed=False,
                )
            )

    return violations


def _check_ui_and_feature_multiline_rules(
    filepath: str,
    source_text: str,
    uncommented_text: str,
    *,
    is_ui_scope: bool,
    is_feature_widget_scope: bool,
    is_theme_scope: bool,
    is_test_scope: bool,
    default_severity: GuardrailSeverity,
) -> list[DartViolation]:
    """Evaluate DGR002, DGR003, DGR007, DGR008, and DGR010 across full comment-stripped Dart source.

    Args:
        filepath: Target file path being scanned.
        source_text: Original decoded UTF-8 source text.
        uncommented_text: Source text with comments replaced by spaces preserving line breaks.
        is_ui_scope: Whether the file is a non-test, non-theme Dart source file.
        is_feature_widget_scope: Whether the file is a non-test, non-theme Dart source file.
        is_theme_scope: Whether the file is a theme token definition file.
        is_test_scope: Whether the file resides in a test directory.
        default_severity: Default severity tier (WARNING or FATAL when strict).

    Returns:
        List of DartViolation instances detected across single-line and multi-line constructs.
    """
    violations: list[DartViolation] = []

    if is_ui_scope:
        for dgr002_match in DGR002_PATTERN.finditer(uncommented_text):
            lineno, col_offset = _offset_to_line_col(source_text, dgr002_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR002",
                    message="Banned `SizedBox.shrink()` UI error or layout concealment detected.",
                    remediation="Use `AppErrorBoundary`, typed error state widgets, or explicit empty placeholders instead of `SizedBox.shrink()`.",
                    severity=default_severity,
                    is_suppressed=False,
                )
            )

        for err_match in DGR003_RAW_ERROR_PATTERN.finditer(uncommented_text):
            lineno, col_offset = _offset_to_line_col(source_text, err_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR003",
                    message="Banned raw exception `.toString()` or `'$e'` in UI localization/error widget.",
                    remediation="Use `AppExceptionX.extractLocalizedHint(error, l10n)` instead of passing raw `error.toString()` or `'$e'` to UI strings.",
                    severity=default_severity,
                    is_suppressed=False,
                )
            )

    if is_feature_widget_scope:
        for dgr003_match in DGR003_TEXT_LITERAL_PATTERN.finditer(uncommented_text):
            literal_cluster = dgr003_match.group(1)
            segments = _DGR003_STRING_SEGMENT_PATTERN.findall(literal_cluster)
            raw_text = "".join(seg[1] for seg in segments)
            static_residue = _strip_dart_interpolations(raw_text)
            if not PUNCTUATION_OR_EMPTY_PATTERN.match(static_residue):
                lineno, col_offset = _offset_to_line_col(source_text, dgr003_match.start())
                is_multiline = "\n" in dgr003_match.group(0)
                prefix_label = (
                    "Banned multi-line hardcoded string literal" if is_multiline else "Banned hardcoded string literal"
                )
                violations.append(
                    DartViolation(
                        filepath=filepath,
                        lineno=lineno,
                        col_offset=col_offset,
                        rule_code="DGR003",
                        message=f'{prefix_label} `"{raw_text}"` in `Text()` widget.',
                        remediation="Use `AppLocalizations.of(context)` or `.arb` localization keys instead of raw hardcoded strings in `Text(...)` widgets.",
                        severity=default_severity,
                        is_suppressed=False,
                    )
                )

        if not is_theme_scope:
            for dgr007_match in DGR007_PATTERN.finditer(uncommented_text):
                matched_color = re.sub(r"\s+", " ", dgr007_match.group(0).strip())
                lineno, col_offset = _offset_to_line_col(source_text, dgr007_match.start())
                violations.append(
                    DartViolation(
                        filepath=filepath,
                        lineno=lineno,
                        col_offset=col_offset,
                        rule_code="DGR007",
                        message=f"Banned hardcoded hex color or direct Colors.* call `{matched_color}` in feature widget.",
                        remediation="Use Theme.of(context).colorScheme tokens or DesignTokens instead of hardcoded Color(0x...) or Colors.*.",
                        severity=default_severity,
                        is_suppressed=False,
                    )
                )

            for opacity_match in DGR007_WITH_OPACITY_PATTERN.finditer(uncommented_text):
                lineno, col_offset = _offset_to_line_col(source_text, opacity_match.start())
                violations.append(
                    DartViolation(
                        filepath=filepath,
                        lineno=lineno,
                        col_offset=col_offset,
                        rule_code="DGR007",
                        message="Banned deprecated `.withOpacity(...)` call detected in feature widget.",
                        remediation="Use .withValues(alpha: ...) instead of deprecated .withOpacity(...) for Impeller wide-gamut color precision.",
                        severity=default_severity,
                        is_suppressed=False,
                    )
                )

    if not is_test_scope:
        for dgr008_match in DGR008_PATTERN.finditer(uncommented_text):
            lineno, col_offset = _offset_to_line_col(source_text, dgr008_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR008",
                    message="Banned manual string clipping via `.substring()` detected.",
                    remediation="Use LinguisticShield, safeTruncate(), or character boundary utilities instead of manual `.substring()`.",
                    severity=default_severity,
                    is_suppressed=False,
                )
            )

        for v4_match in DGR008_UUID_V4_PATTERN.finditer(uncommented_text):
            lineno, col_offset = _offset_to_line_col(source_text, v4_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR008",
                    message="Banned legacy `Uuid().v4()` version-4 UUID generation detected.",
                    remediation="Use `generateOpaqueUuid7(prefix)` or `const Uuid().v7()` to enforce 32-hex RFC 9562 UUIDv7 parity.",
                    severity=default_severity,
                    is_suppressed=False,
                )
            )

        for dgr010_match in DGR010_PATTERN.finditer(uncommented_text):
            lineno, col_offset = _offset_to_line_col(source_text, dgr010_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR010",
                    message="Missing AsyncValue guard: direct `.requireValue` access detected on dynamic AsyncValue consumer.",
                    remediation="Use Dart 3 native switch pattern matching (switch (asyncVal) { AsyncData(:final value) => ..., AsyncError(:final error) => ..., AsyncLoading() => ... }) or .valueOrNull instead of .requireValue.",
                    severity=default_severity,
                    is_suppressed=False,
                )
            )

    return violations


def _extract_brace_block(text: str, open_brace_index: int) -> str:
    """Extract a balanced brace-enclosed substring starting at open_brace_index.

    Args:
        text: Comment-stripped Dart source text.
        open_brace_index: Index of the opening '{' character.

    Returns:
        Substring from open_brace_index through the matching closing '}', or to the end of text.
    """
    depth = 0
    for idx in range(open_brace_index, len(text)):
        ch = text[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace_index : idx + 1]
    return text[open_brace_index:]


def _check_hook_and_router_lifecycle_rules(
    filepath: str,
    source_text: str,
    uncommented_text: str,
    *,
    is_test_scope: bool,
) -> list[DartViolation]:
    """Evaluate DGR011 (hook mounted safety) and DGR012 (GoRouter refreshListenable) across Dart source.

    Args:
        filepath: Target file path being scanned.
        source_text: Original decoded UTF-8 source text.
        uncommented_text: Source text with comments replaced by spaces preserving line breaks.
        is_test_scope: Whether the file resides in a test directory.

    Returns:
        List of DartViolation instances for DGR011 and DGR012.
    """
    if is_test_scope:
        return []

    violations: list[DartViolation] = []

    # DGR011 Check A: Banned deprecated useIsMounted() hook call
    for mounted_match in DGR011_USE_IS_MOUNTED_PATTERN.finditer(uncommented_text):
        lineno, col_offset = _offset_to_line_col(source_text, mounted_match.start())
        violations.append(
            DartViolation(
                filepath=filepath,
                lineno=lineno,
                col_offset=col_offset,
                rule_code="DGR011",
                message="Banned deprecated `useIsMounted()` hook call detected.",
                remediation="Capture `final context = useContext();` and check `if (!context.mounted) return ...;` after every `await`.",
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        )

    # DGR011 Check B: Unguarded post-await ValueNotifier state.value assignment inside custom hooks
    for hook_match in _CUSTOM_HOOK_HEADER_PATTERN.finditer(uncommented_text):
        hook_name = hook_match.group(1)
        body_start = hook_match.end() - 1
        hook_body = _extract_brace_block(uncommented_text, body_start)
        state_vars = re.findall(r"\bfinal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*useState\b", hook_body)
        first_await = re.search(r"\bawait\s+", hook_body)
        if not state_vars or first_await is None:
            continue

        await_end = first_await.end()
        catch_match = re.search(r"\bcatch\s*\(", hook_body[await_end:])
        catch_offset = (await_end + catch_match.start()) if catch_match is not None else len(hook_body)

        for state_var in state_vars:
            assign_pattern = re.compile(rf"\b{re.escape(state_var)}\s*\.\s*value\s*=")
            for assign_match in assign_pattern.finditer(hook_body):
                assign_pos = assign_match.start()
                if assign_pos <= await_end:
                    continue
                segment_start = await_end if assign_pos < catch_offset else catch_offset
                preceding_segment = hook_body[segment_start:assign_pos]
                if "mounted" not in preceding_segment:
                    lineno, col_offset = _offset_to_line_col(source_text, body_start + assign_pos)
                    violations.append(
                        DartViolation(
                            filepath=filepath,
                            lineno=lineno,
                            col_offset=col_offset,
                            rule_code="DGR011",
                            message=(
                                f"Unguarded post-await ValueNotifier mutation `{state_var}.value = ...` "
                                f"in custom hook `{hook_name}` without `context.mounted` check."
                            ),
                            remediation=(
                                "Capture `final context = useContext();` and check `if (!context.mounted) return ...;` "
                                "immediately after `await` (and inside `catch`) before mutating hook `ValueNotifier` state."
                            ),
                            severity=GuardrailSeverity.FATAL,
                            is_suppressed=False,
                        )
                    )

    # DGR012: GoRouter provider direct ref.watch disposal hazard & mandatory refreshListenable
    for router_match in _GOROUTER_PROVIDER_HEADER_PATTERN.finditer(uncommented_text):
        body_start = router_match.end() - 1
        router_body = _extract_brace_block(uncommented_text, body_start)
        for watch_match in DGR012_REF_WATCH_PATTERN.finditer(router_body):
            lineno, col_offset = _offset_to_line_col(source_text, body_start + watch_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR012",
                    message="Banned `ref.watch(...)` inside `GoRouter router(Ref ref)` provider; disposes and recreates GoRouter on state transitions.",
                    remediation=(
                        "Bridge reactive auth state via `ValueNotifier` + `ref.listen` + `ref.onDispose` "
                        "and pass `refreshListenable: authStateNotifier` to `GoRouter(...)`."
                    ),
                    severity=GuardrailSeverity.FATAL,
                    is_suppressed=False,
                )
            )
        if re.search(r"\bGoRouter\s*\(", router_body) and not re.search(r"\brefreshListenable\s*:", router_body):
            lineno, col_offset = _offset_to_line_col(source_text, router_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR012",
                    message="`GoRouter router(Ref ref)` provider is missing mandatory `refreshListenable:` configuration.",
                    remediation="Pass `refreshListenable: authStateNotifier` backed by `ref.listen(authControllerProvider, ...)` to `GoRouter(...)`.",
                    severity=GuardrailSeverity.FATAL,
                    is_suppressed=False,
                )
            )

    return violations


def _check_dgr014_build_method_body(
    filepath: str,
    source_text: str,
    build_body: str,
    body_start: int,
) -> list[DartViolation]:
    """Evaluate DGR014 Check 14B top-level ref.read(...) usage inside a Widget build(...) body.

    Args:
        filepath: Target file path being scanned.
        source_text: Original decoded UTF-8 source text.
        build_body: Extracted brace-enclosed body of the build method.
        body_start: Character offset of build_body within source_text.

    Returns:
        List of DGR014 DartViolation instances for top-level ref.read calls in build().
    """
    violations: list[DartViolation] = []
    for read_match in _DGR014_REF_READ_CALL_PATTERN.finditer(build_body):
        read_arg = read_match.group(1)
        if ".notifier" in read_arg or "loggerServiceProvider" in read_arg:
            continue
        prefix = build_body[: read_match.start()]
        brace_depth = prefix.count("{") - prefix.count("}")
        last_statement = prefix.rsplit(";", maxsplit=1)[-1]
        if brace_depth == 1 and "=>" not in last_statement:
            lineno, col_offset = _offset_to_line_col(source_text, body_start + read_match.start())
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=col_offset,
                    rule_code="DGR014",
                    message=(
                        "Banned `ref.read(...)` inside `Widget build(...)`; reactive state in `build()` "
                        "must use `ref.watch(...)` (`riverpod_read_vs_watch_ban`)."
                    ),
                    remediation=(
                        "Replace `ref.read(provider)` with `ref.watch(provider)` inside `build()`, and "
                        "reserve `ref.read` for event callbacks (`onPressed`)."
                    ),
                    severity=GuardrailSeverity.FATAL,
                    is_suppressed=False,
                )
            )
    return violations


def _check_freezed_and_riverpod_rules(
    filepath: str,
    source_text: str,
    uncommented_text: str,
    *,
    is_test_scope: bool,
) -> list[DartViolation]:
    """Evaluate DGR013 (freezed_when_ban) and DGR014 (Riverpod 3.1 provider & ref rules) across Dart source.

    Args:
        filepath: Target file path being scanned.
        source_text: Original decoded UTF-8 source text.
        uncommented_text: Source text with comments replaced by spaces preserving line breaks.
        is_test_scope: Whether the file resides in a test directory.

    Returns:
        List of DartViolation instances for DGR013 and DGR014.
    """
    if is_test_scope:
        return []

    violations: list[DartViolation] = []

    for when_match in DGR013_FREEZED_WHEN_PATTERN.finditer(uncommented_text):
        lineno, col_offset = _offset_to_line_col(source_text, when_match.start())
        violations.append(
            DartViolation(
                filepath=filepath,
                lineno=lineno,
                col_offset=col_offset,
                rule_code="DGR013",
                message=(
                    "Banned Freezed/AsyncValue `.when()` / `.maybeWhen()` / `.map()` chain detected "
                    "(`freezed_when_ban`)."
                ),
                remediation=(
                    "Use Dart 3 native `switch` expressions with pattern matching destructuring "
                    "(`switch (state) { AsyncData(:final value) => ..., AsyncLoading() => ... }`)."
                ),
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        )

    for legacy_match in DGR014_LEGACY_PROVIDER_PATTERN.finditer(uncommented_text):
        lineno, col_offset = _offset_to_line_col(source_text, legacy_match.start())
        violations.append(
            DartViolation(
                filepath=filepath,
                lineno=lineno,
                col_offset=col_offset,
                rule_code="DGR014",
                message=(
                    f"Banned legacy manual provider or notifier `{legacy_match.group(0)}` detected "
                    "(`manual_riverpod_providers`)."
                ),
                remediation=(
                    "Use `@riverpod` code generation (`Notifier` / `AsyncNotifier`) for all "
                    "Riverpod 3.1 state providers."
                ),
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        )

    for build_match in _WIDGET_BUILD_HEADER_PATTERN.finditer(uncommented_text):
        body_start = build_match.end() - 1
        build_body = _extract_brace_block(uncommented_text, body_start)
        violations.extend(_check_dgr014_build_method_body(filepath, source_text, build_body, body_start))

    for cb_match in DGR014_CALLBACK_REF_WATCH_PATTERN.finditer(uncommented_text):
        watch_pos = cb_match.group(0).rfind("ref")
        offset = cb_match.start() + max(0, watch_pos)
        lineno, col_offset = _offset_to_line_col(source_text, offset)
        violations.append(
            DartViolation(
                filepath=filepath,
                lineno=lineno,
                col_offset=col_offset,
                rule_code="DGR014",
                message="Banned `ref.watch(...)` inside UI event callback (`riverpod_read_vs_watch_ban`).",
                remediation=(
                    "Use `ref.read(provider)` or `ref.read(provider.notifier)` for one-time execution "
                    "inside UI event callbacks (`onPressed`)."
                ),
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        )

    return violations


def _check_master_view_error_boundary(
    filepath: str,
    normalized_path: str,
    path_parts: set[str],
    source_text: str,
    uncommented_text: str,
    default_severity: GuardrailSeverity,
) -> list[DartViolation]:
    """Verify DGR009 mandatory AppErrorBoundary wrapping on feature master views.

    Args:
        filepath: Target file path being scanned.
        normalized_path: Forward-slash normalized file path.
        path_parts: Set of path directory segments.
        source_text: Decoded UTF-8 source text of the Dart file.
        uncommented_text: Comment-stripped Dart source text.
        default_severity: Default severity tier (WARNING or FATAL when strict).

    Returns:
        Single-element list containing a DGR009 violation if missing, or empty list.
    """
    is_master_view_file = (
        "features" in path_parts
        and "test" not in path_parts
        and (
            "master_view" in normalized_path.lower() or bool(re.search(r"\bclass\s+\w*MasterView\b", uncommented_text))
        )
    )
    if is_master_view_file and "AppErrorBoundary" not in uncommented_text:
        match = re.search(r"\bclass\s+\w*MasterView\b", uncommented_text)
        if match:
            class_lineno, col_offset = _offset_to_line_col(source_text, match.start())
        else:
            class_lineno, col_offset = 1, 0
        return [
            DartViolation(
                filepath=filepath,
                lineno=class_lineno,
                col_offset=col_offset,
                rule_code="DGR009",
                message="Feature master view is missing mandatory AppErrorBoundary wrapping.",
                remediation="Wrap the root body or view content in an AppErrorBoundary widget to isolate unexpected UI crashes.",
                severity=default_severity,
                is_suppressed=False,
            )
        ]
    return []


def scan_dart_source(filepath: str, source_bytes: bytes, strict: bool = False) -> list[DartViolation]:
    """Scan Dart source code bytes for architectural violations across single and multi-line constructs.

    Args:
        filepath: File path string associated with the source bytes.
        source_bytes: Raw file bytes to decode and inspect.
        strict: Whether to escalate warning-level violations to FATAL severity.

    Returns:
        List of detected DartViolation instances ordered by line and column.
    """
    try:
        source_text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [
            DartViolation(
                filepath=filepath,
                lineno=1,
                col_offset=0,
                rule_code="DGR000",
                message=f"Fatal encoding error reading Dart file: {exc}",
                remediation="Ensure file is valid UTF-8 encoded text.",
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        ]

    if is_generated_dart_file(filepath, source_text):
        return []

    violations: list[DartViolation] = []
    normalized_path = filepath.replace("\\", "/").strip("/")
    path_parts = set(normalized_path.split("/"))

    is_api_or_model_scope = (
        "api" in path_parts
        or "models" in path_parts
        or "controllers" in path_parts
        or "providers" in path_parts
        or "data" in path_parts
        or "repositories" in path_parts
        or "network" in path_parts
        or "core/api" in normalized_path
    )
    is_test_scope = "test" in path_parts or "bin" in path_parts
    is_theme_scope = "theme" in path_parts or Path(filepath).name.lower() == "app_colors.dart"
    is_ui_scope = not is_test_scope and not is_theme_scope
    is_feature_widget_scope = is_ui_scope
    default_severity = GuardrailSeverity.FATAL if strict else GuardrailSeverity.WARNING

    # DGR004 scans raw lines specifically to catch // ignore: and // ignore_for_file: comments and plan breadcrumbs
    for lineno, line in enumerate(source_text.splitlines(), start=1):
        dgr004_match = DGR004_PATTERN.search(line)
        if dgr004_match:
            violations.append(
                DartViolation(
                    filepath=filepath,
                    lineno=lineno,
                    col_offset=dgr004_match.start(),
                    rule_code="DGR004",
                    message="Banned Dart lint suppression comment detected in handwritten code.",
                    remediation="Resolve the underlying static analysis warning instead of using `// ignore:` or `// ignore_for_file:`.",
                    severity=GuardrailSeverity.FATAL,
                    is_suppressed=False,
                )
            )
        if not is_test_scope:
            breadcrumb_match = DGR004_PLAN_BREADCRUMB_PATTERN.search(line)
            if breadcrumb_match:
                violations.append(
                    DartViolation(
                        filepath=filepath,
                        lineno=lineno,
                        col_offset=breadcrumb_match.start(),
                        rule_code="DGR004",
                        message=(
                            f"Banned implementation plan/phase/step breadcrumb `{breadcrumb_match.group(0).strip()}` "
                            "detected in comment (`documentation_and_hygiene`)."
                        ),
                        remediation=(
                            "Remove plan/phase/step/REQ tracking markers from comments. "
                            "Describe current functionality and WHY business logic exists in timeless present-tense English."
                        ),
                        severity=GuardrailSeverity.FATAL,
                        is_suppressed=False,
                    )
                )

    uncommented_text = _strip_dart_comments(source_text)

    violations.extend(
        _check_api_and_codec_multiline_rules(
            filepath,
            source_text,
            uncommented_text,
            is_api_or_model_scope=is_api_or_model_scope,
            is_test_scope=is_test_scope,
        )
    )
    violations.extend(
        _check_ui_and_feature_multiline_rules(
            filepath,
            source_text,
            uncommented_text,
            is_ui_scope=is_ui_scope,
            is_feature_widget_scope=is_feature_widget_scope,
            is_theme_scope=is_theme_scope,
            is_test_scope=is_test_scope,
            default_severity=default_severity,
        )
    )
    violations.extend(
        _check_master_view_error_boundary(
            filepath,
            normalized_path,
            path_parts,
            source_text,
            uncommented_text,
            default_severity,
        )
    )
    violations.extend(
        _check_hook_and_router_lifecycle_rules(
            filepath,
            source_text,
            uncommented_text,
            is_test_scope=is_test_scope,
        )
    )
    violations.extend(
        _check_freezed_and_riverpod_rules(
            filepath,
            source_text,
            uncommented_text,
            is_test_scope=is_test_scope,
        )
    )

    violations.sort(key=lambda v: (v.lineno, v.col_offset, v.rule_code))
    return violations


def scan_dart_file(filepath: Path, strict: bool = False) -> list[DartViolation]:
    """Scan a single Dart file on disk for architectural violations.

    Args:
        filepath: Path to the target Dart file on disk.
        strict: Whether to escalate warning-level violations to FATAL severity.

    Returns:
        List of detected DartViolation instances (including DGR000 on read failure).
    """
    if not filepath.exists():
        return [
            DartViolation(
                filepath=str(filepath),
                lineno=1,
                col_offset=0,
                rule_code="DGR000",
                message=f"Fatal read error: File not found `{filepath}`",
                remediation="Verify that the target path exists.",
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        ]

    try:
        source_bytes = filepath.read_bytes()
    except OSError as exc:
        return [
            DartViolation(
                filepath=str(filepath),
                lineno=1,
                col_offset=0,
                rule_code="DGR000",
                message=f"Fatal OS read error: {exc}",
                remediation="Check file permissions and disk availability.",
                severity=GuardrailSeverity.FATAL,
                is_suppressed=False,
            )
        ]

    return scan_dart_source(str(filepath), source_bytes, strict=strict)


def scan_dart_files(filepaths: Sequence[Path], strict: bool = False) -> list[DartViolation]:
    """Scan multiple Dart files or directories recursively for architectural violations.

    Args:
        filepaths: Sequence of file or directory Paths to scan.
        strict: Whether to escalate warning-level violations to FATAL severity.

    Returns:
        Aggregated list of detected DartViolation instances across all targets.
    """
    all_violations: list[DartViolation] = []
    for fp in filepaths:
        if fp.is_dir():
            for child in fp.rglob("*.dart"):
                if child.is_file():
                    all_violations.extend(scan_dart_file(child, strict=strict))
        elif fp.is_file() and fp.suffix == ".dart":
            all_violations.extend(scan_dart_file(fp, strict=strict))
    return all_violations


def format_dart_violations_table(violations: Sequence[DartViolation]) -> str:
    """Format Dart guardrail violations into a structured ASCII table.

    Args:
        violations: Sequence of DartViolation objects to format.

    Returns:
        Formatted ASCII table string or clean status message if empty.
    """
    if not violations:
        return "No Dart guardrail violations found."

    headers = ("Severity", "Rule", "File:Line:Col", "Message")
    rows: list[tuple[str, str, str, str]] = []
    for v in violations:
        loc = f"{v.filepath}:{v.lineno}:{v.col_offset}"
        rows.append((v.severity.value, v.rule_code, loc, v.message))

    col_widths = [max(len(headers[i]), max((len(r[i]) for r in rows), default=0)) for i in range(4)]

    header_line = " | ".join(headers[i].ljust(col_widths[i]) for i in range(4))
    separator_line = "-+-".join("-" * col_widths[i] for i in range(4))
    body_lines = [" | ".join(row[i].ljust(col_widths[i]) for i in range(4)) for row in rows]

    return "\n".join([header_line, separator_line] + body_lines)


def main(argv: list[str] | None = None) -> int:
    """Execute the CLI entry point for the Dart guardrail engine.

    Args:
        argv: Optional list of command-line arguments.

    Returns:
        Exit code 0 if no fatal violations (or warnings under --strict) were found, 1 otherwise.
    """
    parser = argparse.ArgumentParser(
        description="""Client-Side Static Dart Guardrail Analyzer (DGR001-DGR014).

Enforces Flutter client architecture and static type safety invariants across full multi-line source:
  DGR001: Loose Map return types in API clients, models, controllers, data, repositories, or providers (FATAL)
  DGR002: SizedBox.shrink() concealment across all non-test, non-theme lib/ files (WARNING)
  DGR003: Raw hardcoded string literals in Text widgets across all non-test, non-theme lib/ files (WARNING)
  DGR004: Dart lint suppressions across lib/ and test/ (FATAL)
  DGR005: Non-codec Map<String, dynamic> or unexempted Map<String, Object?> in handwritten Dart code (FATAL)
  DGR006: Anonymous Map literals in HTTP request payloads (FATAL)
  DGR007: Banned hardcoded hex colors or direct Colors.* calls across all non-test, non-theme lib/ files (WARNING)
  DGR008: Banned manual string clippings via .substring() and legacy Uuid().v4() (WARNING)
  DGR009: Missing AppErrorBoundary wrapping on feature master views (WARNING)
  DGR010: Missing AsyncValue guards on dynamic AsyncNotifierProvider consumers (WARNING)
  DGR011: Banned deprecated useIsMounted() and unguarded post-await hook ValueNotifier mutations (FATAL)
  DGR012: Banned direct ref.watch(...) inside GoRouter provider and missing refreshListenable (FATAL)
  DGR013: Banned Freezed/AsyncValue .when() / .maybeWhen() / .maybeMap() / .map(data: ...) chains (FATAL)
  DGR014: Banned manual StateProvider/ChangeNotifier, ref.read in build(), and ref.watch in callbacks (FATAL)

Immunity: Generated files (*.g.dart, *.freezed.dart) are automatically exempted.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples (PowerShell):
  uv run python scripts/_dart_guardrails.py client_app_v2
  uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/studio/ --strict
  uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/execution/models/
""",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=["client_app_v2"],
        help="Target Dart files or directories to scan (default: client_app_v2).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat all violations (including warnings) as FATAL and return exit code 1.",
    )
    args = parser.parse_args(argv)

    target_paths = [Path(t) for t in args.targets]
    violations = scan_dart_files(target_paths, strict=args.strict)

    fatal_violations = [v for v in violations if v.severity == GuardrailSeverity.FATAL]
    warning_violations = [v for v in violations if v.severity == GuardrailSeverity.WARNING]

    if violations:
        print(format_dart_violations_table(violations))
        print(
            f"\nTotal Dart Violations: {len(violations)} "
            f"({len(fatal_violations)} FATAL, {len(warning_violations)} WARNING)"
        )
    else:
        print("All Dart guardrail checks passed cleanly! (0 violations)")

    if fatal_violations or (args.strict and violations):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
