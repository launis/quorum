"""Neuro-Symbolic Audit Matrix Manager.

Enforces deterministic rule validation for AI Hardening loops.
Dynamically injects rule requirements into the validation JSON to
prevent AI attention drift, and enforces anti-laziness heuristics.
"""

import argparse
import json
import re
import sys
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
    """Generate a blank JSON matrix with injected context.

    Args:
        args: CLI arguments.
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

    matrix_rules: list[dict[str, str]] = []
    matrix: dict[str, Any] = {"target_file": "", "rules": matrix_rules}

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

    print(f"[SUCCESS] Generated strict JSON audit matrix at {out_path} with {len(unique_rules)} rules.")
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


def cmd_verify(args: argparse.Namespace) -> None:
    """Verify a filled JSON matrix for strict compliance and anti-laziness.

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

    if not matrix.get("target_file"):
        print("ERROR: Validation Failed: 'target_file' is empty.")
        sys.exit(1)

    rules = matrix.get("rules", [])
    if not rules:
        print("ERROR: Validation Failed: No rules found in matrix.")
        sys.exit(1)

    errors = []
    valid_statuses = {"PASS", "FAIL", "NA"}
    seen_justifications = set()
    duplicate_count = 0

    for idx, rule in enumerate(rules):
        rule_id = rule.get("rule_id", f"unknown_rule_{idx}")
        status = rule.get("status", "").upper()
        justification = rule.get("justification", "").strip()

        if status not in valid_statuses:
            errors.append(f"Rule '{rule_id}' has invalid status '{status}'. Must be one of: {valid_statuses}")

        lazy_error = check_anti_laziness(justification)
        if lazy_error:
            errors.append(f"Rule '{rule_id}': {lazy_error}")

        # Anti-Copy-Paste logic
        if justification in seen_justifications:
            duplicate_count += 1
            if duplicate_count > 3:  # Allow max 3 identical justifications
                errors.append(f"Rule '{rule_id}': Duplicate justification detected. AI is copy-pasting answers.")
        else:
            seen_justifications.add(justification)

    if errors:
        print(f"ERROR: Validation Failed with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        print("\nThe AI MUST correct the JSON file before proceeding to fixes.")
        sys.exit(1)

    print(f"[SUCCESS] All {len(rules)} rules have been strictly validated for {matrix['target_file']}.")
    sys.exit(0)


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Neuro-Symbolic Audit Matrix Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Generate a blank JSON matrix")
    gen_parser.add_argument("--type", required=True, choices=["backend", "frontend"], help="Target domain rules")

    ver_parser = subparsers.add_parser("verify", help="Verify a filled JSON matrix")
    ver_parser.add_argument("--file", required=True, help="Path to the filled JSON matrix")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "verify":
        cmd_verify(args)


if __name__ == "__main__":
    main()
