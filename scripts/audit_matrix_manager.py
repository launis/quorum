"""Neuro-Symbolic Audit Matrix Manager.

Enforces deterministic rule validation for AI Hardening loops.
Dynamically injects rule requirements into the validation JSON to
prevent AI attention drift, and enforces anti-laziness heuristics.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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

    rules = []
    for match in matches:
        rule_id = match.group(1)
        block_content = match.group(2)

        banned_match = re.search(r"<banned_pattern>(.*?)</banned_pattern>", block_content, re.DOTALL)
        mandatory_match = re.search(r"<mandatory_pattern>(.*?)</mandatory_pattern>", block_content, re.DOTALL)

        banned = banned_match.group(1).strip() if banned_match else "N/A"
        mandatory = mandatory_match.group(1).strip() if mandatory_match else "N/A"

        rules.append({"rule_id": rule_id, "banned_pattern": banned, "mandatory_pattern": mandatory})

    return rules


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate a blank JSON matrix with injected context for a specific target file.

    Args:
        args: CLI arguments containing target domain type and target file.
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
    unique_rules = []
    for r in all_rules:
        if r["rule_id"] not in seen:
            seen.add(r["rule_id"])
            unique_rules.append(r)

    normalized_target = Path(args.target).as_posix() if hasattr(args, "target") and args.target else ""
    if not normalized_target:
        print("ERROR: Mandatory argument '--target' cannot be empty.")
        sys.exit(1)

    matrix_rules: list[dict[str, str]] = []
    matrix: dict[str, Any] = {
        "target_file": normalized_target,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rules": matrix_rules,
    }

    for rule in unique_rules:
        matrix_rules.append(
            {
                "rule_id": rule["rule_id"],
                "banned_pattern": rule["banned_pattern"],
                "mandatory_pattern": rule["mandatory_pattern"],
                "status": "PENDING",
                "justification": "",
            }
        )

    out_dir = repo_root / "tmp"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "audit_matrix.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2)

    print(
        f"[SUCCESS] Generated strict JSON audit matrix at {out_path} for target '{normalized_target}' with {len(unique_rules)} rules."
    )
    print("AI MUST fill out this JSON explicitly. 'status' must be PASS, FAIL, or NA.")


def check_anti_laziness(justification: str) -> str | None:
    """Verify justification length and complexity to prevent AI laziness.

    Args:
        justification: The provided justification text.

    Returns:
        Error message if failed, else None.
    """
    if len(justification) < 25:
        return f"Justification too short ({len(justification)} chars). Must be >= 25 chars."

    words = [w for w in justification.split() if len(w) > 1]
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

    # Find file path patterns ending in .py or .dart
    file_pattern = r"(?:[\w./\\]+[/\\])?([a-zA-Z0-9_]+\.(?:py|dart))"
    found_files = re.findall(file_pattern, justification)

    # Allowed common files mentioned as systemic dependencies or rules
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


def cmd_verify(args: argparse.Namespace) -> None:
    """Verify a filled JSON matrix for strict compliance, target lock, and anti-laziness.

    Args:
        args: CLI arguments.
    """
    matrix_path = Path(args.file)
    if not matrix_path.exists():
        print(f"Error: Matrix file {matrix_path} not found.")
        sys.exit(1)

    try:
        with open(matrix_path, encoding="utf-8") as f:
            matrix = json.load(f)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    matrix_target = matrix.get("target_file", "").strip()
    if not matrix_target:
        print("ERROR: Validation Failed: 'target_file' is empty in matrix JSON.")
        sys.exit(1)

    normalized_matrix_target = Path(matrix_target).as_posix()
    normalized_cli_target = Path(args.target).as_posix() if hasattr(args, "target") and args.target else ""

    if not normalized_cli_target:
        print("ERROR: Validation Failed: Mandatory argument '--target' was not provided.")
        sys.exit(1)

    if normalized_matrix_target != normalized_cli_target:
        print(
            f"ERROR: Target mismatch. Matrix was generated for '{normalized_matrix_target}', "
            f"but verification requested for '{normalized_cli_target}'."
        )
        sys.exit(1)

    rules = matrix.get("rules", [])
    if not rules:
        print("ERROR: Validation Failed: No rules found in matrix.")
        sys.exit(1)

    errors: list[str] = []
    valid_statuses = {"PASS", "FAIL", "NA"}
    seen_pass_justifications: set[str] = set()
    seen_na_justifications: dict[str, int] = {}

    for idx, rule in enumerate(rules):
        rule_id = rule.get("rule_id", f"unknown_rule_{idx}")
        status = rule.get("status", "").upper()
        justification = rule.get("justification", "").strip()

        if status == "PENDING":
            errors.append(f"Rule '{rule_id}': Status is still PENDING. AI must audit this rule.")
            continue

        if status not in valid_statuses:
            errors.append(f"Rule '{rule_id}' has invalid status '{status}'. Must be one of: {valid_statuses}")

        lazy_error = check_anti_laziness(justification)
        if lazy_error:
            errors.append(f"Rule '{rule_id}': {lazy_error}")

        conflict_error = check_conflicting_file_references(justification, normalized_matrix_target)
        if conflict_error:
            errors.append(f"Rule '{rule_id}': {conflict_error}")

        if status == "PASS":
            if justification in seen_pass_justifications:
                errors.append(
                    f"Rule '{rule_id}': Duplicate PASS justification detected. "
                    f"Each PASS rule must cite unique substantive code evidence."
                )
            else:
                seen_pass_justifications.add(justification)
        elif status == "NA":
            seen_na_justifications[justification] = seen_na_justifications.get(justification, 0) + 1
            if seen_na_justifications[justification] > 40:
                errors.append(f"Rule '{rule_id}': NA justification repeated more than 40 times.")

    if errors:
        print(f"ERROR: Validation Failed with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        print("\nThe AI MUST correct the JSON file before proceeding to fixes.")
        sys.exit(1)

    print(f"[SUCCESS] All {len(rules)} rules have been strictly validated for target '{normalized_matrix_target}'.")
    sys.exit(0)


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Neuro-Symbolic Audit Matrix Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Generate a blank JSON matrix")
    gen_parser.add_argument("--type", required=True, choices=["backend", "frontend"], help="Target domain rules")
    gen_parser.add_argument("--target", required=True, help="Target file path being audited")

    ver_parser = subparsers.add_parser("verify", help="Verify a filled JSON matrix")
    ver_parser.add_argument("--file", default="tmp/audit_matrix.json", help="Path to the filled JSON matrix")
    ver_parser.add_argument("--target", required=True, help="Expected target file path")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "verify":
        cmd_verify(args)


if __name__ == "__main__":
    main()
