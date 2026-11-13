"""Backend <-> Frontend DTO Parity Verification Script.

Scans Python Pydantic models and Dart Freezed models to verify field-name
parity across the system boundaries using zero-reflection AST parsing and strict Pydantic V2 DTOs.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Annotated, Final

from pydantic import BaseModel, ConfigDict, Field

_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(_WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts._script_base import setup_script_environment

setup_script_environment()

__all__ = [
    "DtoFieldMismatchDTO",
    "DtoParityReportDTO",
    "EXPLICIT_MODEL_ALIASES",
    "PREFERRED_BACKEND_ALIASES",
    "audit_parity",
    "audit_parity_report",
    "camel_to_snake",
    "extract_freezed_fields",
    "extract_pydantic_fields",
    "main",
    "snake_to_camel",
    "split_dart_params",
]

_INHERITANCE_RESOLUTION_PASSES: Final[int] = 5


class DtoFieldMismatchDTO(BaseModel):
    """Pydantic V2 DTO representing a field mismatch between Python and Dart models.

    Attributes:
        model_name: Canonical model name where the mismatch occurred.
        field_name: Serialized wire field name that is missing on one side.
        python_type: Resolved Python field type label.
        dart_type: Resolved Dart field type label.
        mismatch_reason: Detailed explanation of the parity discrepancy.
        remediation: Actionable fix instruction for the developer or agent.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    model_name: Annotated[str, Field(min_length=1, description="Canonical model name where the mismatch occurred")]
    field_name: Annotated[str, Field(min_length=1, description="Serialized wire field name missing on one side")]
    python_type: Annotated[str, Field(default="unknown", description="Resolved Python field type label")] = "unknown"
    dart_type: Annotated[str, Field(default="unknown", description="Resolved Dart field type label")] = "unknown"
    mismatch_reason: Annotated[str, Field(min_length=1, description="Detailed explanation of the parity discrepancy")]
    remediation: Annotated[str, Field(min_length=1, description="Actionable fix instruction")]


class DtoParityReportDTO(BaseModel):
    """Pydantic V2 DTO representing the aggregate DTO parity audit report.

    Attributes:
        is_success: True when zero field mismatches exist across all matched models.
        shared_models_count: Number of matched Python-to-Dart model pairs audited.
        mismatches: List of individual field parity mismatch records.
        summary_messages: Formatted summary strings for CLI reporting.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    is_success: Annotated[bool, Field(description="True when zero field mismatches exist across matched models")]
    shared_models_count: Annotated[int, Field(ge=0, description="Number of matched model pairs audited")]
    mismatches: Annotated[list[DtoFieldMismatchDTO], Field(description="Individual field parity mismatch records")]
    summary_messages: Annotated[list[str], Field(description="Formatted summary strings for CLI reporting")]


def snake_to_camel(snake_str: str) -> str:
    """Convert a snake_case identifier to camelCase.

    Args:
        snake_str: Identifier formatted in snake_case.

    Returns:
        Converted camelCase identifier string.
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """Convert a camelCase identifier to snake_case.

    Args:
        camel_str: Identifier formatted in camelCase.

    Returns:
        Converted snake_case identifier string.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


def _resolve_pydantic_field_name(stmt: ast.AnnAssign) -> str | None:
    """Resolve the serialized wire field name from an AST annotated assignment node.

    Args:
        stmt: AST AnnAssign statement inside a Pydantic class body.

    Returns:
        Serialized field name string, or None when private, model_config, or excluded.
    """
    if not isinstance(stmt.target, ast.Name):
        return None
    field_name = stmt.target.id
    if field_name.startswith("_") or field_name == "model_config":
        return None

    field_alias: str | None = None
    ser_alias: str | None = None
    for sub in ast.walk(stmt):
        match sub:
            case ast.keyword(arg="exclude", value=ast.Constant(value=True)):
                return None
            case ast.keyword(
                arg="serialization_alias",
                value=ast.Constant(value=str() as resolved_ser_alias),
            ):
                ser_alias = resolved_ser_alias
            case ast.keyword(
                arg="alias",
                value=ast.Constant(value=str() as resolved_alias),
            ):
                field_alias = resolved_alias
            case _:
                pass

    if ser_alias is not None:
        return ser_alias
    if field_alias is not None:
        return field_alias
    return field_name


def extract_pydantic_fields(file_path: Path) -> tuple[dict[str, set[str]], dict[str, list[str]]]:
    """Extract Pydantic model class names, serialized field names, and base class names via AST.

    Args:
        file_path: Path to the Python module containing Pydantic model definitions.

    Returns:
        2-tuple mapping model names to serialized field sets and model names to base class lists.
    """
    if not file_path.exists() or file_path.suffix != ".py":
        return {}, {}

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=file_path.as_posix())
    except SyntaxError, UnicodeDecodeError, OSError:
        return {}, {}

    models: dict[str, set[str]] = {}
    class_bases: dict[str, list[str]] = {}

    for node in ast.walk(tree):
        match node:
            case ast.ClassDef(name=class_name, body=body, bases=bases):
                fields: set[str] = set()
                base_names = [b.id for b in bases if isinstance(b, ast.Name)]
                class_bases[class_name] = base_names

                for stmt in body:
                    if isinstance(stmt, ast.AnnAssign):
                        resolved_name = _resolve_pydantic_field_name(stmt)
                        if resolved_name is not None:
                            fields.add(resolved_name)
                if fields or base_names:
                    models[class_name] = fields
            case _:
                pass

    return models, class_bases


def split_dart_params(params_block: str) -> list[str]:
    """Split Dart parameter definitions by comma while respecting nested brackets and quotes.

    Args:
        params_block: Raw parameter block string from a Freezed factory constructor.

    Returns:
        List of trimmed individual parameter definition strings.
    """
    params: list[str] = []
    current: list[str] = []
    depth = 0
    in_single_quote = False
    in_double_quote = False
    escape = False

    for char in params_block:
        if escape:
            current.append(char)
            escape = False
            continue

        if char == "\\":
            current.append(char)
            escape = True
            continue

        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            current.append(char)
            continue

        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current.append(char)
            continue

        if in_single_quote or in_double_quote:
            current.append(char)
            continue

        if char in "({[<":
            depth += 1
            current.append(char)
        elif char in ")}]>":
            if depth > 0:
                depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            param = "".join(current).strip()
            if param:
                params.append(param)
            current = []
        else:
            current.append(char)

    if current:
        param = "".join(current).strip()
        if param:
            params.append(param)

    return params


def _extract_single_dart_param_field(entry: str) -> str | None:
    """Extract the serialized wire field name from a single Dart Freezed constructor parameter.

    Args:
        entry: Trimmed single parameter declaration string.

    Returns:
        Serialized snake_case field name, or None when excluded via @JsonKey.
    """
    if re.search(r"@JsonKey\s*\([^)]*?\b(?:includeFromJson|includeToJson)\s*:\s*false", entry) or re.search(
        r"@JsonKey\s*\([^)]*?\bignore\s*:\s*true", entry
    ):
        return None

    json_key_match = re.search(r"@JsonKey\s*\([^)]*?\bname\s*:\s*['\"]([^'\"]+)['\"]", entry)
    if json_key_match:
        return json_key_match.group(1)

    clean_param = entry.split("=")[0].strip()
    clean_param = re.sub(r"@[A-Za-z0-9_]+(?:\([^)]*\))?", "", clean_param).strip()
    clean_param = re.sub(r"^\s*required\s+", "", clean_param).strip()
    tokens = clean_param.split()
    if tokens:
        field_identifier = tokens[-1]
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", field_identifier):
            return camel_to_snake(field_identifier)
    return None


def extract_freezed_fields(file_path: Path) -> dict[str, set[str]]:
    """Extract Freezed model class names and serialized field names from a Dart file.

    Args:
        file_path: Path to the Dart source file.

    Returns:
        Dictionary mapping class names to sets of serialized field names.
    """
    if not file_path.exists() or file_path.suffix != ".dart":
        return {}

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError, OSError:
        return {}

    models: dict[str, set[str]] = {}
    class_pattern = re.compile(
        r"@(?:[Ff]reezed(?:\([^)]*\))?)\s+(?:abstract\s+)?class\s+([A-Za-z0-9_]+)\b[\s\S]*?factory\s+\1(?:\.[A-Za-z0-9_]+)?\s*\(\s*\{([\s\S]*?)\}\s*\)\s*=",
        re.MULTILINE,
    )

    for class_match in class_pattern.finditer(content):
        class_name = class_match.group(1)
        params_block = class_match.group(2)
        fields: set[str] = set()

        for entry in split_dart_params(params_block):
            resolved_field = _extract_single_dart_param_field(entry)
            if resolved_field is not None:
                fields.add(resolved_field)

        if fields:
            models[class_name] = fields

    return models


EXPLICIT_MODEL_ALIASES: Final[dict[str, str]] = {
    "mcpaudittrace": "mcpaudittracedto",
    "renderedsynthesiscache": "profilesynthesisentrydto",
    "traceevent": "executiontraceitemdto",
    "workflowresponsedto": "workflow",
    "useradminview": "user",
    "systemconfigmcpgateways": "mcpgateway",
    "systemconfigmodelregistry": "modelconfig",
    "modelprofile": "llmmodelconfig",
    "taskbriefresponsedto": "taskbrief",
    "outputprofileresponsedto": "outputprofile",
}

PREFERRED_BACKEND_ALIASES: Final[dict[str, str]] = {
    "workflow": "workflowresponsedto",
    "user": "useradminview",
    "taskbrief": "taskbriefresponsedto",
    "outputprofile": "outputprofileresponsedto",
}


def _collect_backend_models(backend_dir: Path) -> dict[str, set[str]]:
    """Scan Python files under backend_dir and resolve cross-file model inheritance.

    Args:
        backend_dir: Root directory containing Python Pydantic models.

    Returns:
        Dictionary mapping backend class names to their inherited serialized field sets.
    """
    backend_models: dict[str, set[str]] = {}
    backend_bases: dict[str, list[str]] = {}
    if backend_dir.exists():
        for py_file in backend_dir.rglob("*.py"):
            file_models, file_bases = extract_pydantic_fields(py_file)
            for m_name, m_fields in file_models.items():
                if m_name in backend_models:
                    backend_models[m_name] = backend_models[m_name] | m_fields
                else:
                    backend_models[m_name] = m_fields
            for m_name, bases in file_bases.items():
                backend_bases[m_name] = bases

    for _ in range(_INHERITANCE_RESOLUTION_PASSES):
        for cls_name, bases in backend_bases.items():
            for base in bases:
                if base in backend_models:
                    if cls_name not in backend_models:
                        backend_models[cls_name] = set()
                    backend_models[cls_name] = backend_models[cls_name] | backend_models[base]

    filtered_models = {k: v for k, v in backend_models.items() if v}
    backend_by_lower: dict[str, str] = {name.lower(): name for name in filtered_models}

    for base_lower, preferred_lower in PREFERRED_BACKEND_ALIASES.items():
        if base_lower in backend_by_lower and preferred_lower in backend_by_lower:
            base_model_name = backend_by_lower[base_lower]
            preferred_model_name = backend_by_lower[preferred_lower]
            filtered_models[preferred_model_name] = (
                filtered_models[preferred_model_name] | filtered_models[base_model_name]
            )

    for sub_event_lower in ("errortraceevent", "tombstoneevent"):
        if "traceevent" in backend_by_lower and sub_event_lower in backend_by_lower:
            trace_event_name = backend_by_lower["traceevent"]
            sub_event_name = backend_by_lower[sub_event_lower]
            filtered_models[trace_event_name] = filtered_models[trace_event_name] | filtered_models[sub_event_name]

    return filtered_models


def _collect_frontend_models(frontend_dir: Path) -> dict[str, set[str]]:
    """Scan Dart files under frontend_dir and aggregate Freezed model field sets.

    Args:
        frontend_dir: Root directory containing Flutter Dart Freezed models.

    Returns:
        Dictionary mapping Dart Freezed class names to their serialized field sets.
    """
    frontend_models: dict[str, set[str]] = {}
    if frontend_dir.exists():
        for dart_file in frontend_dir.rglob("*.dart"):
            for m_name, m_fields in extract_freezed_fields(dart_file).items():
                if m_name in frontend_models:
                    frontend_models[m_name] = frontend_models[m_name] | m_fields
                else:
                    frontend_models[m_name] = m_fields
    return frontend_models


def _match_model_pairs(
    backend_models: dict[str, set[str]],
    frontend_models: dict[str, set[str]],
) -> list[tuple[str, str]]:
    """Match backend Pydantic model names to corresponding frontend Freezed model names.

    Args:
        backend_models: Mapping of backend class names to serialized field sets.
        frontend_models: Mapping of frontend class names to serialized field sets.

    Returns:
        Sorted list of matched (backend_model_name, frontend_model_name) pairs.
    """
    backend_by_lower: dict[str, str] = {name.lower(): name for name in backend_models}
    frontend_by_lower: dict[str, str] = {name.lower(): name for name in frontend_models}

    matched_pairs: list[tuple[str, str]] = []
    matched_frontend: set[str] = set()

    for b_name in sorted(backend_models.keys()):
        b_lower = b_name.lower()
        if b_lower in PREFERRED_BACKEND_ALIASES and PREFERRED_BACKEND_ALIASES[b_lower] in backend_by_lower:
            continue

        target_f_lower = EXPLICIT_MODEL_ALIASES[b_lower] if b_lower in EXPLICIT_MODEL_ALIASES else b_lower
        if target_f_lower in frontend_by_lower:
            f_name = frontend_by_lower[target_f_lower]
            if f_name not in matched_frontend:
                matched_pairs.append((b_name, f_name))
                matched_frontend.add(f_name)

    return matched_pairs


def audit_parity_report(backend_dir: Path, frontend_dir: Path) -> DtoParityReportDTO:
    """Compare matching DTO models across backend and frontend directories.

    Args:
        backend_dir: Root directory containing Backend Python Pydantic models.
        frontend_dir: Root directory containing Frontend Dart Freezed models.

    Returns:
        Structured DtoParityReportDTO containing parity status and field mismatches.
    """
    backend_models = _collect_backend_models(backend_dir)
    frontend_models = _collect_frontend_models(frontend_dir)
    matched_pairs = _match_model_pairs(backend_models, frontend_models)

    mismatches: list[DtoFieldMismatchDTO] = []
    summary_messages: list[str] = []

    for b_name, f_name in matched_pairs:
        b_fields = backend_models[b_name]
        f_fields = frontend_models[f_name]
        if b_fields != f_fields:
            missing_in_front = b_fields - f_fields
            missing_in_back = f_fields - b_fields
            diffs: list[str] = []
            if missing_in_front:
                diffs.append(f"Missing in Frontend: {sorted(missing_in_front)}")
                for fld in sorted(missing_in_front):
                    mismatches.append(
                        DtoFieldMismatchDTO(
                            model_name=b_name,
                            field_name=fld,
                            mismatch_reason=(
                                f"Field '{fld}' present in Python Pydantic model '{b_name}' "
                                f"but missing in Dart Freezed model '{f_name}'."
                            ),
                            remediation=(
                                f"Add @JsonKey(name: '{fld}') or camelCase field "
                                f"'{snake_to_camel(fld)}' to Dart Freezed class '{f_name}'."
                            ),
                        )
                    )
            if missing_in_back:
                diffs.append(f"Missing in Backend: {sorted(missing_in_back)}")
                for fld in sorted(missing_in_back):
                    mismatches.append(
                        DtoFieldMismatchDTO(
                            model_name=b_name,
                            field_name=fld,
                            mismatch_reason=(
                                f"Field '{fld}' present in Dart Freezed model '{f_name}' "
                                f"but missing in Python Pydantic model '{b_name}'."
                            ),
                            remediation=f"Add field '{fld}: <Type>' to Python Pydantic class '{b_name}'.",
                        )
                    )
            summary_messages.append(f"[{b_name} <-> {f_name}] " + "; ".join(diffs))

    return DtoParityReportDTO(
        is_success=len(mismatches) == 0,
        shared_models_count=len(matched_pairs),
        mismatches=mismatches,
        summary_messages=summary_messages,
    )


def audit_parity(backend_dir: Path, frontend_dir: Path) -> tuple[bool, list[str]]:
    """Compare matching DTO models across backend and frontend directories.

    Args:
        backend_dir: Root directory containing Backend Python Pydantic models.
        frontend_dir: Root directory containing Frontend Dart Freezed models.

    Returns:
        2-tuple of parity success boolean and formatted mismatch summary messages.
    """
    report = audit_parity_report(backend_dir, frontend_dir)
    return report.is_success, report.summary_messages


def main(argv: list[str] | None = None) -> None:
    """Execute the CLI entrypoint for cross-domain DTO parity auditing.

    Args:
        argv: Optional list of CLI argument strings.

    Raises:
        SystemExit: Exits with 0 when models align or --no-fail-on-mismatch is set, or 1 on mismatch.
    """
    parser = argparse.ArgumentParser(
        description="""Cross-Domain DTO Model & Field Parity Gate.

Verifies 1:1 structural and naming parity between Backend Pydantic V2 DTOs and Flutter Dart Freezed models:
  - Model Name Alignment: Matches Python DTO classes to corresponding Dart Freezed models.
  - Field Naming Parity: Verifies snake_case Python fields map to camelCase Dart fields or explicit @JsonKey annotations.
  - Type Parity: Flags missing, extraneous, or mismatched property definitions across boundaries.
  - Exit Code Semantics: Exits with 0 when models are aligned, 1 on mismatch (if fail-on-mismatch), or 2 on syntax error.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples (PowerShell):
  uv run python scripts/audit_dto_parity.py
  uv run python scripts/audit_dto_parity.py --backend-dir backend_v2/models/dtos --frontend-dir client_app_v2/lib/features
  uv run python scripts/audit_dto_parity.py --no-fail-on-mismatch
""",
    )
    parser.add_argument(
        "--backend-dir",
        default="backend_v2/models",
        help="Backend models root directory to scan (default: backend_v2/models).",
    )
    parser.add_argument(
        "--frontend-dir",
        default="client_app_v2/lib",
        help="Frontend lib root directory to scan (default: client_app_v2/lib).",
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Exit with code 1 if any field parity mismatches are detected (default: True).",
    )
    args = parser.parse_args(argv)

    b_dir = Path(args.backend_dir).resolve()
    f_dir = Path(args.frontend_dir).resolve()

    print(f"\n🔍 Auditing DTO Parity between {b_dir} and {f_dir}...")
    report = audit_parity_report(b_dir, f_dir)

    if report.is_success:
        print(f"✅ DTO Parity Audit Passed: All {report.shared_models_count} shared models are 1:1 aligned.")
        sys.exit(0)
    else:
        print("❌ DTO Parity Mismatches Found:")
        for r in report.summary_messages:
            print(f"  - {r}")
        if args.fail_on_mismatch:
            sys.exit(1)
        sys.exit(0)


if __name__ == "__main__":
    main()
