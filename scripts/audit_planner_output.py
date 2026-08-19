"""Audit Planner Output.

A deterministic neuro-symbolic check to ensure the Tier 1 Planner
has not abstracted away specific line boundaries, target files, or KI context via lossy compression.
"""

import argparse
import re
import sys
from pathlib import Path

# Add scripts directory to sys.path if not present
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from _ast_boundary_utils import (  # noqa: E402
    extract_deprecated_symbols,
    extract_target_files,
    parse_line_bound,
    validate_ast_line_bound,
)


def main() -> None:
    """Execute the Tier 1 Planner output audit.

    Validates that generated plan files preserve line boundaries, target files,
    AST nodes, KI references, and rule blocks present in the original Epic.
    """
    parser = argparse.ArgumentParser(description="Audit Tier 1 Planner Output for lossy compression.")
    parser.add_argument("--epic", required=True, type=str, help="Path to the source Epic .md file")
    parser.add_argument("--plan-dir", required=True, type=str, help="Directory containing the generated plans")
    args = parser.parse_args()

    epic_path = Path(args.epic)
    plan_dir = Path(args.plan_dir)

    if not epic_path.exists():
        print(f"ERROR: Epic file not found: {epic_path}")
        sys.exit(1)

    if not plan_dir.exists() or not plan_dir.is_dir():
        print(f"ERROR: Plan directory not found or not a directory: {plan_dir}")
        sys.exit(1)

    bound_pattern = re.compile(r"#L\d+-L?\d+")
    py_bound_pattern = re.compile(r"([a-zA-Z0-9_./\\-]+\.py)#(L\d+-L?\d+)")

    with open(epic_path, encoding="utf-8") as f:
        epic_content = f.read()

    epic_bounds = set(bound_pattern.findall(epic_content))
    print(f"AUDIT: Found {len(epic_bounds)} specific line bounds in Epic:")
    for b in sorted(epic_bounds):
        print(f"   - {b}")

    plan_files = sorted(plan_dir.glob("*.md"))
    if not plan_files:
        print(f"ERROR: No .md plan files found in {plan_dir}")
        sys.exit(1)

    combined_plan_content = ""
    for pf in plan_files:
        with open(pf, encoding="utf-8") as f:
            combined_plan_content += f.read() + "\n"

    plan_bounds = set(bound_pattern.findall(combined_plan_content))
    missing_bounds = epic_bounds - plan_bounds
    failed = False

    print("-" * 50)

    # 1. TEST LINE BOUNDARY PRESERVATION
    if missing_bounds:
        print("FAILED: The Planner abstracted away the following line bounds:")
        for b in sorted(missing_bounds):
            print(f"  - {b}")
        failed = True
    else:
        if epic_bounds:
            print("SUCCESS: All line bounds from the Epic were preserved verbatim in the plans!")
        else:
            print("SKIP: No line bounds found in Epic to verify.")

    # 2. TEST TARGET FILE COVERAGE
    epic_targets = extract_target_files(epic_content)
    if epic_targets:
        missing_targets = []
        for action, target_path, _ in epic_targets:
            # Check if target file path is referenced in plan content
            clean_name = Path(target_path).name
            if target_path not in combined_plan_content and clean_name not in combined_plan_content:
                missing_targets.append((action, target_path))
        if missing_targets:
            print("FAILED: Plans omit the following target files stated in the Epic:")
            for act, tpath in missing_targets:
                print(f"  - [{act}] {tpath}")
            failed = True
        else:
            print(f"SUCCESS: All {len(epic_targets)} target files from the Epic are referenced in the plans.")

    # 3. TEST AST BOUNDARY VALIDATION FOR PYTHON FILES
    py_bound_matches = py_bound_pattern.findall(epic_content) + py_bound_pattern.findall(combined_plan_content)
    invalid_ast_bounds = []
    for file_str, bound_str in py_bound_matches:
        py_file_path = Path(file_str)
        if py_file_path.exists():
            bounds = parse_line_bound(bound_str)
            if bounds:
                start, end = bounds
                if not validate_ast_line_bound(py_file_path, start, end):
                    invalid_ast_bounds.append((file_str, bound_str))
    if invalid_ast_bounds:
        print("FAILED: The following Python line bounds do not match valid AST nodes in physical codebase:")
        for fstr, bstr in invalid_ast_bounds:
            print(f"  - {fstr}#{bstr}")
        failed = True
    elif py_bound_matches:
        print(f"SUCCESS: All {len(py_bound_matches)} Python AST line bounds verified against physical codebase.")

    # 4. TEST MANDATORY XML BLOCKS
    required_tags = ["<anti_targets>", "<dod_checklist>", "<validation_gate>"]
    for tag in required_tags:
        if tag not in combined_plan_content:
            print(f"FAILED: Mandatory XML block {tag} is missing from the generated plans!")
            failed = True
        else:
            print(f"SUCCESS: Mandatory XML block {tag} found.")

    # 5. TEST KI COVERAGE (Epic -> Plan inheritance)
    ki_pattern = re.compile(r"(?:knowledge[/\\][^/\\]+[/\\]artifacts[/\\]\S+\.md|ki_[a-zA-Z0-9_-]+\.md)")
    epic_kis = set(ki_pattern.findall(epic_content))
    plan_kis = set(ki_pattern.findall(combined_plan_content))
    if epic_kis:
        missing_kis = epic_kis - plan_kis
        if missing_kis:
            print("FAILED: Plans are missing the following KIs from the Epic's <required_knowledge_items>:")
            for ki in sorted(missing_kis):
                print(f"  - {ki}")
            failed = True
        else:
            print(f"SUCCESS: All {len(epic_kis)} KI references from the Epic are present in the plans.")
    else:
        print("SKIP: No KI artifact references found in Epic.")

    # 6. TEST RULE COVERAGE (Plan -> required_context_rules completeness)
    core_rule_pattern = re.compile(r"00-antigravity-core\.md")
    domain_rule_pattern = re.compile(r"0[1-5][-_][a-z_-]+\.md")

    plans_with_rules_block = 0
    plans_missing_core = []
    plans_missing_domain = []

    for pf in plan_files:
        with open(pf, encoding="utf-8") as f:
            plan_text = f.read()

        if "<required_context_rules>" not in plan_text:
            continue

        plans_with_rules_block += 1
        if not core_rule_pattern.search(plan_text):
            plans_missing_core.append(pf.name)
        if not domain_rule_pattern.search(plan_text):
            plans_missing_domain.append(pf.name)

    if plans_with_rules_block == 0:
        print("SKIP: No plans contain a <required_context_rules> block.")
    else:
        if plans_missing_core:
            print("FAILED: Plans missing core rule (00-antigravity-core.md) in <required_context_rules>:")
            for name in plans_missing_core:
                print(f"  - {name}")
            failed = True
        else:
            print(f"SUCCESS: All {plans_with_rules_block} plans reference 00-antigravity-core.md.")

        if plans_missing_domain:
            print("FAILED: Plans with zero domain-specific rules in <required_context_rules>:")
            for name in plans_missing_domain:
                print(f"  - {name}")
            failed = True
        else:
            print(f"SUCCESS: All {plans_with_rules_block} plans reference at least one domain rule.")

    # 7. TEST DEMOLISH TAG PROPAGATION (Epic -> Plans)
    epic_demolish = extract_deprecated_symbols(epic_content)
    plan_demolish = extract_deprecated_symbols(combined_plan_content)
    if epic_demolish:
        if not plan_demolish:
            print("FAILED: Epic contains <demolish> tags but no <demolish> tags found in plans!")
            failed = True
        else:
            missing_demolish = epic_demolish - plan_demolish
            if missing_demolish:
                print("FAILED: Plans are missing the following demolish symbols from the Epic:")
                for sym in sorted(missing_demolish):
                    print(f"  - {sym}")
                failed = True
            else:
                print(f"SUCCESS: All {len(epic_demolish)} demolish symbols from Epic are propagated into plans.")
    else:
        print("SKIP: No <demolish> tags found in Epic.")

    print("-" * 50)
    if failed:
        print("AUDIT FAILED: The Planner dropped critical details. Tune tier1-planner.md rules further.")
        sys.exit(1)
    else:
        print("AUDIT PASSED: The Planner obeyed the strict boundary and layout rules perfectly!")
        sys.exit(0)


if __name__ == "__main__":
    main()
