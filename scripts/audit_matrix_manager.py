"""Neuro-Symbolic Audit Matrix Manager.

Enforces deterministic rule validation for AI Hardening loops with strict Pydantic V2 schemas.
Dynamically injects rule requirements and automated AST scan evidence into the validation JSON to
prevent AI attention drift, and enforces anti-laziness heuristics.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from scripts._ast_guardrails import GuardrailViolation, scan_files_for_guardrails

# Force UTF-8 encoding for stdout on Windows without reflection
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass

# Rule ID to AST Guardrail Code mapping for automated evidence binding
RULE_ID_AST_MAP: dict[str, set[str]] = {
    "the_duct_tape_ban": {"QGR002", "QGR003"},
    "the_zero_compromise_pledge": {"QGR001", "QGR007"},
    "zero_service_layer_fallbacks": {"QGR002"},
    "strict_pydantic_v2_rust": {"QGR001", "QGR007"},
    "system_concurrency_ssot": {"QGR006", "QGR008"},
    "python_314_modern_syntax": {"QGR006"},
    "pydantic_discriminated_union_mandate": {"QGR004", "QGR005"},
}

# Placeholder texts rejected under anti-rubber-stamping heuristics
PLACEHOLDER_JUSTIFICATIONS: set[str] = {
    "n/a",
    "na",
    "ok",
    "verified",
    "passed",
    "none",
    "test",
    "done",
    "pass",
    "fail",
    "",
}


class EvidenceType(StrEnum):
    """Evidence classification for matrix rule evaluations."""

    STATIC_AST = "STATIC_AST"
    SEMANTIC_DIFF = "SEMANTIC_DIFF"
    MANUAL_AUDIT = "MANUAL_AUDIT"


class AuditRuleStatus(StrEnum):
    """Evaluation status for an audit rule."""

    PASS = "PASS"
    FAIL = "FAIL"
    NA = "NA"
    PENDING = "PENDING"


class AuditRuleEntryDTO(BaseModel):
    """Pydantic V2 DTO representing an individual rule evaluation entry in an audit matrix."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_id: Annotated[str, Field(description="Unique rule identifier e.g. the_duct_tape_ban")]
    banned_pattern: Annotated[str, Field(description="Banned architectural pattern")]
    mandatory_pattern: Annotated[str, Field(description="Mandatory architectural pattern")]
    status: Annotated[AuditRuleStatus, Field(description="Evaluation status")]
    evidence_type: Annotated[EvidenceType, Field(default=EvidenceType.MANUAL_AUDIT, description="Evidence type")]
    ast_violations: Annotated[
        list[GuardrailViolation], Field(default_factory=list, description="Static AST violations if any")
    ]
    justification: Annotated[str, Field(default="", description="Substantive human or agent justification")]


class AuditMatrixDTO(BaseModel):
    """Pydantic V2 DTO representing the complete audit matrix for a target file."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    target_file: Annotated[str, Field(description="Normalized target file path relative to repo root")]
    generated_at: Annotated[str, Field(description="ISO timestamp of matrix generation")]
    rules: Annotated[list[AuditRuleEntryDTO], Field(description="List of rule evaluation entries")]


def get_repo_root() -> Path:
    """Return the absolute path to the repository root."""
    return Path(__file__).resolve().parent.parent


def extract_rule_blocks(file_path: Path) -> list[dict[str, str]]:
    """Parse a Markdown file and extract rule blocks dynamically.

    Args:
        file_path: Path to the Markdown rules file.

    Returns:
        List of dictionaries containing rule logic.
    """
    if not file_path.exists():
        print(f"Error: Rules file {file_path} not found.")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    pattern = r'<rule_block\s+id=["\']([^"\']+)["\']>(.*?)</rule_block>'
    matches = re.finditer(pattern, content, re.DOTALL)

    rules: list[dict[str, str]] = []
    for match in matches:
        rule_id = match.group(1)
        block_content = match.group(2)

        banned_match = re.search(r"<banned_pattern>(.*?)</banned_pattern>", block_content, re.DOTALL)
        mandatory_match = re.search(r"<mandatory_pattern>(.*?)</mandatory_pattern>", block_content, re.DOTALL)

        banned = banned_match.group(1).strip() if banned_match else "N/A"
        mandatory = mandatory_match.group(1).strip() if mandatory_match else "N/A"

        rules.append({"rule_id": rule_id, "banned_pattern": banned, "mandatory_pattern": mandatory})

    return rules


def cmd_generate(args: argparse.Namespace, exit_on_completion: bool = True) -> AuditMatrixDTO:
    """Generate a blank JSON matrix with injected context for a specific target file.

    Args:
        args: CLI arguments containing target domain type, target file, and flags.
        exit_on_completion: Whether to call sys.exit at completion.

    Returns:
        Constructed AuditMatrixDTO object.
    """
    repo_root = get_repo_root()
    core_rules = repo_root / ".agents" / "rules" / "00-antigravity-core.md"

    if args.type == "backend":
        domain_rules = repo_root / ".agents" / "rules" / "01-python-backend.md"
    elif args.type == "frontend":
        domain_rules = repo_root / ".agents" / "rules" / "02_flutter_desktop.md"
    else:
        print("Invalid type. Must be 'backend' or 'frontend'.")
        sys.exit(1)

    all_rules = extract_rule_blocks(core_rules) + extract_rule_blocks(domain_rules)

    seen: set[str] = set()
    unique_rules: list[dict[str, str]] = []
    for r in all_rules:
        if r["rule_id"] not in seen:
            seen.add(r["rule_id"])
            unique_rules.append(r)

    args_dict = vars(args)
    raw_target = str(args_dict["target"]) if "target" in args_dict and args_dict["target"] else ""
    normalized_target = Path(raw_target).as_posix() if raw_target else ""
    if not normalized_target:
        print("ERROR: Mandatory argument '--target' cannot be empty.")
        sys.exit(1)

    # Perform automated AST scan if requested or if target is a Python file
    ast_scan_active = bool(args_dict["ast_scan"]) if "ast_scan" in args_dict else False
    target_violations: list[GuardrailViolation] = []
    full_target_path = repo_root / normalized_target
    if ast_scan_active and full_target_path.exists() and full_target_path.suffix == ".py":
        target_violations, _ = scan_files_for_guardrails([full_target_path])

    rule_entries: list[AuditRuleEntryDTO] = []
    for rule in unique_rules:
        rule_id = rule["rule_id"]
        matching_qgr_codes = RULE_ID_AST_MAP[rule_id] if rule_id in RULE_ID_AST_MAP else set()

        rule_ast_violations = [v for v in target_violations if v.rule_code in matching_qgr_codes]
        evidence_type = EvidenceType.STATIC_AST if rule_ast_violations else EvidenceType.MANUAL_AUDIT

        rule_entries.append(
            AuditRuleEntryDTO(
                rule_id=rule_id,
                banned_pattern=rule["banned_pattern"],
                mandatory_pattern=rule["mandatory_pattern"],
                status=AuditRuleStatus.PENDING,
                evidence_type=evidence_type,
                ast_violations=rule_ast_violations,
                justification="",
            )
        )

    matrix_dto = AuditMatrixDTO(
        target_file=normalized_target,
        generated_at=datetime.now(UTC).isoformat(),
        rules=rule_entries,
    )

    out_file_str = (
        str(args_dict["output"]) if "output" in args_dict and args_dict["output"] else "tmp/audit_matrix.json"
    )
    out_path = repo_root / out_file_str if not Path(out_file_str).is_absolute() else Path(out_file_str)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_path.write_text(matrix_dto.model_dump_json(indent=2), encoding="utf-8")

    print(
        f"[SUCCESS] Generated strict JSON audit matrix at {out_path.as_posix()} for target '{normalized_target}' with {len(unique_rules)} rules."
    )
    print("AI MUST fill out this JSON explicitly. 'status' must be PASS, FAIL, or NA.")

    if exit_on_completion:
        sys.exit(0)

    return matrix_dto


def check_anti_laziness(justification: str) -> str | None:
    """Verify justification length, word count, and anti-rubber-stamping heuristics.

    Args:
        justification: The provided justification text.

    Returns:
        Error message if failed, else None.
    """
    cleaned = justification.strip()
    if cleaned.lower() in PLACEHOLDER_JUSTIFICATIONS:
        return f"Placeholder or empty justification '{cleaned}' rejected under anti-rubber-stamping heuristic."

    if len(cleaned) < 25:
        return f"Justification too short ({len(cleaned)} chars). Must be >= 25 chars."

    words = [w for w in cleaned.split() if len(w) > 1]
    if len(words) < 4:
        return f"Justification lacks detail ({len(words)} words). Must have >= 4 distinct words."

    return None


def check_conflicting_file_references(justification: str, target_file: str) -> str | None:
    """Check whether justification cites code files conflicting with the target file.

    Args:
        justification: The justification text.
        target_file: The normalized target file path.

    Returns:
        Error message if a conflicting file reference is found, else None.
    """
    target_posix = Path(target_file).as_posix()
    target_stem = Path(target_file).name

    file_pattern = r"(?:[\w./\\]+[/\\])?([a-zA-Z0-9_]+\.(?:py|dart))"
    found_files = re.findall(file_pattern, justification)

    allowed_mentions = {
        target_stem,
        "settings.py",
        "enums.py",
        "conftest.py",
        "audit_matrix_manager.py",
        "backend_audit_loop.py",
        "flutter_audit_loop.py",
    }

    for file_name in found_files:
        if file_name not in allowed_mentions and not target_posix.endswith(file_name):
            return f"Conflicting file reference '{file_name}' detected in justification. Justification must anchor to target '{target_stem}'."

    return None


def cmd_verify(args: argparse.Namespace, exit_on_completion: bool = True) -> list[str]:
    """Verify a filled JSON matrix for strict compliance, target lock, AST violations, and anti-laziness.

    Args:
        args: CLI arguments.
        exit_on_completion: Whether to call sys.exit at completion.

    Returns:
        List of validation error strings.
    """
    matrix_path = Path(args.file)
    if not matrix_path.exists():
        print(f"Error: Matrix file {matrix_path} not found.")
        if exit_on_completion:
            sys.exit(1)
        return [f"Matrix file {matrix_path} not found."]

    try:
        raw_content = matrix_path.read_text(encoding="utf-8")
        matrix_dto = AuditMatrixDTO.model_validate_json(raw_content)
    except (ValueError, OSError) as e:
        print(f"Error parsing or validating JSON against AuditMatrixDTO: {e}")
        if exit_on_completion:
            sys.exit(1)
        return [f"Error parsing or validating JSON against AuditMatrixDTO: {e}"]

    matrix_target = matrix_dto.target_file.strip()
    if not matrix_target:
        print("ERROR: Validation Failed: 'target_file' is empty in matrix JSON.")
        if exit_on_completion:
            sys.exit(1)
        return ["'target_file' is empty in matrix JSON."]

    normalized_matrix_target = Path(matrix_target).as_posix()
    args_dict = vars(args)
    raw_cli_target = str(args_dict["target"]) if "target" in args_dict and args_dict["target"] else ""
    normalized_cli_target = Path(raw_cli_target).as_posix() if raw_cli_target else ""

    if not normalized_cli_target:
        print("ERROR: Validation Failed: Mandatory argument '--target' was not provided.")
        if exit_on_completion:
            sys.exit(1)
        return ["Mandatory argument '--target' was not provided."]

    if normalized_matrix_target != normalized_cli_target:
        msg = (
            f"ERROR: Target mismatch. Matrix was generated for '{normalized_matrix_target}', "
            f"but verification requested for '{normalized_cli_target}'."
        )
        print(msg)
        if exit_on_completion:
            sys.exit(1)
        return [msg]

    rules = matrix_dto.rules
    if not rules:
        print("ERROR: Validation Failed: No rules found in matrix.")
        if exit_on_completion:
            sys.exit(1)
        return ["No rules found in matrix."]

    errors: list[str] = []
    seen_pass_justifications: set[str] = set()
    seen_na_justifications: dict[str, int] = {}

    for rule in rules:
        rule_id = rule.rule_id
        status = rule.status
        justification = rule.justification.strip()

        if status == AuditRuleStatus.PENDING:
            errors.append(f"Rule '{rule_id}': Status is still PENDING. AI must audit this rule.")
            continue

        # If unsuppressed AST violations are present, status cannot be PASS
        unsuppressed_violations = [v for v in rule.ast_violations if not v.is_suppressed]
        if status == AuditRuleStatus.PASS and unsuppressed_violations:
            errors.append(
                f"Rule '{rule_id}': Marked as PASS but contains {len(unsuppressed_violations)} un-suppressed AST violations "
                f"({unsuppressed_violations[0].rule_code}: {unsuppressed_violations[0].message})."
            )

        lazy_error = check_anti_laziness(justification)
        if lazy_error:
            errors.append(f"Rule '{rule_id}': {lazy_error}")

        conflict_error = check_conflicting_file_references(justification, normalized_matrix_target)
        if conflict_error:
            errors.append(f"Rule '{rule_id}': {conflict_error}")

        if status == AuditRuleStatus.PASS:
            if justification in seen_pass_justifications:
                errors.append(
                    f"Rule '{rule_id}': Duplicate PASS justification detected. "
                    f"Each PASS rule must cite unique substantive code evidence."
                )
            else:
                seen_pass_justifications.add(justification)
        elif status == AuditRuleStatus.NA:
            current_count = seen_na_justifications[justification] + 1 if justification in seen_na_justifications else 1
            seen_na_justifications[justification] = current_count
            if current_count > 40:
                errors.append(f"Rule '{rule_id}': NA justification repeated more than 40 times.")

    if errors:
        print(f"ERROR: Validation Failed with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        print("\nThe AI MUST correct the JSON file before proceeding to fixes.")
        if exit_on_completion:
            sys.exit(1)
        return errors

    print(f"[SUCCESS] All {len(rules)} rules have been strictly validated for target '{normalized_matrix_target}'.")
    if exit_on_completion:
        sys.exit(0)
    return []


def main(args_list: list[str] | None = None) -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Neuro-Symbolic Audit Matrix Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Generate a blank JSON matrix")
    gen_parser.add_argument("--type", required=True, choices=["backend", "frontend"], help="Target domain rules")
    gen_parser.add_argument("--target", required=True, help="Target file path being audited")
    gen_parser.add_argument("--ast-scan", action="store_true", help="Perform automated static AST scan on target")
    gen_parser.add_argument("--output", default="tmp/audit_matrix.json", help="Destination file path")

    ver_parser = subparsers.add_parser("verify", help="Verify a filled JSON matrix")
    ver_parser.add_argument("--file", default="tmp/audit_matrix.json", help="Path to the filled JSON matrix")
    ver_parser.add_argument("--target", required=True, help="Expected target file path")

    args = parser.parse_args(args_list)

    if args.command == "generate":
        cmd_generate(args, exit_on_completion=True)
    elif args.command == "verify":
        cmd_verify(args, exit_on_completion=True)


if __name__ == "__main__":
    main()
