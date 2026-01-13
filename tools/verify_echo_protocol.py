"""Verify Echo Protocol Compliance."""

import re
import sys
from pathlib import Path

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

ROUTER_DIR = Path("c:/src/quorum/backend/api")

def verify_echo_protocol(file_path):
    """Scan file for Echo Protocol violations."""
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    errors = []

    # 1. Check Echo Protocol (Logger before Raise)
    # Pattern: raise HTTPException(..., detail="ERROR_CODE")
    # or detail=error_code

    raise_pattern = re.compile(r"raise HTTPException\s*\(")
    log_pattern = re.compile(r"logger\.(error|warning|exception|critical)\s*\(")

    for i, line in enumerate(lines):
        if raise_pattern.search(line):
            # Scan backwards for logger
            found_logger = False
            for j in range(i - 1, max(-1, i - 20), -1):
                prev_line = lines[j].strip()
                if not prev_line or prev_line.startswith("#"):
                    continue
                if log_pattern.search(prev_line):
                    found_logger = True
                    break
                if (
                    prev_line.endswith(":") or
                    prev_line.startswith("if ") or
                    prev_line.startswith("else") or
                    prev_line.startswith("try") or
                    prev_line.startswith("except")
                ):
                    # Boundary hit, likely no logger in this block
                    break

            if not found_logger:
                # Exclude re-raises that might match?
                # If "raise HTTPException" is alone in a block, it needs a log.
                # Check if it has 'detail'
                if "detail=" in line or "detail" in line:
                    errors.append(f"Line {i+1}: raise HTTPException without preceding logger call.")

    return errors

def main():
    """Run the verification."""
    print(f"Scanning {ROUTER_DIR} for Echo Protocol compliance...")

    files = list(ROUTER_DIR.glob("*_router.py"))
    total_errors = 0

    with open("tools/verification_result.txt", "w", encoding="utf-8") as out:
        for file_path in files:
            file_errors = verify_echo_protocol(file_path)
            if file_errors:
                out.write(f"FAIL: {file_path.name}\n")
                for err in file_errors:
                    out.write(f"  - {err}\n")
                total_errors += len(file_errors)
            else:
                out.write(f"PASS: {file_path.name}\n")

    if total_errors > 0:
        print(f"\n{RED}Total Errors: {total_errors}{RESET}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}All routers compliant!{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
