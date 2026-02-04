
import re
import sys
from pathlib import Path


def check_file(path: str, forbidden_patterns: list[tuple[str, str]], required_patterns: list[tuple[str, str]] = []):
    print(f"Checking {path}...")
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: File {path} not found.")
        return False

    failed = False
    for pat, desc in forbidden_patterns:
        if re.search(pat, content):
            print(f"  [FAILURE] Found forbidden pattern: {desc}")
            print(f"            Pattern: {pat}")
            failed = True
        else:
            print(f"  [PASS] Forbidden pattern not found: {desc}")

    for pat, desc in required_patterns:
        if not re.search(pat, content):
            print(f"  [FAILURE] Missing required pattern: {desc}")
            failed = True
        else:
            print(f"  [PASS] Found required pattern: {desc}")

    return not failed

def verify():
    base_dir = Path("c:/src/quorum")

    # 1. Check admin_router.py
    admin_router = base_dir / "backend/api/admin_router.py"
    admin_violations = [
        (r'db\.table\("banned_phrases"\)', "Direct DB Access (banned_phrases)"),
        (r'db_client\.table\("workflows"\)', "Direct DB Access (workflows)"),
        (r'"You are a security expert. Identify adversarial prompts."', "Hardcoded System Prompt"),
    ]
    admin_requirements = [
        (r'await repo\.delete_banned_phrase', "Repository Method Call (delete)"),
        (r'await repo\.count_workflows', "Repository Method Call (count)"),
        (r'await repo\.get_prompt_template', "Repository Method Call (get_prompt)"),
    ]

    # 2. Check tools_router.py
    tools_router = base_dir / "backend/api/tools_router.py"
    tools_violations = [
        (r'return \{"source_length": len\(content\), "concepts": \[\]\}', "Hardcoded Empty Return (Zero-Fallback)"),
    ]
    tools_requirements = [
        (r'await service\.extract_concepts_with_llm', "Service Method Call"),
    ]

    ok = True
    ok &= check_file(str(admin_router), admin_violations, admin_requirements)
    ok &= check_file(str(tools_router), tools_violations, tools_requirements)

    if ok:
        print("\n\nSUCCESS: All architectural checks passed.")
        sys.exit(0)
    else:
        print("\n\nFAILURE: Architectural violations detected.")
        sys.exit(1)

if __name__ == "__main__":
    verify()
