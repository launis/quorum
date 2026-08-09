"""Audit Planner Output.

A deterministic neuro-symbolic check to ensure the Tier 1 Planner
has not abstracted away specific line boundaries via lossy compression.
"""

import argparse
import re
import sys
from pathlib import Path


def main() -> None:
    """Execute the Tier 1 Planner output audit.

    Validates that the generated plan files preserve all fine-grained
    line boundaries (#Lxx-Lyy) present in the original Epic document.
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

    # Regex to match line boundaries like #L830-L841
    bound_pattern = re.compile(r"#L\d+-L\d+")

    with open(epic_path, encoding="utf-8") as f:
        epic_content = f.read()

    epic_bounds = set(bound_pattern.findall(epic_content))

    print(f"AUDIT: Found {len(epic_bounds)} specific line bounds in Epic:")
    for b in epic_bounds:
        print(f"   - {b}")

    plan_files = list(plan_dir.glob("*.md"))
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
        for b in missing_bounds:
            print(f"  - {b}")
        failed = True
    else:
        if epic_bounds:
            print("SUCCESS: All line bounds from the Epic were preserved verbatim in the plans!")
        else:
            print("SKIP: No line bounds found in Epic to verify.")

    # 2. TEST MANDATORY XML BLOCKS
    required_tags = ["<anti_targets>", "<dod_checklist>", "<validation_gate>"]
    for tag in required_tags:
        if tag not in combined_plan_content:
            print(f"FAILED: Mandatory XML block {tag} is missing from the generated plans!")
            failed = True
        else:
            print(f"SUCCESS: Mandatory XML block {tag} found.")

    # 3. TEST KI COVERAGE (Epic → Plan inheritance)
    ki_pattern = re.compile(r"knowledge[/\\][^/\\]+[/\\]artifacts[/\\]\S+\.md")
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
        print("SKIP: No KI artifact references found in Epic (consider adding <required_knowledge_items>).")

    # 4. TEST RULE COVERAGE (Plan → required_context_rules completeness)
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
        print("SKIP: No plans contain a <required_context_rules> block (non-self-hydrating plans).")
    else:
        if plans_missing_core:
            print("FAILED: Plans missing core rule (00-antigravity-core.md) in <required_context_rules>:")
            for name in plans_missing_core:
                print(f"  - {name}")
            failed = True
        else:
            print(
                f"SUCCESS: All {plans_with_rules_block} plans with "
                "<required_context_rules> reference 00-antigravity-core.md."
            )

        if plans_missing_domain:
            print("FAILED: Plans with zero domain-specific rules in <required_context_rules>:")
            for name in plans_missing_domain:
                print(f"  - {name}")
            failed = True
        else:
            print(
                f"SUCCESS: All {plans_with_rules_block} plans with "
                "<required_context_rules> reference at least one domain rule."
            )

    print("-" * 50)
    if failed:
        print("AUDIT FAILED: The Planner dropped critical details. Tune tier1-planner.md rules further.")
        sys.exit(1)
    else:
        print("AUDIT PASSED: The Planner obeyed the strict boundary and layout rules perfectly!")
        sys.exit(0)


if __name__ == "__main__":
    main()
