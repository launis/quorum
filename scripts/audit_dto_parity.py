"""Backend <-> Frontend DTO Parity Verification Script.

Scans Python Pydantic models and Dart Freezed models to verify field-name
parity across the system boundaries using zero-reflection AST parsing and strict Pydantic V2 DTOs.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import sys
from pathlib import Path

from pydantic import BaseModel, ConfigDict

# Force UTF-8 encoding for stdout/stderr to support emojis on Windows
try:
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    if sys.stderr is not None:
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
except AttributeError, io.UnsupportedOperation:
    pass


class DtoFieldMismatchDTO(BaseModel):
    """Pydantic V2 DTO representing a field mismatch between Python and Dart models."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    model_name: str
    field_name: str
    python_type: str = "unknown"
    dart_type: str = "unknown"
    mismatch_reason: str
    remediation: str


class DtoParityReportDTO(BaseModel):
    """Pydantic V2 DTO representing the aggregate DTO parity audit report."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    is_success: bool
    shared_models_count: int
    mismatches: list[DtoFieldMismatchDTO]
    summary_messages: list[str]


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case identifier to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase identifier to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


def extract_pydantic_fields(file_path: Path) -> tuple[dict[str, set[str]], dict[str, list[str]]]:
    """Extract Pydantic model class names, field names, and base class names via zero-reflection Python AST."""
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
                    match stmt:
                        case ast.AnnAssign(target=ast.Name(id=field_name)):
                            if not field_name.startswith("_") and field_name != "model_config":
                                is_excluded = False
                                for sub in ast.walk(stmt):
                                    match sub:
                                        case ast.keyword(arg="exclude", value=ast.Constant(value=True)):
                                            is_excluded = True
                                            break
                                        case _:
                                            pass
                                if not is_excluded:
                                    fields.add(field_name)
                        case _:
                            pass
                if fields or base_names:
                    models[class_name] = fields
            case _:
                pass

    return models, class_bases


def split_dart_params(params_block: str) -> list[str]:
    """Split Dart parameter definitions by comma while respecting nested brackets and quotes.

    Args:
        params_block: The raw parameter block string from a Freezed factory constructor.

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

        # Split parameter definitions by comma respecting nested parenthesis/brackets
        param_entries = split_dart_params(params_block)
        for entry in param_entries:
            # Check for @JsonKey exclusion flags (mirroring Python Field(exclude=True))
            if re.search(r"@JsonKey\s*\([^)]*?\b(?:includeFromJson|includeToJson)\s*:\s*false", entry) or re.search(
                r"@JsonKey\s*\([^)]*?\bignore\s*:\s*true", entry
            ):
                continue

            # Check for @JsonKey(name: '...')
            json_key_match = re.search(r"@JsonKey\s*\([^)]*?\bname\s*:\s*['\"]([^'\"]+)['\"]", entry)
            if json_key_match:
                fields.add(json_key_match.group(1))
            else:
                # Remove default value assignment if any
                clean_param = entry.split("=")[0].strip()
                # Remove annotations
                clean_param = re.sub(r"@[A-Za-z0-9_]+(?:\([^)]*\))?", "", clean_param).strip()
                # Remove only leading 'required' modifier, preserving parameter identifier if named 'required'
                clean_param = re.sub(r"^\s*required\s+", "", clean_param).strip()
                # Field name is the last token
                tokens = clean_param.split()
                if tokens:
                    field_identifier = tokens[-1]
                    if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", field_identifier):
                        fields.add(camel_to_snake(field_identifier))

        if fields:
            models[class_name] = fields

    return models


EXPLICIT_MODEL_ALIASES: dict[str, str] = {
    "mcpaudittrace": "mcpaudittracedto",
    "workflowresponsedto": "workflow",
    "useradminview": "user",
}

PREFERRED_BACKEND_ALIASES: dict[str, str] = {
    "workflow": "workflowresponsedto",
    "user": "useradminview",
}


def audit_parity_report(backend_dir: Path, frontend_dir: Path) -> DtoParityReportDTO:
    """Compare matching DTO models across backend and frontend directories, returning DtoParityReportDTO."""
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

    # Multi-pass cross-file inheritance resolution for backend models
    for _ in range(5):
        for cls_name, bases in backend_bases.items():
            for base in bases:
                if base in backend_models:
                    if cls_name not in backend_models:
                        backend_models[cls_name] = set()
                    backend_models[cls_name] = backend_models[cls_name] | backend_models[base]

    backend_models = {k: v for k, v in backend_models.items() if v}

    frontend_models: dict[str, set[str]] = {}
    if frontend_dir.exists():
        for dart_file in frontend_dir.rglob("*.dart"):
            for m_name, m_fields in extract_freezed_fields(dart_file).items():
                if m_name in frontend_models:
                    frontend_models[m_name] = frontend_models[m_name] | m_fields
                else:
                    frontend_models[m_name] = m_fields

    backend_by_lower: dict[str, str] = {name.lower(): name for name in backend_models}
    frontend_by_lower: dict[str, str] = {name.lower(): name for name in frontend_models}

    # Map backend models to corresponding frontend models using normalized and aliased names
    matched_pairs: list[tuple[str, str]] = []
    matched_frontend: set[str] = set()

    for b_name in sorted(backend_models.keys()):
        b_lower = b_name.lower()

        # If a more specific response DTO exists for this model (e.g. WorkflowResponseDTO > Workflow), prioritize it
        if b_lower in PREFERRED_BACKEND_ALIASES and PREFERRED_BACKEND_ALIASES[b_lower] in backend_by_lower:
            continue

        target_f_lower = EXPLICIT_MODEL_ALIASES[b_lower] if b_lower in EXPLICIT_MODEL_ALIASES else b_lower
        if target_f_lower in frontend_by_lower:
            f_name = frontend_by_lower[target_f_lower]
            if f_name not in matched_frontend:
                matched_pairs.append((b_name, f_name))
                matched_frontend.add(f_name)

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
                            mismatch_reason=f"Field '{fld}' present in Python Pydantic model '{b_name}' but missing in Dart Freezed model '{f_name}'.",
                            remediation=f"Add @JsonKey(name: '{fld}') or camelCase field '{snake_to_camel(fld)}' to Dart Freezed class '{f_name}'.",
                        )
                    )
            if missing_in_back:
                diffs.append(f"Missing in Backend: {sorted(missing_in_back)}")
                for fld in sorted(missing_in_back):
                    mismatches.append(
                        DtoFieldMismatchDTO(
                            model_name=b_name,
                            field_name=fld,
                            mismatch_reason=f"Field '{fld}' present in Dart Freezed model '{f_name}' but missing in Python Pydantic model '{b_name}'.",
                            remediation=f"Add field '{fld}: <Type>' to Python Pydantic class '{b_name}'.",
                        )
                    )
            summary_messages.append(f"[{b_name} <-> {f_name}] " + "; ".join(diffs))

    is_success = len(mismatches) == 0
    return DtoParityReportDTO(
        is_success=is_success,
        shared_models_count=len(matched_pairs),
        mismatches=mismatches,
        summary_messages=summary_messages,
    )


def audit_parity(backend_dir: Path, frontend_dir: Path) -> tuple[bool, list[str]]:
    """Compare matching DTO models across backend and frontend directories.

    Returns:
        tuple[bool, list[str]] indicating (is_success, mismatch_summary_messages).
    """
    report = audit_parity_report(backend_dir, frontend_dir)
    return report.is_success, report.summary_messages


def main() -> None:
    """CLI Entrypoint for DTO parity auditing."""
    parser = argparse.ArgumentParser(description="Audit field-level parity between Backend and Frontend DTOs.")
    parser.add_argument("--backend-dir", default="backend_v2/models", help="Backend models directory")
    parser.add_argument("--frontend-dir", default="client_app_v2/lib", help="Frontend lib directory")
    parser.add_argument("--fail-on-mismatch", action="store_true", default=True, help="Exit with 1 on mismatch")
    args = parser.parse_args()

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
